import os
import uuid
import shutil
import grpc
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from storage import init_db, save_message, get_recent
from grpc_services import video_analysis_pb2, video_analysis_pb2_grpc

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
init_db()

app = FastAPI(title="Video Analyzer API", description="Local AI Video Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _stub(port: int):
    ch = grpc.insecure_channel(f"localhost:{port}")
    return ch, video_analysis_pb2_grpc.VideoAnalysisStub(ch)


# Upload
@app.post("/upload", tags=["Video"])
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 allowed.")

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(UPLOADS_DIR, unique_name)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    save_message("user", f"Uploaded video: {unique_name}")
    save_message("system", f"Saved to path: {path}")
    return {"file_name": unique_name, "saved_path": path}


# Transcribe
@app.post("/transcribe", tags=["Agents"])
def transcribe_video(file_name: str):
    path = os.path.join(UPLOADS_DIR, file_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found.")

    save_message("user", f"Transcribing {file_name}")
    try:
        ch, stub = _stub(50051)
        resp = stub.TranscribeVideo(video_analysis_pb2.VideoRequest(file_path=path))
        ch.close()
        transcript = getattr(resp, "transcript", str(resp))
        save_message("assistant", transcript[:500] + "...")
        return {"transcript": transcript}
    except Exception as e:
        save_message("system", f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Detect objects
@app.post("/detect", tags=["Agents"], summary="Detect Video")
def analyze_video(file_name: str):
    path = os.path.join(UPLOADS_DIR, file_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found.")

    save_message("user", f"Detecting {file_name}")
    try:
        ch, stub = _stub(50052)
        resp = stub.AnalyzeVideo(video_analysis_pb2.VideoRequest(file_path=path))
        ch.close()
        objs = list(getattr(resp, "objects", []))
        summary = f"Objects detected: {objs}" if objs else "No objects detected."
        save_message("assistant", summary)
        return {"objects": objs}
    except Exception as e:
        save_message("system", f"Vision agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Generate reports
@app.post("/generate", tags=["Agents"])
def generate_report(file_name: str, report_type: str = "pdf"):
    path = os.path.join(UPLOADS_DIR, file_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found.")
    if report_type not in ("pdf", "pptx"):
        raise HTTPException(status_code=400, detail="Only PDF or PPTX allowed.")

    save_message("user", f"Generating {report_type.upper()} for {file_name}")
    try:
        ch, stub = _stub(50053)
        req = video_analysis_pb2.ReportRequest(file_path=path, report_type=report_type)
        resp = stub.GenerateReport(req)
        ch.close()
        report_path = getattr(resp, "report_path", "")
        save_message("assistant", f"Report generated: {report_path}")
        return {"report_path": report_path}
    except Exception as e:
        save_message("system", f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get history
@app.get("/history", tags=["History"])
def get_history(limit: int = 100):
    return {"messages": get_recent(limit)}


# Clear history
@app.delete("/history", tags=["History"])
def clear_history():
    from storage import clear_all_history
    count = clear_all_history()
    save_message("system", f"🧹 Cleared {count} messages.")
    return {"message": f"Deleted {count} messages."}

# Download reports
@app.get("/download/{filename}", tags=["Functions"])
def download_file(filename: str):
    from pathlib import Path
    path = Path(__file__).resolve().parent / "artifacts" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    save_message("system", f"Downloaded: {filename}")
    return FileResponse(path=path, filename=filename)


# Clarify (route to MCP gRPC)
@app.post("/clarify", tags=["Functions"])
def clarify_query(query: str):
    import grpc
    from grpc_services import video_analysis_pb2, video_analysis_pb2_grpc
    from storage import save_message

    q = query.lower().strip()
    save_message("user", query)

    try:
        # Connect to MCP Server (Intent Matcher)
        channel = grpc.insecure_channel("localhost:50054")
        stub = video_analysis_pb2_grpc.VideoAnalysisStub(channel)

        # Send the query to the MCP Server with timeout (5 seconds)
        resp = stub.ClarifyQuery(video_analysis_pb2.ClarificationRequest(query=q), timeout=5)
        channel.close()

        # DEBUG: log the raw response object and attributes so we can see exactly what arrived
        print("[API Clarify] raw resp:", repr(resp))
        # Access attributes explicitly (proto fields are normal attributes)
        selected_option = getattr(resp, "selected_option", None)
        message = getattr(resp, "message", None)
        options_proto = getattr(resp, "options", None)

        # Normalize options into a Python list
        try:
            options = list(options_proto) if options_proto is not None else []
        except Exception:
            options = []

        # Only fallback if message is None or consists only of whitespace
        if message is None or (isinstance(message, str) and message.strip() == ""):
            fallback_msg = "Did you want me to transcribe, detect objects, or generate a report?"
            print("[API Clarify] Empty/blank message received from MCP — using fallback.")
            message = fallback_msg

        # If selected_option is None or empty, fallback to "clarify"
        if not selected_option:
            print("[API Clarify] No selected_option returned from MCP — defaulting to 'clarify'.")
            selected_option = "clarify"

        # Debug log
        print(f"[API Clarify] decision={selected_option!r}, message={message!r}, options={options}")

        # Save to chat history (so frontend can see it later)
        save_message("assistant", message)

        return {
            "decision": selected_option,
            "message": message,
            "options": options
        }

    except Exception as e:
        print(f"[API Clarify Error] {e}")
        save_message("assistant", "Did you want me to transcribe, detect objects, or generate a report?")
        return {
            "decision": "clarify",
            "message": "Did you want me to transcribe, detect objects, or generate a report?",
            "options": ["Transcribe", "Detect Objects", "Generate Report"]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
