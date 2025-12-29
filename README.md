# 🌊 Tolkyn

**Tolkyn** is a real-time, audio-responsive 3D generative art system written in **Processing (P3D)**. It visualizes thousands of drifting particles (“nodes”), glowing connections (“edges”), and melody-driven bursts, creating a living sculpture of motion, light, and sound.

---
<p align="center">
  <a href="https://www.youtube.com/watch?v=pi5H7Lr1hQ8">
    <img src="https://github.com/user-attachments/assets/fbe33cbb-38bb-4373-ab6a-a90b9ddcbae2" width="100%" />
  </a>
</p>



## ✨ Features

### 🌐 3D Node Universe
- **3,000 nodes** arranged randomly on a 3D sphere  
- Each node has:
  - A 3D position (`PVector`)
  - A fade-out cycle
  - A randomized HSB color
  - A size, opacity, and musical note assignment
- Nodes continuously fade out and regenerate in new random positions

### 🔥 Edge Burst System
Every few seconds:
- 1 to 5 **focus nodes** are selected  
- For each focus node, the system finds the **farthest nodes** using `NodeDistance`  
- Lines (“edges”) are drawn between them  
- Edges:
  - Glow with blended node colors
  - Fade over time
  - Have randomized thickness & brightness

### 🎼 Procedural Melody Engine

When a new focus cycle begins, a musical system plays a note from one of four phrases:
```
Phrase 1: B3 C4 F4 E4
Phrase 2: B3 C4 E4 D4
Phrase 3: B3 C4 F4
Phrase 4: F4 D4 E4
```

The system:
- Cycles through phrases  
- Advances through notes one-by-one  
- Plays short tones using `SinOsc`  
- Automatically loops forever  

### Gyroscope + Camera Fusion Rotation
Tolkyn can rotate the entire 3D universe using physical motion from an external gyroscope (L3G4200D for this instance) combined with webcam-based motion detection.
#### ⭐ What This Feature Does
  - Reads real-time X/Y/Z angular velocity from Arduino
  - Integrates gyro values to compute orientation
  - Tracks motion from the webcam (motion centroid)
  - Smoothly fuses them together with adjustable weights:
```
fusedAngle = camWeight * cameraAngle + gyroWeight * gyroAngle
```
#### 🎮 Why This Matters
- The scene rotates when you move:
- Move your hand → camera detects motion → rotation
- Rotate your device → gyro rotates the scene
- Both systems support each other:
  - The camera provides stability
  - The gyro provides responsiveness and physicality

#### ⚙️ Fusion Details
- Gyro data integrated with time (dt) to compute angles
- Scene rotation uses:
  - rotateX()
  - rotateY()
  - rotateZ()
- Gyro Z-axis is also applied for subtle drifting spin
- Camera motion centroid changes the target orientation
- Easing keeps rotation smooth and non-jittery
This adds a layer of embodied, physical interaction—ideal for installations, performances, or handheld devices.

### 🎥 Motion-Driven Interaction (Optional)

The webcam feed is analyzed frame-to-frame:
- Motion centroid controls **scene rotation**  

A mirrored live camera feed is rendered behind the scene at extreme depth (z = -10000), intended to be hidden from plain-sight.

### 🔊 Audio Reactivity (FFT and Beat-Driven)

- Input from the microphone is processed with a 512-band FFT:
  - The loudest frequency band is extracted each frame  
  - Large amplitudes trigger more edges  
  - Quiet audio produces sparse, minimal visuals
- A beat detection system identifies rhythmic onsets (kicks, pulses, percussive events).
- Each detected beat triggers structural and visual responses in the node system.

### 🌈 Visual Aesthetics
- Additive blending for glow effects  
- HSB color system  
- Soft rotation drift  
- Procedural node respawn with new colors, sizes, and positions  
- Timed reveal: nodes appear one-by-one using a configurable interval

---

## 🧠 Code Architecture Overview

### Classes

#### **Node**
- Stores:
  - 3D position (x, y, z)
  - Assigned note index
  - Frequency for optional musical use  
- Created with a random spherical distribution

#### **Edge**
- Stores:
  - Start and end points
  - Alpha (fade)
  - Brightness
  - Thickness
- Draws a fading connection between two nodes

#### **NodeDistance**
- Used during sorting to find the farthest nodes from a focus node

---

## 🛠 Installation & Requirements

1. Install **Processing 4.x**
2. Install libraries:
   - Sound  
   - Video  
3. Enable:
   - Microphone access  
   - Webcam access  

### Running

1. Open the sketch in Processing  
2. Press **Run**  
3. Allow camera & microphone permissions  

---

## ▶️ Controls & Behavior

### 🎥 Motion Input
- Move hands → rotates the 3D node sphere

### 🎮 Gyroscope Input
- Tilt or rotate your device → rotates the 3D universe
- Z-axis rotation produces slow drifting spin
- Camera + gyro blended for stability and responsiveness

### 🔊 Audio Input
- Louder sounds → more edges  
- Quiet → sparse visuals

### 🎼 Melody
- Each burst cycle triggers the next note  
- Phrases loop automatically  

---

## 📂 Code Structure
```
Tolqyn/
└── Tolqyn.ino  # Arduino code

Tolqyn.pde # Main sketch containing:
    ├── Node class
    ├── Edge class
    ├── NodeDistance class
    ├── FFT + camera processing
    ├── Gyroscope fusion system
    ├── Motion tracking
    ├── Melody engine
    └── Node/edge rendering

README.md
```
---

## 📜 Copyright

© 2025. **Myint Myat Aung** and **Prithwis Das**

---

## 💬 About the Name

**Tolqyn / Tolkyn**  
Kazakh for **wave**.  
Represents:
- Waves of sound  
- Waves of motion  
- Waves of color  
- Waves of dynamic emergence in the node universe  

The name symbolizes the breathing, flowing nature of the artwork.

---

## 🌟 Future Improvements
- Shader-based GPU acceleration
- IMU-based gesture recognition
- Multi-oscillator sound engine
- OSC output for live performance tools
- Node clustering: galaxies, tendrils, starfields

---

