# ⚽ FootballVerse AI
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![React](https://img.shields.io/badge/Frontend-React-blue?logo=react)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.x-yellow?logo=python)
**FootballVerse AI** is a next-generation, AI-driven football gaming ecosystem designed to test a user's physical reflexes, tactical intelligence, and historical knowledge of the beautiful game. 
Built with a modern React frontend and a powerful FastAPI backend, the platform features real-time computer vision, complex match simulation engines, and global leaderboards made by three football fanatics from Human Resources Department of BRAC University Computer Club. 

The contributors are respectively
- Mahir Dyan : https://github.com/Iamm3taphorical
- Dibyo Singho Barua Subrajit : https://github.com/whosubrajit
- Adittya Dey : https://github.com/Adittya202
  
---
## ✨ Core Features
- **Immersive UI/UX**: A sleek, dark-themed interface featuring dynamic stadium backgrounds, rain animations, and cinematic splash screens.
- **Computer Vision Integration**: Real-time webcam tracking using MediaPipe for physical, gesture-based gameplay.
- **Player Profiles & DNA**: Build a persistent "Football DNA" profile that tracks your playstyle, stats, and achievements across modes.
- **Global Leaderboards**: Independent competitive ladders tracking the top 100 players worldwide for each distinct game mode.
---
## 🎮 Game Modes
### 1. Player Arena (The Penalty Shootout)
- **Focus**: Reflexes & Computer Vision
- **Mechanics**: Step into a virtual penalty shootout! Using the device's webcam, the game tracks your hand movements in real-time. Aim a crosshair using your hand and perform gestures (e.g., closing your fist to charge power, opening it to shoot) to strike the ball past an AI goalkeeper.
- **Output**: Receive a detailed "Player Report" that analyzes your reaction times, accuracy, and compares your playstyle to legendary footballers (your "DNA Match").
### 2. Tactical Coach (The Match Simulator)
- **Focus**: Strategy & Resource Management
- **Mechanics**: Assume the role of a manager during a full 90-minute football match broken down into 15-minute segments. Use a drag-and-drop tactical pitch visualizer to switch between 15 formations and assign roles. The AI generates dynamic scenarios (e.g., "The opponent is pressing high") that require immediate tactical adjustments.
- **Output**: Earn "Tactical Points" and prestigious titles like "Elite Tactician" or "Sunday League Coach".
### 3. Fan Trivia (The Ultimate Gauntlet)
- **Focus**: Football Knowledge & History
- **Mechanics**: A high-stakes trivia game where you have exactly 5 minutes to clear four categories: Guess The Player, Guess The Coach, Guess The Stadium, and Guess The Iconic Match. The AI provides up to 10 progressive clues.
- **Output**: Ranked on the Fan Leaderboard with titles ranging from "Sunday Fan" to "FootballVerse Immortal".
---
## 🛠 Technical Stack
### Frontend
- **Framework**: React, TypeScript, Vite
- **Styling**: Vanilla CSS (Tailored for dynamic and aesthetic animations)
### Backend
- **Framework**: Python, FastAPI
- **Database**: SQLite, SQLAlchemy
- **Core AI Engines**: 
  - MediaPipe (Computer Vision Tracking)
  - Custom Python Algorithms (Match Simulation & Tactical Generators)
---
## 🚀 Getting Started
Follow these steps to set up the project locally.
### 1. Clone the repository
```bash
git clone https://github.com/Iamm3taphorical/bucc_FootballVerseAI.git
cd bucc_FootballVerseAI
```
### 2. Backend Setup
Set up your Python virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt # or install fastapi uvicorn mediapipe sqlalchemy
```
Start the FastAPI server:
```bash
cd backend
uvicorn main:app --reload
```
### 3. Frontend Setup
Open a new terminal window, navigate to the `frontend` folder, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
### 4. Play the Game
Open your browser and navigate to `http://localhost:5173` to enter the FootballVerse!
---
## 📄 License
This project is licensed under the MIT License.
