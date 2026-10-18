# ReachOS — AI-Powered B2B Lead Intelligence & Outreach

**Built for the Nebius × NVIDIA Global AI Hackathon 2026**

ReachOS is an AI-powered sales intelligence platform that helps B2B teams turn raw lead lists into researched, qualified prospects and personalized outreach drafts.

It combines lead validation, web research through Tavily, AI-powered analysis using NVIDIA Nemotron models through Nebius Token Factory, and a human-in-the-loop outreach workflow. The goal is to reduce repetitive sales research while making AI-generated recommendations easier to inspect and review.

**Live Demo:** https://reach-8ptiuuoxk-astha-051.vercel.app  
**Source Code:** https://github.com/astha-051/ReachOS  
**API Documentation:** https://reachos-fapk.onrender.com/docs

## The Problem

B2B sales teams often spend significant time validating lead data, researching companies, identifying potential business needs, qualifying prospects, and writing personalized emails.

Manual research can slow down prospecting, while generic outreach may fail to address a prospect's actual business context.

ReachOS brings these tasks into a single workflow, helping sales teams make more informed decisions before contacting a prospect.

## How ReachOS Works

1. **Import leads:** Upload a CSV containing prospect and company information.
2. **Validate data:** Check contact fields, website formats, and incomplete or duplicate records.
3. **Research companies:** Use Tavily to retrieve relevant web information and potential business signals.
4. **Qualify prospects:** Use NVIDIA Nemotron through Nebius Token Factory to analyze available evidence and generate lead scores.
5. **Generate outreach:** Create personalized email drafts grounded in the available research.
6. **Review and approve:** Let a human review, edit, approve, or reject outreach before dispatch.
7. **Analyze replies:** Where configured and supported by the workflow, classify prospect replies and suggest possible next actions.

## Key Features

### Lead Validation and CSV Import
- CSV parsing and header normalization.
- Contact-field and website-format validation.
- Detection of duplicate records.
- Lead status tracking.

### Web-Based Company Research
- Tavily-powered web search.
- Research summaries, potential pain points, and business opportunities.
- Source URLs and supporting snippets for review.
- Research confidence information where available.

Research results should be treated as AI-assisted findings, not as independently verified facts. Review the cited sources before relying on them.

### NVIDIA Nemotron-Powered Analysis
ReachOS uses NVIDIA Nemotron models through Nebius Token Factory for supported AI tasks, including prospect qualification and personalized outreach generation.

The qualification workflow can provide:
- Fit, intent, and timing scores.
- An overall lead score and priority.
- Evidence-based explanations.
- Personalized email drafts and supporting research references.

**Model configuration:** Use the model IDs configured in the application and deployment environment. The `nvidia/nemotron-3-super-120b-a12b` model has been tested during development. Update this section if the deployed application uses additional models or a different routing configuration.

### Human-in-the-Loop Outreach
- Review generated email drafts.
- Inspect personalization points and supporting evidence.
- Approve or reject drafts before dispatch.
- Use the mock email provider for safe testing or configure a supported real email provider.

### Lead Pipeline and Dashboard
- Lead and research status tracking.
- Qualification scores and priorities.
- Outreach status visibility.
- Persistent lead records and related research data, backed by the configured database.

### Reply Intelligence
The project includes reply-classification and next-action workflows. Confirm the live configuration and test these workflows before relying on them in production.

## Architecture

```text
                 Next.js Frontend
                        |
                     REST API
                        |
                 FastAPI Backend
                        |
          +-------------+-------------+
          |             |             |
     Tavily API    Nebius Token    Database
                   Factory API
                        |
                NVIDIA Nemotron
                        |
               AI Analysis & Drafts
                        |
                Human Review
                        |
                Email Provider
                 Resend / Mock
```

### Technology Stack

- **Frontend:** Next.js, React, Tailwind CSS, Lucide icons
- **Backend:** Python, FastAPI
- **AI inference:** Nebius Token Factory and NVIDIA Nemotron
- **Web research:** Tavily API
- **Database:** SQLAlchemy-compatible database configured through `DATABASE_URL`
- **Email:** Resend integration or mock provider
- **Deployment:** Vercel frontend and Render backend
- **Local development:** Docker Compose or manual setup

## Prerequisites

Before running ReachOS locally, install:

