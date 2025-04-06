# Complete Prompt for Vietnamese Stock MCP Server with Multi-Agent Architecture

## Project Overview
Create a Market Collection and Processing (MCP) Server for Vietnamese Stock Prices with the following features:
- Main language: Python
- LLM integration: Ollama
- Database: DuckDB for price data storage
- Multi-agent architecture with 3 specialized AI agents:
  - Fundamental Analysis Agent
  - Technical Analysis Agent
  - Portfolio Manager Agent

## Technical Stack

### Core Components:
- Python 3.9+
- DuckDB for time-series price data
- Ollama for local LLM integration
- FastAPI for API endpoints
- LangChain/LangGraph for agent architecture
- Redis for caching and agent communication
- Docker for containerization

### Data Collection:
- HTTPX/Requests for API calls
- BeautifulSoup4/Selenium (if needed for web scraping)
- APScheduler for scheduling data collection

### Data Processing:
- Pandas & Polars for data manipulation
- NumPy for numerical operations
- FinTA/TA-Lib for technical indicators

### Agent Framework:
- LangChain/LangGraph for agent workflows
- Agent memory systems with shared vector DB
- Tool integration for financial analysis

## Folder Structure
```
vietnamese-stock-mcp/
├── config/
│   ├── settings.py                # Global settings
│   └── logging_config.py          # Logging configuration
├── data/
│   ├── raw/                       # Raw data from API calls
│   ├── processed/                 # Processed data
│   └── historical/                # Historical data archives
├── src/
│   ├── collectors/                # Data collection modules
│   │   ├── __init__.py
│   │   ├── vndirect.py            # VNDirect API client
│   │   ├── ssi.py                 # SSI API client
│   │   └── hsx.py                 # HOSE/HSX API client
│   ├── processors/                # Data processing modules
│   │   ├── __init__.py
│   │   ├── cleaner.py             # Data cleaning utilities
│   │   └── transformer.py         # Data transformation utilities
│   ├── database/                  # Database operations
│   │   ├── __init__.py
│   │   ├── duckdb_client.py       # DuckDB client
│   │   ├── models.py              # Data models
│   │   └── operations.py          # CRUD operations
│   ├── api/                       # API server
│   │   ├── __init__.py
│   │   ├── routes.py              # API endpoints
│   │   └── middlewares.py         # API middlewares
│   ├── llm/                       # LLM integration
│   │   ├── __init__.py
│   │   ├── ollama_client.py       # Ollama client
│   │   ├── prompts.py             # General prompt templates
│   │   ├── agent_prompts/         # Agent-specific prompts
│   │   │   ├── fundamental_prompts.py
│   │   │   ├── technical_prompts.py
│   │   │   └── portfolio_prompts.py
│   │   └── evaluation.py          # Agent output evaluation
│   ├── agents/                    # Agent-related code
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class
│   │   ├── fundamental_agent.py   # Fundamental analysis agent
│   │   ├── technical_agent.py     # Technical analysis agent
│   │   ├── portfolio_agent.py     # Portfolio management agent
│   │   ├── orchestrator.py        # Agent orchestration
│   │   ├── tools/                 # Shared agent tools
│   │   │   ├── __init__.py
│   │   │   ├── data_tools.py      # Data retrieval tools
│   │   │   ├── calculation_tools.py # Financial calculations
│   │   │   └── viz_tools.py       # Visualization tools
│   │   └── memory/                # Agent memory systems
│   │       ├── __init__.py
│   │       └── shared_memory.py   # Shared knowledge base
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       └── helpers.py             # Helper functions
├── scripts/                       # Utility scripts
│   ├── setup.sh                   # Setup script
│   └── backfill.py                # Historical data backfill
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── notebooks/                     # Jupyter notebooks for analysis
├── docker/                        # Docker configuration
│   ├── Dockerfile                 # Main Dockerfile
│   └── docker-compose.yml         # Multi-container setup
├── .env.example                   # Example environment variables
├── .gitignore                     # Git ignore file
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Poetry config (optional)
├── main.py                        # Application entry point
└── README.md                      # Project documentation
```

## Key Files Implementation Requirements

### 1. `main.py` - Application Entry Point
- Initialize FastAPI application
- Setup DuckDB connection
- Configure logging
- Start scheduled tasks
- Initialize agent system

### 2. `src/database/duckdb_client.py` - DuckDB Implementation
- Connection pool management
- Table creation for Vietnamese stock data
- Optimized time-series queries
- Data partitioning strategy
- Support for both in-memory and persistent storage

