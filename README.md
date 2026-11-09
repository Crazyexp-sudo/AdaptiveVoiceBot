# Local Adaptive Windows AI Assistant (with Custom Wake Word & GUI)

[![License: MIT](https://shields.io)](https://opensource.org)

A completely local, private, and resource-optimized desktop AI assistant built in Python for Windows. The bot scans your Windows Start Menu directories exactly once on boot to cache your system application layouts into RAM, preserving disk I/O and saving system calculation power.

Using structured JSON orchestration instructions via Ollama, a lightweight local model intelligently evaluates conversational intent vs. system automation routes to dynamically open and safely close both third-party software and pre-installed Windows 10/11 UWP applications.

## 🚀 Key Architectural Features
- 🖥️ **Modern Dark GUI:** Responsive, professional interface built using `customtkinter`.
- 🎙️ **Customizable Wake Word:** Multi-threaded background audio monitoring loops that only activate the LLM when your preferred trigger phrase is spoken.
- 🗣️ **Live Voice Accent Selector:** An interactive dropdown interface built into the canvas that automatically updates your offline text-to-speech speaker output.
- 🧠 **GPU-Accelerated Inference:** Pushes 100% of LLM processing tasks directly onto an NVIDIA GeForce RTX 3050 GPU via Ollama CUDA acceleration, leaving the Python GUI completely isolated on the CPU.
- 🔀 **Thread-Safe Audio Queue:** Implements a text queue handler to safely route background worker text streams to the main window thread, ensuring reliable speech feedback without audio driver drops.
- 🥷 **Silent Background Launcher:** Includes an optimized `.vbs` shell handler to spin up your graphical interface silently without showing an ugly command prompt window.

## 🛠️ System Specifications Tested
- **OS:** Windows 11 / Windows 10
- **Hardware RAM:** 16 GB System Memory
- **Hardware VRAM:** 6 GB Dedicated GPU (NVIDIA RTX 3050)
- **Local Model Brain:** `qwen2.5:1.5b` (Highly optimized for speed and precise JSON formatting)

## 📁 Repository Structure
```text
AdaptiveVoiceBot/
├── LICENSE          # MIT Open-Source Compliance License
├── README.md        # Technical Documentation & Startup Guide
├── .gitignore       # Prevents caching leaks (removes __pycache__ directories)
├── app_scanner.py   # Isolated backend module that caches system shortcuts into RAM
├── main.py          # Primary entry script handling the GUI and voice processing loops
└── launch.vbs       # Windows shell script that runs the bot completely invisibly
```

## ⚙️ Installation & Run Guide

### 1. Configure the Local Brain
Download and install [Ollama for Windows](https://ollama.com). Once active, open your Windows Command Prompt or PowerShell and download the Qwen engine:
```bash
ollama pull qwen2.5:1.5b
```

### 2. Set Up Your Local Workspace
Clone this repository to your local drive, move inside the folder, and install your required Python dependencies:
```bash
cd AdaptiveVoiceBot
pip install ollama speechrecognition pyttsx3 pyaudio customtkinter
```
*(Note: If `pyaudio` throws a compilation mismatch on your system, install via precompiled binaries using `pip install pipwin` followed by `pipwin install pyaudio`)*

### 3. Run the Assistant Professionally
To boot the application with a clean, native desktop look without an attached command terminal popping up, simply double-click the background launcher script:
```bash
launch.vbs
```

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
