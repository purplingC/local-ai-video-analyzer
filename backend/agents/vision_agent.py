from concurrent import futures
import grpc
import cv2
from pathlib import Path
from PIL import Image
from transformers import pipeline
from grpc_services import video_analysis_pb2, video_analysis_pb2_grpc

import warnings
warnings.filterwarnings("ignore", message=".*meta parameter.*")

# Initialize Hugging Face object detection model 
detector = pipeline("object-detection", model="models/detr-resnet-50")

UPLOADS_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

class VisionServicer(video_analysis_pb2_grpc.VideoAnalysisServicer):
    def AnalyzeVideo(self, request, context):
        video_path = request.file_path
        path = Path(video_path)

        if not path.exists():
            return video_analysis_pb2.AnalysisResponse(objects=["File not found"], graphs=[])

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return video_analysis_pb2.AnalysisResponse(objects=["Unable to open video"], graphs=[])

        frame_rate = int(cap.get(cv2.CAP_PROP_FPS)) or 15
        frame_interval = frame_rate * 2  # analyze every 2 secs

        detected_labels = set()
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Only process selected frames to save time
            if frame_idx % frame_interval == 0:
                # Convert OpenCV frame (BGR) to PIL (RGB)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)

                # Run detection
                results = detector(pil_image)

                # Collect unique, confident object labels
                for r in results:
                    if r["score"] >= 0.5:
                        detected_labels.add(r["label"])

            frame_idx += 1

        cap.release()

        # Prepare final summary
        if detected_labels:
            summary_text = "Objects detected:\n" + "\n".join(sorted(detected_labels))
        else:
            summary_text = "No objects detected."

        # Save vision results
        vision_txt_path = UPLOADS_DIR / f"{path.stem}.vision.txt"
        vision_txt_path.write_text(summary_text, encoding="utf-8")

        print(f"Vision summary saved: {vision_txt_path}")
        print(f"Detected objects:\n{summary_text}")

        # Return list of unique objects to API
        return video_analysis_pb2.AnalysisResponse(
            objects=list(sorted(detected_labels)), graphs=[]
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    video_analysis_pb2_grpc.add_VideoAnalysisServicer_to_server(VisionServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("Vision Agent running (DETR mode) on port 50052")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
