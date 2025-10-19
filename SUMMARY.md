# What Works?
- Analyzes short `.mp4` videos (English only)
- Transcription (speech-to-text via Transcription Agent)
- Object recognition (Vision Agent using DETR)
- Summarized report generation in PDF and PPTX (Generation Agent)
- Human-in-the-loop query clarification (MCP Server)
- Persistent offline chat history (SQLite + localStorage)

# What Doesn't Work?
- Graph/text detection and captioning not included (Vision Agent handles objects detection only)

# Encountered Challenges
- OpenVINO model installation failure
    -> Solution: switched to Hugging Face Transformers model (Zero-Shot Object Detection) for vision tasks.
- Rust linker missing during Tauri build 
    -> Solution: Required installation of Visual Studio Build Tools (MSVC toolchain)
- Build failed due to JSX syntax parsing issue when using .js files.
    -> Solution: adjusting React/Vite configuration or renaming to .jsx.
- Packaging caused crashes / memory errors (PyInstaller) 
    -> Solution: Skipped PyInstaller packaging due to laptop limitation
- IntentMatcher, DETR model and T5-Small model setup for offline mode
    -> Solution: Pre-downloaded all and saved into `backend/models/intent_embed/`to ensure complete offline operation.
    
# Potential Improvements (If No Technological Constraints)
- Cross-platform packaging and deployment 
- Multi-language transcription and translation support
- Automatic keyframe extraction with highlighted detections

# What Could Be Achieved With More Time or Hardware
- Smarter query understanding across agents
- Graph and text caption recognition in Vision Agent
- Elaborate more detailed technical documentation 
- Research and checked whether accuracy evaluation is required
