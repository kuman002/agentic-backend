# Agentic AI Backend

A multi-agent AI system built with LangGraph and FastAPI that intelligently routes queries to specialized agents for weather information, document Q&A, meeting scheduling, and database queries.

## Features

- **Smart Query Routing**: Automatically classifies user queries and routes them to the appropriate agent
- **Weather Agent**: Fetches real-time weather data using OpenWeather API
- **Document Q&A Agent**: Processes PDF documents and answers questions using RAG (Retrieval-Augmented Generation)
- **Meeting Scheduler**: Intelligently schedules meetings based on weather conditions
- **Database Agent**: Executes natural language queries against a meetings database
- **RESTful API**: FastAPI endpoints for document upload and chat queries
- **Error Handling**: Comprehensive error handling and fallback mechanisms
- **Vector Store**: Uses Chroma with HuggingFace embeddings for document retrieval

## Prerequisites

- Python 3.12 or higher
- Conda (for environment management)
- GROQ API Key (for LLM access)
- OpenWeather API Key (for weather data)

## Installation

### 1. Create and Activate Virtual Environment

```bash
conda create -n venv_py312 python=3.12 -y
conda activate venv_py312
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Get your keys from:
- [Groq Console](https://console.groq.com)
- [OpenWeather API](https://openweathermap.org/api)

## Project Structure

```
agentic-backend/
├── main.py                 # FastAPI application entry point
├── agent_graph.py         # LangGraph workflow and agent definitions
├── tool.py                # Tool definitions (weather, web search)
├── rag.py                 # RAG pipeline for document processing
├── database.py            # SQLAlchemy database models
├── meeting.py             # Meeting management utilities
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
├── meetings.db            # SQLite database (auto-created)
└── README.md             # This file
```

## API Endpoints

### 1. Upload Document
**POST** `/upload`

Upload a PDF document for processing.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "message": "Document processed successfully."
}
```

### 2. Chat Query
**POST** `/chat`

Send a query to the agentic system.

**Request:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Chennai?"}'
```

**Response:**
```json
{
  "response": "Weather in Chennai: clear sky, Temp: 28.5°C"
}
```

## Usage Examples

### Weather Query
```
Query: "What's the weather in New York?"
Response: Agent routes to weather_worker → fetches real-time data
```

### Document Q&A
```
Query: "What are the company policies?"
Response: Agent routes to doc_worker → searches uploaded documents
```

### Meeting Scheduling
```
Query: "Schedule a meeting in London"
Response: Agent routes to scheduler_worker → checks weather → recommends scheduling
```

### Database Query
```
Query: "Show me all meetings tomorrow"
Response: Agent routes to db_worker → executes SQL → returns results
```

## Architecture

### Agent Flow

```
User Query
    ↓
Router Agent (Classification)
    ↓
    ├─→ Weather Agent
    ├─→ Document QA Agent
    ├─→ Meeting Scheduler
    └─→ Database Query Agent
    ↓
Response
```

### Components

1. **Router Node**: Classifies incoming queries into 4 categories
2. **Weather Agent**: Extracts city, fetches weather using OpenWeather API
3. **Document QA Agent**: Uses Chroma vector store for similarity search, falls back to web search
4. **Scheduler Agent**: Extracts location, checks weather, provides scheduling recommendation
5. **Database Agent**: Uses SQL agent to convert natural language to SQL queries

## Configuration

### LLM Model
Currently using `llama-3.3-70b-versatile` from Groq. To change:

Edit `agent_graph.py`:
```python
llm = ChatGroq(
    temperature=0,
    model_name="your_model_here",
    api_key=os.getenv("GROQ_API_KEY")
)
```

### Vector Store
Document embedding uses HuggingFace's `all-MiniLM-L6-v2` model. Change in `rag.py`:
```python
embeddings = HuggingFaceEmbeddings(model_name="your_model_here")
```

## Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

Access Swagger documentation at `http://localhost:8000/docs`

## Database

### Meeting Table Schema

```sql
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    start_time VARCHAR,
    description VARCHAR
);
```

### Meeting Management

Use `meeting.py` utilities:
- `create_meeting()`: Add a new meeting
- `get_all_meetings()`: List all meetings
- `update_meeting()`: Modify meeting details
- `delete_meeting()`: Remove a meeting
- `search_meetings()`: Search by title or description

## Troubleshooting

### API Key Errors
- Verify `.env` file exists in project root
- Check API keys are correct and active
- Ensure keys have sufficient quota

### LLM Model Deprecated
If receiving "model decommissioned" error:
1. Check [Groq deprecations](https://console.groq.com/docs/deprecations)
2. Update model name in `agent_graph.py`
3. Restart the application

### Document Upload Issues
- Ensure PDF file is valid
- Check file size (recommended < 50MB)
- Verify write permissions in project directory

### Database Connection
- SQLite database creates automatically on first run
- Check for `meetings.db` in project root
- Ensure no file permission issues

### Weather API Failures
- Verify OpenWeather API key is valid
- Check city name spelling
- Rate limit: Free tier allows 60 calls/minute

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **LangChain**: LLM framework
- **LangGraph**: Workflow orchestration
- **Groq**: LLM provider
- **Chroma**: Vector database
- **HuggingFace**: Embeddings
- **SQLAlchemy**: ORM
- **Python-dotenv**: Environment management

## Performance Tips

1. **Caching**: LangChain caches LLM responses by default
2. **Batch Queries**: Process multiple queries sequentially for better throughput
3. **Document Size**: Smaller PDFs process faster
4. **Chunking**: Adjust chunk size in `rag.py` for better accuracy

## Future Enhancements

- [ ] Multi-language support
- [ ] Real-time streaming responses
- [ ] Advanced caching strategies
- [ ] Message history tracking
- [ ] User authentication
- [ ] Rate limiting
- [ ] Monitoring and logging dashboard
- [ ] Docker containerization

## License

MIT

## Support

For issues or questions, check:
- [LangChain Documentation](https://docs.langchain.com)
- [Groq Documentation](https://console.groq.com/docs/api-overview)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

---

**Last Updated**: January 21, 2026
