# IOT-AIML: Gesture-Controlled IoT Integration

A lightweight, robust, and real-time hand-tracking system that maps finger gestures to IoT API endpoints. Built using MediaPipe Tasks API (Landmarker) and OpenCV.

---

## 🚀 Overview

**IOT-AIML** recognizes finger counts (0-5) and triggers actions based on the configured mode. It features a **1-second debounce** (holding timer) to ensure gestures are intentional before locking them in.

- **Counting Mode**: Visual feedback only. Shows "LOCKED" on screen. No API calls.
- **IOT Mode**: Active triggering. Fires `GET` requests and shows "TRIGGERED" on screen.

---

## 🛠️ Quick Start

1. **Setup**: Run `.\setup.bat` (Windows) to create the environment.
2. **Launch**: Run `.\run.bat` or `python main.py`.
3. **Switch Configs**: Click the **"CONFIG"** button in the top-right corner of the video window to load a new JSON file!

---

## ⚙️ Configuration File Examples

Copy the example below that fits your current needs and save it as `config.json`.

### Example 1: Testing / Counting Mode
*Use this for initial setup and testing detection accuracy without firing any network requests.*

```json
{
  "mode": "Counting",
  "iot_endpoints": {
    "1": "Test Mode - No API",
    "2": "Test Mode - No API",
    "3": "Test Mode - No API",
    "4": "Test Mode - No API",
    "5": "Test Mode - No API"
  }
}
```

### Example 2: Active IOT Mode
*Use this to control smart devices. Ensure your URLs are reachable from your local network.*

```json
{
  "mode": "IOT",
  "iot_endpoints": {
    "1": "http://192.168.1.100/light/on",
    "2": "http://192.168.1.100/fan/on",
    "3": "http://192.168.1.100/monitor/toggle",
    "4": "http://192.168.1.100/ac/set/24",
    "5": "http://192.168.1.100/all/off"
  }
}
```

---

## ✨ System Features

- **MediaPipe Tasks**: Uses orientation-independent straightness ratios for extremely reliable finger counting.
- **Visual Feedback**: On-screen "LOCKED" and "TRIGGERED" messages provide instant confirmation.
- **HUD Interface**: Real-time display of detection mode, current finger count, and FPS.
- **Hot-Reloading**: Change the behavior of the application at runtime by selecting a new configuration file.

---

## 📁 Project Structure

```text
IOT-AIML/
├── core/                   # Logic for config loading and IoT triggering
├── detector/               # Advanced geometry-based hand detection
├── ui/                     # HUD and visual feedback rendering
├── models/                 # Pre-trained MediaPipe task models
├── main.py                 # Application entry point
├── config.json             # Active configuration file
├── setup.bat / run.bat     # Windows startup and execution scripts
└── requirements.txt        # Python dependency list
```

---

## 📄 Core File Reference

| File | Sub-system | Description |
| :--- | :--- | :--- |
| `main.py` | Orchestration | Coordinates camera feed, detection, and rendering. |
| `core/iot_manager.py` | Logic | Handles the 1-second hold timer and API dispatching. |
| `detector/hand_detector.py` | AI/ML | Calculates finger extension using robust ratio math. |
| `ui/renderer.py` | UI | Renders the premium HUD and trigger animations. |

---

## 📝 License
Educational and development project for AI/ML and IoT integration.
