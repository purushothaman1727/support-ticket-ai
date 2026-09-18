
# Support Ticket AI

An AI-powered support ticket analytics system built using Python, FastAPI, Streamlit, and Ollama.

## Features

- Natural language ticket queries
- Ticket count analysis
- Average customer rating
- Top resolved agent analysis
- Lowest-rated agent detection
- Critical unresolved ticket detection
- Resolution-time anomaly detection
- High-priority unresolved ticket detection
- REST API using FastAPI
- Minimal interactive UI using Streamlit
- Local LLM integration using Ollama
- DDD-inspired architecture with separation of concerns

## Tech Stack

- Python 3.13+
- FastAPI
- Streamlit
- Pandas
- Pydantic
- Ollama
- Llama 3.2
- Pytest
- HTTPX

## Project Structure

```text
support-ticket-ai/
├── app/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── data/
│   └── support_tickets.csv
├── tests/
├── ui/
│   └── app.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

## Installation

### 1. Clone or open the project

```bash
cd support-ticket-ai
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Ollama Setup

Install Ollama and pull the required model:

```bash
ollama pull llama3.2
```

Start the Ollama service:

```bash
ollama serve
```

Configure the `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=60
```

## Run the Application

### Start FastAPI

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit UI

Open another terminal:

```bash
python -m streamlit run ui/app.py
```

The UI will open at:

```text
http://localhost:8501
```

## Supported Queries

Example questions:

- How many open tickets are there?
- What is the average customer rating for Technical tickets?
- Which agent resolved the most tickets?
- Which agent has the lowest average rating?
- Which agent resolved the most tickets this month?
- How many critical tickets were not resolved within 12 hours?
- Show resolution time anomalies this week.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/query` | Process natural language queries |
| GET | `/api/anomalies` | Detect ticket anomalies |

## Testing

Run all tests:

```bash
pytest -q
```

## Important Dataset Limitation

The dataset contains historical ticket records.

For time-based analysis such as "this month" and ticket age calculations, the system uses the dataset's latest available timestamp as a reference when appropriate.

Therefore, time-based results are relative to the dataset and not necessarily the current real-world date.

## Architecture

The project follows a DDD-inspired structure:

- Domain: Business entities and domain services
- Application: Use cases and application ports
- Infrastructure: CSV repository and Ollama integration
- Presentation: REST API and UI

The architecture separates business logic from external dependencies to improve maintainability and testability.

## License

This project was developed as part of a technical assessment.