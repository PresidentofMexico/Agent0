# Exa Scheduler

Exa Scheduler is an intelligent, autonomous scheduling assistant designed to help manage your calendar, reminders, and tasks using natural language.

## Features
- **ReAct Agent Architecture**: Uses a Reasoning + Acting loop to solve complex problems.
- **Tool Integration**: Built-in support for Calendar, Reminders, and Email (implementations pending).
- **Local Memory**: ChromaDB integration for long-term memory (pending).
- **Extensible**: Easy to add new tools using Pydantic-based schemas.

## Project Structure
```
exa-scheduler/
├── .antigravity/       # Agent-specific settings
├── config/             # Configuration files
├── src/
│   ├── core/           # Orchestrator, Planner, Memory
│   ├── llm/            # OpenAI Client Wrapper
│   ├── tools/          # Tool implementations
│   └── prompts/        # System prompts
└── tests/              # Unit and Integration tests
```

## Setup

### Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/) (optional, but recommended) or `pip`

### Installation
1. Clone the repository (if applicable) or navigate to the directory.
2. Install dependencies:
   ```bash
   # Using Poetry
   poetry install
   
   # OR using pip
   pip install .
   ```
3. Configure Environment:
   - Copy `config/secrets.example.yaml` to `config/secrets.yaml` (implementation detail may vary, or use .env).
   - Set up `.env` file with `OPENAI_API_KEY`:
     ```bash
     echo "OPENAI_API_KEY=sk-..." > .env
     ```

## Usage

Run the main entry point:
```bash
python src/main.py
```

## Development

### Running Tests
```bash
pytest tests/
```

### Adding a New Tool
1. Create a new file in `src/tools/` (e.g., `my_tool.py`).
2. Inherit from `BaseTool` (in `src.tools.base`).
3. Define the arguments as Pydantic fields.
4. Implement the `run` method.
5. Register the tool in `src/main.py` or the Orchestrator initialization.

## License
Proprietary / Private.
