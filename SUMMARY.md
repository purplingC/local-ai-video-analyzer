# What Works?
- Analyzes short `.mp4` videos (English only)
- Extracts and transcribes audio (Transcription Agent)
- Identifies and recognizes objects (Vision Agent)
- Produce summarized reports in PDF and PPTX formats (Generation Agent)
- Integrated simple human-in-the-loop query clarification (MCP Server)
- Interprets user queries and logs intent confidence scores for decision routing (MCP Server)
- Keeps complete chat history locally, even after app restarts (SQLite + localStorage)
- Enables users to interact through a chat-style interface to perform all operations

# What Doesn't Work?
- Graph/text detection and captioning are not integrated (Vision Agent handles objects detection only)
- Multilingual transcription has not been tested so the system currently operates in English only (language="en")

# Encountered Challenges
- OpenVINO model installation failure
    -> Solution: switched to Hugging Face Transformers model (Zero-Shot Object Detection) for vision tasks
- Rust linker missing during Tauri build 
    -> Solution: Required installation of Visual Studio Build Tools (MSVC toolchain)
- JSX Parsing Errors During Build
    -> Solution: adjusting React/Vite configuration and renaming `.js` to .`jsx` files
- Packaging caused crashes / memory errors (PyInstaller) 
    -> Solution: Skipped PyInstaller packaging due to laptop limitation
- IntentMatcher, DETR model and T5-Small model setup for offline mode
    -> Solution: Pre-downloaded and stored all models in `backend/models/`to ensure full offline operation

# What Could Be Achieved With More Time or Hardware
- Smarter intent and query understanding between agents
- Extended Vision Agent capabilities (graph/text caption recognition)
- More comprehensive technical documentation
- Optimization for larger or longer video files
- Expanded testing and evaluation for accuracy and speed

# Potential Improvements
- Cross-platform packaging and deployment 
- Multi-language transcription and translation support
- Automatic keyframe extraction with highlighted detections
- Enhanced UI/UX for smoother user interaction and progress feedback
