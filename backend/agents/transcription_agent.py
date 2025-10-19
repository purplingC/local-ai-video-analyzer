from concurrent import futures
import grpc
import os
from pathlib import Path
from grpc_services import video_analysis_pb2, video_analysis_pb2_grpc
from model.openvino_model import extract_audio_to_wav

# Import faster-whisper for ASR
try:
    from faster_whisper import WhisperModel  # type: ignore
    _HAS_ASR = True
except Exception:
    _HAS_ASR = False
    WhisperModel = None


UPLOADS_DIR = Path(__file__).resolve().parents[1] / "uploads"
ASR_MODEL_SIZE = "tiny"  # smallest model


class TranscriptionServicer(video_analysis_pb2_grpc.VideoAnalysisServicer):
    def TranscribeVideo(self, request, context):
        video_path = request.file_path
        try:
            # Extract audio from the uploaded video
            wav_path = extract_audio_to_wav(video_path)

            # Run local speech-to-text if ASR is available
            if _HAS_ASR:
                model = WhisperModel(ASR_MODEL_SIZE, device="cpu")
                segments, info = model.transcribe(wav_path, language="en") # Force English
                transcript = " ".join([seg.text for seg in segments])
            else:
                # fallback if no ASR installed
                transcript = (
                    f"(No local ASR installed) Audio saved at {wav_path}. "
                    f"To enable speech-to-text, install faster-whisper and rerun."
                )
                
            # Save transcript to .txt for later report generation
            txt_path = os.path.splitext(wav_path)[0] + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            return video_analysis_pb2.TextResponse(transcript=transcript)
        except Exception as e:
            return video_analysis_pb2.TextResponse(transcript=f"Error: {str(e)}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    video_analysis_pb2_grpc.add_VideoAnalysisServicer_to_server(TranscriptionServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Transcription Agent running on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
