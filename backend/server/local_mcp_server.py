from concurrent import futures
import re
import grpc
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # 👈 ADD THIS

from model.intent_matcher import IntentMatcher
from grpc_services import video_analysis_pb2, video_analysis_pb2_grpc


intent_matcher = IntentMatcher()


class MCPServicer(video_analysis_pb2_grpc.VideoAnalysisServicer):
    last_intent = None

    def ClarifyQuery(self, request, context):
        query = request.query.lower().strip()
        print(f"[MCP] Incoming query: {query}")

        # Detect multiple actions
        actions_present = []
        if re.search(r"\b(transcribe|subtitle|speech|audio)\b", query):
            actions_present.append("transcribe")
        if re.search(r"\b(detect|identify|recognize|object|analyz)\b", query):
            actions_present.append("detect")
        if re.search(r"\b(generate|report|summary|create|make|build|output)\b", query):
            actions_present.append("generate")
        if len(actions_present) >= 2:
            print(f"[MCP] Multi-action detected → {actions_present}")
            return video_analysis_pb2.ClarificationResponse(
                selected_option="clarify",
                message="I noticed you mentioned more than one action. Please specify just one — Transcribe, Detect Objects, or Generate a Report.",
                options=["Transcribe", "Detect Objects", "Generate Report"]
            )

        # Direct format
        if re.search(r"\b(pdf|pdf report)\b", query):
            return video_analysis_pb2.ClarificationResponse(
                selected_option="generate_pdf",
                message="Generating PDF report..."
            )
        if re.search(r"\b(ppt|pptx|powerpoint|slides)\b", query):
            return video_analysis_pb2.ClarificationResponse(
                selected_option="generate_pptx",
                message="Generating PowerPoint report..."
            )
        if re.search(r"\bboth\b", query):
            return video_analysis_pb2.ClarificationResponse(
                selected_option="generate_both",
                message="Generating both PDF and PowerPoint reports..."
            )

        # Run matcher
        intents = intent_matcher.predict_multiple(query)
        print(f"[MCP] Detected intents: {intents}")
        top_intent, confidence = intents[0] if intents else ("clarify", 0.0)

        # Boost repeated
        if self.last_intent == top_intent and confidence > 0.4:
            confidence = min(0.95, confidence + 0.15)
        self.last_intent = top_intent

        # FORCE generate branch before fallback 
        if top_intent == "generate":
            print(f"[MCP] Top intent: generate ({confidence:.3f}) → ask format")
            return video_analysis_pb2.ClarificationResponse(
                selected_option="ask_generate_format",
                message="Would you like the report in PDF or PowerPoint (PPTX) format?",
                options=["PDF", "PPTX", "Both"]
            )

        if top_intent == "transcribe" and confidence >= 0.5:
            print(f"[MCP] Top intent: transcribe ({confidence:.3f})")
            return video_analysis_pb2.ClarificationResponse(
                selected_option="transcribe",
                message="Transcribing the video now..."
            )

        if top_intent == "detect" and confidence >= 0.5:
            print(f"[MCP] Top intent: detect ({confidence:.3f})")
            return video_analysis_pb2.ClarificationResponse(
                selected_option="detect",
                message="Detecting objects in the video..."
            )

        # Fallback
        print(f"[MCP] Fallback clarify (top={top_intent}, conf={confidence:.3f})")
        return video_analysis_pb2.ClarificationResponse(
            selected_option="clarify",
            message="Did you want me to transcribe, detect objects, or generate a report?",
            options=["Transcribe", "Detect Objects", "Generate Report"]
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    video_analysis_pb2_grpc.add_VideoAnalysisServicer_to_server(MCPServicer(), server)
    server.add_insecure_port('[::]:50054')
    print("MCP Server running on port 50054 (Semantic Intent Matcher)")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
