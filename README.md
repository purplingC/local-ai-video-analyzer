# Local AI Video Analyzer
## Project Overview
A **fully offline AI desktop application** designed to analyze short videos (~1 minute) in terms of **transcribing speech**, **detecting visual objects** and **generating summarized reports (PDF or PPTX)** through an interactive chat-style interface built with **React** and **Tauri**. 

Please note that pre-download models such as the **SentenceTransformer**, **Hugging Face DETR** and **T5-small** models are required to ensure all AI operations can run with no internet connection.



## System Architecture Overview
+----------------------+
|   React + Tauri UI   |
|  (User Interaction)  |
+----------+-----------+
           |
           ▼
+----------------------+
| FastAPI + gRPC Layer |
| (Request Routing)    |
+----------+-----------+
           |
           ▼
+----------------------+
|     MCP Server       |
| (Intent Detection)   |
+----------+-----------+
     ┌──────────────┬──────────────┬──────────────┐
     ▼              ▼              ▼
+-----------+  +-----------+  +-----------------+
|Transcribe |  |   Vision  |  |   Generation    |
|(Whisper)  |  | (DETR)    |  | (T5 + OpenVINO) |
+-----------+  +-----------+  +-----------------+
           │
           ▼
+----------------------+
|  SQLite + localStorage  |
| (Output & Chat History) |
+----------------------+



The **React + Tauri** frontend provides a chat-style interface that connects to the **FastAPI** backend via **gRPC**. The backend routes user queries to the **MCP** Server, which interprets intent using **SentenceTransformer** embeddings and confidence scoring. 

Depending on the query, tasks are handled by specialized local AI agents:
- Transcription Agent –> speech-to-text conversion using **Faster-Whisper**
- Vision Agent –> object detection using **Hugging Face DETR**
- Generation Agent –> summarization and report creation using **T5-small optimized with OpenVINO**

All outputs and chat history are stored locally using **SQLite** and **localStorage**


## Technical Highlights
| Component | Technology / Framework |
| ---------- | ---------------------- |
| **Frontend** | React + Tauri |
| **Backend** | FastAPI + gRPC |
| **MCP Server** | SentenceTransformer (all-MiniLM-L6-v2) |
| **Transcription Agent** | Faster-Whisper |
| **Vision Agent** | Hugging Face DETR |
| **Generation Agent** | T5-small (OpenVINO-optimized) |
| **Storage Layer** | SQLite + localStorage |
| **API Layer** | FastAPI REST API + Swagger UI |



## Quick Start  
### Pre-Downloaded Models (Required for Offline Run)
Due to GitHub file size limitations, the **SentenceTransformer**, **Hugging Face DETR** and **T5-small** models are provided separately.

**Download here:**  
https://drive.google.com/file/d/1rN1t8E1ZpD1q0bdEI8GhM-3pnYD_8kuG/view?usp=sharing 

**After downloading:** 
1. Place the `model_files.zip` file in the project root.
2. Extract it into `backend/models/` folder
- Run this in project root -> powershell -Command "Expand-Archive -Path 'model_files.zip' -DestinationPath 'backend/models' -Force"
4. The `backend/models/` folder should look like this:
    
backend/
├── models/
│   ├── model_files/           
│   │   ├── detr-resnet-50/      
│   │   ├── intent_embed/               
│   │   ├── t5_small/          
│   │   └── .placeholder   # ignore duplicate
│   └── .placeholder       # ignore duplicate


---


### Setup Backend  
Set up the backend environment, install dependencies.
Please note that you have Python and Node installed.
- cd backend
- python -m venv venv (if not exists)
- .\venv\Scripts\activate 
- pip install -r requirements.txt

--- 

### Run Backend
Start all agents, MCP and backend, 5 separate terminals are opened.
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

---

### Run Frontend
Launch the app interface.
- npm run tauri dev

---

## Example Input Files
Sample videos are provided in the `/sample_data/` folder.
- sample_meeting.mp4
- sample_pitch.mp4 

---


### How to Use
1. Launch the app.  
2. Select any `.mp4` file from the `/sample_data/` folder.
3. Then, click **“Upload”**.
4. Interact with the assistant by querying or clicking the buttons below the chat interface.

## Sample Queries
- Transcribe the video
- Detect objects in the video
- Generate a PDF report
- Generate reports 

## Generated Outputs Stored Location
- Outputs from transcription agents are stored under the `backend/uploads/` folder.
- Outputs from vision agents are stored under the `backend/uploads/` folder.
- Outputs from generation agents are stored under the `backend/artifacts/` folder.
- All system behaviour and user-assistant interaction history are stored in `backend/data/chat_history.db`.
- Logs can be found in each separate terminals when running backend.



## Human-in-the-loop Logic
Example: When user queries "Generate report", the system will ask user which reports format. 
User can reply pdf, pptx or both.


