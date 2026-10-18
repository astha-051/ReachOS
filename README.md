# ReachOS — Autonomous B2B Lead Intelligence & Personalized Outreach Agent

> **Built for the Nebius × NVIDIA Global AI Hackathon**

ReachOS is a production-grade, AI-native B2B sales intelligence and outreach platform. It takes raw lead lists, validates contact data, performs real-time company web research using **Tavily**, analyzes business pain points and buying intent using **NVIDIA Nemotron models via Nebius Token Factory**, qualifies leads with transparent evidence scorecards, generates hyper-personalized outreach drafts, requires human approval before sending, and analyzes prospect email responses for intelligent next action recommendations.

---

## 🚀 Key Features & Highlights

1. **Lead Validation & CSV Engine**: Robust CSV parsing with header normalization, regex validation, and duplicate row detection.
2. **Tavily Web Research Engine**: Deep web research gathering verified company signals, executive news, and pain points.
3. **Nemotron Model Router (Nebius Token Factory)**:
   - **Fast Model** (`nvidia/nemotron-4-30b-instruct`): Swift response classification and quick extraction.
   - **Reasoning Model** (`nvidia/nemotron-4-120b-instruct`): Lead qualification scoring (Fit, Intent, Timing) with grounded evidence justification.
   - **Deep Model** (`nvidia/nemotron-4-550b-instruct`): In-depth web research synthesis and email outreach generation.
4. **Human-in-the-Loop Workflow**: Review, edit, approve, or reject AI-generated outreach before dispatching via **Resend** or safe **Mock Email Provider**.
5. **Reply Intelligence**: Autonomous reply classification (`INTERESTED`, `OBJECTION`, `QUESTION`, `UNSUBSCRIBE`) and recommended sales actions (`BOOK_MEETING`, `ANSWER_QUESTION`, etc.).
6. **Next.js 14 SaaS Workbench**: Modern dark-mode UI with glassmorphic cards, live metrics, and split-drawer lead scorecards.

---

## 🏗️ Architecture Overview

```
                  ┌────────────────────────┐
                  │    Next.js 14 Dashboard│
                  │   (Tailwind + Lucide)  │
                  └───────────┬────────────┘
                              │ REST API
                  ┌───────────▼────────────┐
                  │      FastAPI Backend   │
                  └─────┬──────┬──────┬────┘
                        │      │      │
      ┌─────────────────┘      │      └─────────────────┐
      │                        │                        │
┌─────▼───────┐        ┌───────▼──────┐        ┌────────▼────────┐
│  Tavily API │        │  Nebius AI   │        │ Resend / Mock   │
│ Web Research│        │ NVIDIA       │        │ Email Dispatch  │
│ Search Engine│       │ Nemotron     │        │ Provider        │
└─────────────┘        └──────────────┘        └─────────────────┘
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:

```env
# Nebius Token Factory & NVIDIA Nemotron Models
NEBIUS_API_KEY=your_nebius_api_key
NEBIUS_BASE_URL=https://api.nebius.ai/v1

NEMOTRON_FAST_MODEL=nvidia/nemotron-4-30b-instruct
NEMOTRON_REASONING_MODEL=nvidia/nemotron-4-120b-instruct
NEMOTRON_DEEP_MODEL=nvidia/nemotron-4-550b-instruct

# Tavily Web Research API
TAVILY_API_KEY=your_tavily_api_key

# Email Dispatch Provider (mock or resend)
EMAIL_PROVIDER=mock
RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=sales@reachos.ai

# Platform Settings
DATABASE_URL=sqlite:///./reachos.db
DEMO_MODE=true
```

---

## 🛠️ Quickstart Guide

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI Documentation**: `http://localhost:8000/docs`

---

### Option 2: Manual Local Setup

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Run Backend Test Suite

```bash
python -m pytest tests/
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 📜 License

MIT License — Built for Nebius × NVIDIA Global AI Hackathon 2026.
