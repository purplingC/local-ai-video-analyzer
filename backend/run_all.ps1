# Backend Launcher (PowerShell)
$backendPath = "C:\Users\Sam Yu Zhen\Documents\intel-genai-assessment\backend"
$venvActivate = "$backendPath\genaienv\Scripts\Activate.ps1"

# Agents
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$backendPath'; . '$venvActivate'; python -m agents.transcription_agent"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$backendPath'; . '$venvActivate'; python -m agents.vision_agent"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$backendPath'; . '$venvActivate'; python -m agents.generation_agent"

# Add MCP 
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$backendPath'; . '$venvActivate'; python -m server.local_mcp_server"

# FastAPI Backend
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$backendPath'; . '$venvActivate'; uvicorn main:app --reload --port 8000"

Write-Host "All agents, MCP intent matcher, and backend started!"
Write-Host "Open http://127.0.0.1:8000/docs to test Swagger UI."
