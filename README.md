# 📡 Campus WiFi Sharing Sandbox: An Evolutionary Game Approach

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4.0-FF6384)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive simulation and testbed platform designed to solve the "tragedy of the commons" in campus WiFi resource sharing. By integrating **Evolutionary Game Theory**, a **Dual-Asset Economy (Token & Reputation)**, and the **Generalized Second-Price (GSP) Auction**, this system effectively suppresses free-riding behaviors and steers the student population toward an Evolutionary Stable Strategy (ESS).

---

## ✨ Key Features

- **📊 Multi-Agent Evolutionary Dashboard**: A real-time, visual sandbox powered by backend agents. It simulates strategy mutations (Cooperation, Free-riding, Reciprocity) driven by the Replicator Dynamics equation.
- **⚖️ GSP Auction Mechanism**: Resolves peak-hour network congestion by allowing users to submit sealed bids. Winners pay the second-highest price, ensuring truthful bidding remains the dominant strategy.
- **🪙 Dual-Asset Economic Model**: 
  - **Tokens (Points)**: Used as circulating currency for bandwidth purchasing and mall redemption.
  - **Reputation**: An asymmetric dynamic scoring algorithm ($R = \min(100, \max(0, 80 + 2 S_{gb} - C_{gb}))$) that heavily rewards sharing while strictly penalizing pure consumption.
- **🛡️ Role-Based Access Control (RBAC)**: Built-in Admin and Root privileges for real-time node removal, user management, and dynamic mall pricing.
- **📈 Real-Time Visualization**: Powered by Chart.js for zero-latency updates on strategy distributions and reputation tiers.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js (No heavy frameworks, ensuring maximum rendering performance for the dashboard).
- **Backend**: Python, **FastAPI** (Asynchronous non-blocking architecture ideal for high-frequency bidding and multi-agent simulation).
- **Database**: SQLite (Lightweight, ACID-compliant persistence for token ledgers).

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.

### 2. Install Dependencies
Install the required Python packages using pip:
```bash
pip install fastapi uvicorn pydantic
```

### 3. Run the Server
Navigate to the project directory and start the FastAPI server:
```bash
python main.py
```
*(Alternatively, you can run: `uvicorn main:app --host 127.0.0.1 --port 8000 --reload`)*

### 4. Access the Application
Open your web browser and go to:
👉 **`http://127.0.0.1:8000`**

- **Default Root Account:**
  - Student ID: `root`
  - Password: `root123`

---

## 🧠 Theoretical Background

The core of the simulation relies on a specialized $3 \times 3$ asymmetric payoff matrix to quantify interactions among agents:

| Player A \ Player B | Cooperation (🤝) | Free-riding (🆓) | Reciprocity (🔄) |
| :--- | :--- | :--- | :--- |
| **Cooperation (🤝)** | (+3, +3) | (-2, +5) | (+1, +1) |
| **Free-riding (🆓)** | (+5, -2) | (0, 0) | (-2, +1) |
| **Reciprocity (🔄)** | (+1, +1) | (+1, -2) | (+1, +1) |

The backend `EvolutionEngine` instantiates virtual students who adjust their strategies dynamically based on their relative payoffs compared to the population average, vividly demonstrating the convergence to Nash Equilibrium in a distributed network.

---

## 📁 Project Structure

```text
CampusWiFiGame/
├── main.py              # FastAPI backend entry, DB initialization, and MAS Engine
├── campus_wifi.db       # SQLite database (Auto-generated upon first run)
└── static/
    └── index.html       # Single-page application (SPA) frontend with all UI/UX
```

---

## 👥 Authors & Contributors

This project was designed and developed by:
- **Yingrui Zhang** (ID: 202330008)
- **Haijiao Wang** (ID: 202330041)
- **Mingze Ren** (ID: 2023300073)

For detailed theoretical derivations and empirical analysis, please refer to our accompanying research paper: *"Design and Implementation of a Campus WiFi Sharing Platform Based on Evolutionary Game Theory"*.

---
*If you find this project helpful for your research, feel free to star this repository! ⭐*