# 🧠 AI Gesture-Controlled Virtual Whiteboard

🚀 What if you could draw on your screen… without touching it?

This project is a **Computer Vision-based Virtual Whiteboard** that allows users to draw in real time using **hand gestures** captured via a webcam.

---

## ✨ Features

- ✋ Draw using index finger
- 🧽 Erase using 3-finger gesture
- 🎨 Dynamic color palette (choose any color)
- ⚡ Real-time hand tracking using MediaPipe
- 🎯 Smooth drawing with interpolation
- 💾 Save drawings as image (press `S`)
- 🧠 Fully touchless interaction (draw, erase, clear)

---

## 🛠️ Tech Stack

- Python
- OpenCV
- MediaPipe
- NumPy

---

## 🧠 How It Works

1. Webcam captures real-time video
2. MediaPipe detects 21 hand landmarks
3. Index finger tip is tracked for drawing
4. Gestures control drawing and erasing
5. Output is rendered on a virtual canvas

---

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-gesture-virtual-whiteboard.git
cd ai-gesture-virtual-whiteboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