- Git
- Docker Desktop, if using Docker Compose
- Python version compatible with the backend dependencies
- Node.js and npm, if running the frontend manually
- A Nebius Token Factory API key
- A Tavily API key

A Resend API key is required only if you want to configure real email delivery.

## Quick Start — Docker Compose

The following commands assume the repository's Docker Compose configuration supports running the frontend and backend together.

### 1. Clone the repository

```bash
git clone https://github.com/astha-051/ReachOS.git
cd ReachOS
```

### 2. Create your environment file

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
notepad .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Edit `.env` and provide the API keys and configuration required by the application.

Use the exact environment-variable names and model IDs expected by the current source code. Do not commit `.env` or expose API keys in screenshots or recordings.

### 3. Start the application

```bash
docker compose up --build
```

When the services have started, open:

- **Frontend:** http://localhost:3000
- **Backend API documentation:** http://localhost:8000/docs

Check the service logs if either URL fails to load.

## Manual Local Setup

Use this option if you prefer to run the backend and frontend separately.

### 1. Configure the backend

Open a terminal in the repository root:

```bash
cd backend
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use Command Prompt:

```bat
venv\Scripts\activate.bat
```

On Linux/macOS:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Configure the backend environment variables using the names expected by the application, then start the API from the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Configure the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Set the frontend API URL in the appropriate local environment file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Use the exact API prefix configured by the backend. Restart the frontend after changing environment variables.

Start the frontend:

```bash
npm run dev
```

Open http://localhost:3000.

## Using ReachOS

1. Open the dashboard.
2. Import a CSV containing your lead records.
3. Review validation results and correct incomplete or invalid records.
4. Select an eligible lead and run company research.
5. Review the research summary, sources, and identified business signals.
6. Run lead qualification and inspect the score and supporting evidence.
7. Generate a personalized email draft.
8. Review and edit the draft before approving or rejecting it.
9. Check the lead's status and refresh the application to verify persistence.

Available actions depend on the current application configuration and the lead's workflow status.

## Email Configuration

ReachOS supports a mock email provider for development and demonstrations.

For safe testing:

```env
EMAIL_PROVIDER=mock
```

Mock mode simulates the sending workflow; it does not deliver real emails.

For real email delivery, configure the supported provider, API credentials, and sender identity. Verify that the sender domain is authorized and test delivery before using the feature with real prospects.

Never describe an email as delivered unless the real provider confirms delivery.

## Testing and Troubleshooting

Run the backend tests from the backend directory after installing the development dependencies:

```bash
python -m pytest tests/
```

If the test directory or test dependencies differ in the current repository, follow the actual project structure and update this command accordingly.

Common issues:

- **Frontend cannot reach the backend:** Check the API URL and backend CORS configuration.
- **AI requests fail:** Verify the Nebius API key, base URL, model ID, account access, and available credits.
- **Research fails:** Check the Tavily API key and service response.
- **Leads disappear after refresh:** Check the database configuration and API responses.
- **Emails are not delivered:** Confirm whether the provider is configured for mock mode or real delivery.
- **Docker services fail to start:** Review container logs and confirm that required environment variables are set.

## Security and Responsible Use

- Keep API keys and database credentials out of source control.
- Store secrets in environment variables or your hosting provider's secret-management settings.
- Avoid uploading unnecessary personal or confidential lead data.
- Review research sources before acting on AI-generated claims.
- Keep human approval enabled before sending outreach.
- Respect applicable privacy, anti-spam, and unsubscribe requirements.

## Current Limitations

ReachOS is an evolving hackathon project. Available capabilities depend on the configured services and the workflows tested in the deployed version.

- Research quality depends on the available web sources.
- AI-generated scores and recommendations may be inaccurate.
- Real email delivery requires a correctly configured email provider.
- Reply analysis and other optional workflows should be tested against the deployed configuration before being treated as production-ready.

## Hackathon Submission

ReachOS was developed for the Nebius × NVIDIA Global AI Hackathon 2026.

The project demonstrates a practical application of NVIDIA Nemotron models through Nebius Token Factory in a multi-step sales intelligence workflow.

- **Live application:** https://reach-8ptiuuoxk-astha-051.vercel.app
- **GitHub repository:** https://github.com/astha-051/ReachOS
- **Backend API:** https://reachos-fapk.onrender.com/docs
- **Demo video:** Add the public YouTube URL here.

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for the full license text.

---