### 3. `src/collectors/*.py` - Data Collection
- Authentication to Vietnamese stock data sources
- Rate limiting and retry logic
- Data validation before storage
- Support for different data frequencies (tick, minute, daily)
- Historical backfilling capabilities

### 4. `src/agents/base_agent.py` - Agent Framework
- Base agent class with shared functionality
- Integration with Ollama
- Tool registration mechanism
- Memory management
- Input/output parsing

### 5. `src/agents/orchestrator.py` - Agent Orchestration
- Routing logic for queries to appropriate agents
- Managing agent collaboration
- Handling conflicts between agent recommendations
- Providing unified API interface for agent system

### 6. `src/llm/ollama_client.py` - Ollama Integration
- Client for Ollama API
- Model loading and management
- Prompt template handling
- Response parsing
- Performance optimization

### 7. `src/api/routes.py` - API Endpoints
- Data retrieval endpoints
- Agent interaction endpoints
- Admin operations
- Authentication and rate limiting
- Documentation with Swagger/ReDoc

## Agent-Specific Implementation

### Fundamental Analysis Agent
- Company financial data analysis
- Ratio calculations and interpretation
- Industry comparison
- News sentiment analysis
- Valuation models (DCF, multiples)

### Technical Analysis Agent
- Chart pattern recognition
- Technical indicator calculation and interpretation
- Support/resistance identification
- Trend analysis
- Signal generation

### Portfolio Manager Agent
- Asset allocation recommendations
- Risk assessment
- Rebalancing suggestions
- Performance attribution
- Optimization strategies

## Data Model for DuckDB

```sql
-- Example schema for price data
CREATE TABLE stock_prices (
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    value DOUBLE,
    trades INTEGER,
    source VARCHAR,
    PRIMARY KEY (symbol, timestamp)
);

-- Partitioning by time
CREATE TABLE stock_prices_daily 
    AS SELECT * FROM stock_prices
    WHERE EXTRACT(HOUR FROM timestamp) = 0
    AND EXTRACT(MINUTE FROM timestamp) = 0;

-- Indexes
CREATE INDEX idx_stock_prices_symbol ON stock_prices(symbol);
CREATE INDEX idx_stock_prices_timestamp ON stock_prices(timestamp);
```

## Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: 
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama

volumes:
  redis-data:
  ollama-models:
```

## Key Dependencies (requirements.txt)

```
# Core
fastapi>=0.95.0
uvicorn>=0.22.0
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.24.0

# Database
duckdb>=0.9.0
sqlalchemy>=2.0.0

# Data Processing
pandas>=2.0.0
polars>=0.18.0
numpy>=1.24.0
pyarrow>=12.0.0

# Finance Tools
finta>=1.3.0
yfinance>=0.2.28
alpha_vantage>=2.3.1
# ta-lib requires separate installation

# LLM Integration
langchain>=0.0.267
langchain-core>=0.0.10
langchain-community>=0.0.10
langgraph>=0.0.10
chromadb>=0.4.6
sentence-transformers>=2.2.2

# Agent Tools
bs4>=0.0.1
matplotlib>=3.7.1
seaborn>=0.12.2
plotly>=5.14.1
pyportfolioopt>=1.5.4

# Infrastructure
redis>=4.5.5
apscheduler>=3.10.1
loguru>=0.7.0

# Development
pytest>=7.3.1
black>=23.3.0
isort>=5.12.0
```

## Implementation Priorities

1. First Phase:
   - Data collection infrastructure
   - DuckDB setup and optimization
   - Basic API endpoints

2. Second Phase:
   - Ollama integration
   - Single agent implementation (start with Technical Analysis)
   - Basic visualization tools

3. Third Phase:
   - Multi-agent architecture
   - Agent orchestration
   - Memory systems

4. Fourth Phase:
   - Advanced analytics
   - Portfolio optimization
   - User interfaces (if needed)

## Vietnamese Stock Market Specifics

- Support for HOSE, HNX, and UPCOM exchanges
- Handle T+1.5 settlement cycle
- Account for trading hours (9:00-11:30, 13:00-14:45)
- Support for order types specific to Vietnam (ATC, ATO, etc.)
- Handle foreign ownership limits and restrictions

## Testing Strategy

- Unit tests for core components
- Integration tests for API endpoints
- Agent evaluation metrics
- Performance benchmarks for DuckDB queries
- Backtesting framework for strategy recommendations