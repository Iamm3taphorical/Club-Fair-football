# FootballVerse AI

### Discover. Play. Coach.

FootballVerse AI is an AI-driven football gaming ecosystem that combines computer vision, tactical decision-making, and football knowledge into a unified interactive experience.

Developed for the BRAC University Computer Club (BUCC), the platform challenges players across three distinct dimensions of football: physical reflexes, strategic intelligence, and historical knowledge. Through real-time gesture recognition, tactical match simulations, and advanced analytics, FootballVerse AI creates a unique environment where players can compete, learn, and improve.

**Institution:** BRAC University
**Organization:** BRAC University Computer Club (BUCC)
**University Website:** https://www.bracu.ac.bd/
**BUCC Website:** https://www.bracucc.org/

---

## Project Overview

FootballVerse AI reimagines football gaming by integrating artificial intelligence with interactive gameplay. Rather than focusing solely on traditional football mechanics, the platform evaluates a player's ability to react, strategize, and understand the sport.

The project is designed around three core objectives:

* Physical interaction through computer vision
* Tactical decision-making through match simulation
* Football knowledge assessment through adaptive trivia

Each activity contributes to a persistent Football DNA profile that reflects the player's strengths, tendencies, and overall performance.

---

## Key Features

### AI-Powered Gameplay

The platform utilizes multiple AI-driven systems, including computer vision, tactical simulation engines, and player analytics to deliver a dynamic gaming experience.

### Real-Time Gesture Recognition

Using MediaPipe hand tracking, players can interact with the game through natural hand movements captured directly from a webcam.

### Football DNA System

A persistent player profile records performance metrics across all game modes and generates detailed insights into individual play styles.

### Global Leaderboards

Players compete across dedicated leaderboards for each game mode, allowing performance comparisons on a global scale.

### Immersive User Experience

The interface features stadium-inspired visuals, dynamic environments, and responsive interactions designed to enhance player engagement.

---

## Game Modes

### Player Arena

**Focus:** Reflexes and Computer Vision

Player Arena places users in a virtual penalty shootout environment where hand gestures are used to control aiming and shooting mechanics.

#### Features

* Real-time hand tracking
* Gesture-based shot control
* AI-controlled goalkeeper
* Accuracy and reaction-time analysis
* Performance reporting

#### Outcome

At the end of each session, players receive a detailed report including:

* Accuracy metrics
* Reaction-time statistics
* Football DNA analysis
* Comparisons with legendary footballers

---

### Tactical Coach

**Focus:** Strategy and Resource Management

Tactical Coach places players in the role of a football manager responsible for making decisions throughout a simulated ninety-minute match.

The match is divided into strategic intervals where players must adapt to changing conditions and respond to AI-generated scenarios.

#### Features

* Tactical pitch visualization
* Formation management
* Dynamic match scenarios
* Tactical decision scoring
* Adaptive opponent behavior

#### Outcome

Players earn Tactical Points and unlock rankings based on their managerial performance.

Examples include:

* Sunday League Coach
* Tactical Analyst
* Elite Tactician
* Master Strategist

---

### Fan Trivia

**Focus:** Football Knowledge and History

Fan Trivia is a time-based challenge that evaluates a player's understanding of football history, players, managers, stadiums, and iconic matches.

Players receive progressively revealing clues and must identify the correct answer before time expires.

#### Categories

* Guess the Player
* Guess the Coach
* Guess the Stadium
* Guess the Iconic Match

#### Outcome

Participants are ranked according to their performance and placed on the Fan Leaderboard.

---

## Football DNA System

The Football DNA System is a cross-platform analytics engine that evaluates player behavior across all game modes.

Metrics include:

* Shooting accuracy
* Reaction speed
* Tactical adaptability
* Decision-making tendencies
* Football knowledge proficiency

Based on collected data, the system generates player profiles and identifies similarities with renowned footballers and managers.

---

## Technical Architecture

### Frontend

| Technology  | Purpose                       |
| ----------- | ----------------------------- |
| React       | User Interface Development    |
| TypeScript  | Type Safety and Scalability   |
| Vite        | Frontend Tooling              |
| Vanilla CSS | Custom Styling and Animations |

### Backend

| Technology | Purpose                |
| ---------- | ---------------------- |
| Python     | Core Application Logic |
| FastAPI    | API Development        |
| SQLAlchemy | Database ORM           |
| SQLite     | Data Storage           |

### AI Components

#### Computer Vision

* MediaPipe Hand Tracking
* Gesture Recognition
* Real-Time Input Processing

#### Tactical Engine

* Match Simulation Algorithms
* Scenario Generation System
* Tactical Evaluation Framework

#### Analytics Engine

* Player Performance Tracking
* Football DNA Classification
* Leaderboard Scoring System

---

## Repository Structure

```text
FootballVerseAI/
│
├── backend/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── database/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── assets/
│
├── requirements.txt
├── package.json
└── README.md
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/Iamm3taphorical/bucc_FootballVerseAI.git

cd bucc_FootballVerseAI
```

### Backend Setup

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend server:

```bash
cd backend

uvicorn main:app --reload
```

Backend endpoint:

```text
http://localhost:8000
```

### Frontend Setup

Open a new terminal:

```bash
cd frontend

npm install

npm run dev
```

Frontend endpoint:

```text
http://localhost:5173
```

---

## Development Roadmap

### Current Features

* Core user interface
* Gesture-based penalty shootout
* Football trivia system
* Tactical match simulator

### Planned Features

* Persistent player accounts
* Football DNA analytics dashboard
* Achievement and progression systems
* Global competitive leaderboards
* Multiplayer game modes
* AI coaching assistant
* Mobile platform support

---

## Contributors

### Mahir Dyan

GitHub: https://github.com/Iamm3taphorical

### Dibyo Singho Barua Subrajit

GitHub: https://github.com/whosubrajit

### Adittya Dey

GitHub: https://github.com/Adittya202

---

## Acknowledgements

This project was developed for the BRAC University Computer Club (BUCC).

Special thanks to:

* BRAC University
* BRAC University Computer Club
* MediaPipe Contributors
* The Open Source Community

---

## License

This project is licensed under the MIT License.

See the LICENSE file for additional information.
