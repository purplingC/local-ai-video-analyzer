# Local AI Video Analyzer

---

## Project Overview
A **fully local AI desktop application** designed to analyze short video clips (~1 minute) entirely offline. The system allows users to **transcribe speech**, **detect visual objects** and **generate summarized reports (PDF or PPTX)** through a chat-style conversational interface (React and Tauri). 

All models are local, the only pre-download required is the SentenceTransformer intent matcher which, once cached, runs 100% offline

---

## Architecture Overview
The system follows a modular, multi-agent architecture that runs fully offline. The **React + Tauri** frontend provides a chat-style interface that connects to the **FastAPI** backend via **gRPC**. The backend routes user queries to the **MCP** Server, which interprets intent using **SentenceTransformer** embeddings and confidence scoring. 

Depending on the query, tasks are handled by specialized local AI agents:
- Transcription Agent –> speech-to-text conversion using **Faster-Whisper**
- Vision Agent –> object detection using **Hugging Face DETR**
- Generation Agent –> summarization and report creation using **T5-small optimized with OpenVINO**

All outputs and chat history are stored locally using **SQLite** and **localStorage**

---

## Quick Start  
### Setup Backend  
Set up the backend environment, install dependencies.
- cd backend
- python -m venv venv (if not exists)
- .\venv\Scripts\activate 
- pip install -r requirements.txt

Please note that you have Python and Node installed.

#### Run Backend
Start all agents + backend, 5 separate terminals are opened.
- .\run_all.ps1
- Open http://127.0.0.1:8000/docs to test Swagger UI.

Other Functions to be Noted (Backend - Swagger UI)
- GET /history – Retrieve recent chat history stored in SQLite.
- DELETE /history – Clear all stored chat messages and reset the local conversation log.

---

### Setup Frontend
Install dependencies.
- cd frontend
- npm install

#### Run Frontend
Launch the app interface.
- npm run tauri dev

---

## Example Input Files
Sample videos are provided in the `/sample_data/` folder.
- sample_meeting.mp4
- sample_pitch.mp4 

### How to Use
1. Launch the app.  
2. Select any `.mp4` file from the `sample_data` folder.
3. Then, click **“Upload”**.
4. Interact with the assistant by querying or clicking the buttons below the chat interface

---

## Sample Queries
Transcribe the video
Detect objects in the video
Generate a PDF report
Generate reports 

---

## Generated Outputs Stored Location
Outputs from transcription agents are stored under the `uploads` folder.
Outputs from vision agents are stored under the `uploads` folder.
Outputs from generation agents are stored under the `artifacts` folder.
All chat history are stored in chat_history.db.

---

## Human-in-the-loop Logic
Example: When user queries "Generate report", the system will ask user which reports format. 
User can reply pdf, pptx or both.

---

## Technical Highlights
- Fully offline AI inference (OpenVINO + Hugging Face pipelines)
- gRPC communication between all agents (Transcription, Vision, Generation + MCP)
- Intent classification using SentenceTransformer embeddings (semantic query understanding)
- Confidence-based routing with human-in-the-loop clarification (MCP Server + terminal logging)
- Offline summarization using T5-small model (optimized with OpenVINO)
- Persistent chat history stored locally (SQLite + localStorage)
- Cross-platform desktop app built with React + Tauri (lightweight and offline-capable)


**Last Updated:** October 20, 2025  
