# 🖥️ mac-control.
> The high-fidelity interface between LLM agents and macOS.

`mac-control.` is a production-grade toolkit designed to give AI agents (like Gemini, Claude, or Friday) surgical control over the macOS operating system. It combines structural UI metadata (via AX-API) with visual perception (via Apple's Native Vision OCR) to create a robust, deep-stealth automation layer.

## 🚀 Features
- **AX-API Engine**: Extracts high-resolution accessibility trees from any running application.
- **Native Vision Engine**: Leverages on-device Apple Silicon OCR for real-time visual grounding.
- **Deep Stealth**: Mimics human-like interaction patterns to bypass automation detection.
- **CLI-First**: Designed for seamless integration with LLM tools and terminal workflows.

## 🛠️ Components
- `engine.py`: The unified Python orchestrator for metadata extraction.
- `core.scpt`: AppleScript wrappers for mouse and keyboard control.

## 📦 Installation
```bash
git clone https://github.com/opendisorder/mac-control.git
pip install pyobjc-framework-AppleScript pyobjc-framework-Vision pyobjc-framework-AppKit
```

## 🎯 Usage
```bash
# Get AX-API tree for the active app
python3 engine.py --mode ax

# Run OCR on the current screen
python3 engine.py --mode vision
```

## ⚖️ License
MIT. Part of the `opendisorder.` ecosystem.
