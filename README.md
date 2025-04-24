# AI-Powered Travel Assistant

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![ADK](https://img.shields.io/badge/ADK-0.2.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)

An AI-powered Travel Assistant implemented using Google's Agent Development Kit (ADK), DeepSeek, and OpenAI SDK. This assistant helps users with travel-related tasks such as flight searches, hotel bookings, destination information, and general travel questions.

## 📋 Table of Contents

- [Features](#-features)
- [Implementation Options](#-implementation-options)
- [User Interface](#-user-interface)
- [Technologies](#-technologies)
- [Project Structure](#-project-structure)
- [Installation and Setup](#-installation-and-setup)
- [Usage Guide](#-usage-guide)
- [Alternative Implementations](#-alternative-implementations)
- [System Architecture](#-system-architecture)
- [Extending ADK Implementation](#-extending-adk-implementation)
- [Troubleshooting](#-troubleshooting)

## 🚀 Project Status

This project is **production-ready** with all planned phases completed. The codebase has been reorganized for maintainability and all tests are currently passing.

### Development Phases
- ✅ Phase 1: Core Backend Components
- ✅ Phase 2: Agent Implementation
- ✅ Phase 3: API and Redis Integration
- ✅ Phase 4: Frontend Development
- ✅ Phase 5: Security Enhancements
- ✅ Phase 6: Error Handling Improvements

## 🌟 Features

- **Advanced Parameter Extraction** - Intelligently identifies travel details including airport codes and temporal references
- **Multi-pattern Recognition** - Enhanced detection of hotel preferences, dates, and locations
- **Real-time Travel Data** - Uses Google Search API with efficient caching for up-to-date information
- **Multiple LLM Support** - Primary: DeepSeek with Groq fallback, optimized client initialization
- **Stateful Conversation** - Maintains context throughout the planning process using an Agent Development Kit (ADK)
- **Enhanced Security** - Comprehensive input validation, rate limiting, and session protection
- **Error Recovery** - Robust error tracking with unique IDs, fallback mechanisms, and monitoring dashboard
- **Interactive UI** - Built with Streamlit for a user-friendly experience.

## 🔄 Implementation Options

### Primary Implementation: Google ADK

Our primary implementation uses Google's Agent Development Kit (ADK) which offers:

- **Modular Tool Architecture** - Well-defined tools for flight search, hotel search, and travel info
- **Advanced Agent Framework** - Sophisticated orchestration and routing capabilities
- **Built-in Web Interface** - ADK's native web interface for interacting with the agent
- **LLM Flexibility** - Support for multiple LLM providers including DeepSeek and Groq
- **Google Cloud Support** - Optional deployment to Google Cloud

### Alternative Implementation: Custom Framework

A legacy custom implementation is also available with:

- **Custom Agent Core** - Lightweight implementation focused specifically on travel use cases
- **Modular Architecture** - Clean separation of concerns (LLM, Search, State Management)
- **Streamlit Frontend** - Simple, intuitive user interface
- **React Alternative** - Optional web UI with the same backend capabilities

## 🖥️ User Interface

### ADK Built-in Web Interface (Recommended)

The primary UI is ADK's built-in web interface, accessible via the `adk web` command:

- **Interactive Chat Interface** - Clean, responsive design for conversations
- **Tool Visualization** - See which tools are being used for each query
- **Debug Information** - View detailed execution steps and reasoning
- **Session Management** - Maintain conversation context throughout interactions
- **No Additional Setup** - Available immediately after installing ADK

## 🥽️ Technologies

### AI & Machine Learning
- **Primary Framework**: Google Agent Development Kit (ADK) 0.2.0+
- **Primary LLM**: DeepSeek-Chat (accessed via OpenAI SDK)
- **Alternative LLMs**: Groq (llama3-8b-8192, via LiteLLM), OpenAI (optional)
- **LLM Integration**: OpenAI SDK configured to use DeepSeek API
- **Agent Architecture**: Modular tools with flexible orchestration
- **State Management**: ADK session management for conversation context

### Backend Components
- **Language**: Python 3.10+
- **Search Integration**: Google Serper API for real-time travel data
- **Tool Framework**: ADK's BaseTool implementation for travel-specific tools
- **Error Handling**: Structured error handling with fallback mechanisms
- **Deployment Options**: Local development or cloud deployment

### Frontend Options
- **Primary UI**: ADK built-in web interface (recommended)
- **Alternative UIs**: Streamlit app and React frontend

## 🧰️ Project Structure

The project is organized into these main components:

```
tavs/
├── travel_agent/           # Original custom implementation
│   ├── config/             # Configuration files
│   │   └── settings.py
│   ├── core/               # Core agent logic
│   │   └── agent.py        # Custom agent implementation
│   ├── models/             # Data models
│   │   ├── parameters.py   # Travel parameters (flights, hotels)
│   │   └── state.py        # Conversation state management
│   └── services/           # External service integrations
│       ├── llm/            # LLM client (DeepSeek, Groq) 
│       └── search/         # Serper search client
├── adk_travel_agent/       # Google ADK implementation (Primary)
│   ├── agent.py            # ADK agent with tools definition 
│   ├── llm_adapter.py      # LiteLLM integration for custom providers
│   └── main.py             # Entry point for ADK CLI
├── frontend/              # Optional React frontend
├── app.py                  # Streamlit app (alternative frontend)
├── .env                    # Environment variables with API keys
├── .env.example            # Example environment variables 
└── requirements.txt        # Python dependencies
```

## 🚀 Installation and Setup

### Prerequisites
- Python 3.10+
- API keys for:
  - **DeepSeek** (primary LLM) or **Groq** (alternative LLM)
  - **Google Serper API** (for search capabilities)

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/Salehnexta/tavs.git
cd tavs
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
# Install main dependencies including google-adk
pip install -r requirements.txt

# Install OpenAI SDK and LiteLLM for LLM provider support
pip install openai litellm
```

4. **Set Up Environment Variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: DEEPSEEK_API_KEY, SERPER_API_KEY
# Optional: GROQ_API_KEY (fallback)
```

## 👀 Usage Guide

### Using ADK Web Interface (Recommended)

1. **Navigate to the ADK Travel Agent Directory**
```bash
cd adk_travel_agent
```

2. **Start the ADK Web Interface**
```bash
adk web
```

3. **Access the Web Interface**
   - Open your browser to http://localhost:8000
   - You'll see the ADK Travel Assistant interface
   - Start asking travel-related questions

### Example Queries

#### Flight Searches
- "Find flights from New York to Tokyo for next Tuesday returning in 10 days"
- "What are the cheapest business class flights from London to Dubai in January?"
- "Are there any direct flights from San Francisco to Bangkok?"
- "I need morning flights from Boston to Chicago for a 3-day trip this month"

#### Hotel Queries
- "Find me a 5-star hotel in Paris within walking distance of the Eiffel Tower"
- "What are family-friendly resorts in Cancun with all-inclusive options?"
- "I need a budget hotel in central Tokyo with free WiFi"
- "Are there any boutique hotels in Rome near the Colosseum?"

#### Destination Information
- "Tell me about the best time to visit Bali considering weather and crowds"
- "What are the must-see attractions in Barcelona for a 4-day trip?"
- "What documents do I need for travel to Japan from the US?"
- "What's the local transportation like in Amsterdam?"

#### Complex Multi-turn Conversations
- "I'm planning a 2-week trip to Europe this summer"
  - *The agent will ask clarifying questions about preferences, budget, and interests*
- "I want to visit both mountains and beaches in the same trip"
  - *The agent can suggest destinations that offer both environments*
- "Help me plan a romantic anniversary trip"
  - *The agent will collect preferences and suggest complete itineraries*

### Advanced Options

```bash
# Run in terminal mode (no web interface)
adk run

# View detailed execution with debugging
adk web --debug
```

>[!TIP]
> The ADK web interface provides built-in debugging tools to visualize how the agent processes your request, which tools it uses, and how it formulates responses.

## 🧱 Alternative Implementations

### Using Original Streamlit Frontend

For those who prefer the original Streamlit implementation:

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Run the Streamlit app
streamlit run app.py

# Access in browser (default: http://localhost:8501)
```

### Using React Frontend

For the React frontend alternative:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev

# Access in browser (default: http://localhost:5173)
```

### Using the Flask API Backend

```bash
# Start the Flask API server
flask --app backend_api run --port 5001

# The API will be available at http://localhost:5001/api/chat
```

## 🔧 Extending ADK Implementation

The ADK implementation can be extended in several ways to enhance functionality:

### Adding New Tools

Create new travel-related tools by extending the `BaseTool` class in ADK:

```python
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext

class NewTravelTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="new_travel_tool",
            description="Description of what this tool does",
            parameters=[
                {"name": "param1", "type": "string", "description": "Parameter description"},
                # Add more parameters as needed
            ],
            required_parameters=["param1"]
        )
        
    def execute(self, tool_context: ToolContext, **kwargs) -> dict:
        # Implementation of the tool functionality
        return {"result": "processed data"}
```

Register the new tool with the agent in `agent.py`:

```python
new_tool = NewTravelTool()
agent = LlmAgent(
    # ... other parameters
    tools=[flight_tool, hotel_tool, travel_info_tool, new_tool]
)
```

### Adding New LLM Providers

To add a new LLM provider that supports OpenAI-compatible API, update the `llm_adapter.py` file:

```python
# Add to DEEPSEEK_MODELS or create a new provider config
NEW_PROVIDER_MODELS = {
    "chat": "model-name-chat",
    "coding": "model-name-coding"
}

# Define the API base URL
NEW_PROVIDER_API_BASE = "https://api.new-provider.com/v1"

# In create_adk_model function, add support for the new provider:
def create_new_provider_model(model_name):
    return openai_model.OpenAI(
        model=model_name,
        api_key=os.getenv("NEW_PROVIDER_API_KEY"),
        base_url=NEW_PROVIDER_API_BASE
    )
```

## 🐞 Troubleshooting

### ADK Web Interface Issues

**Problem**: ADK web interface fails to start

**Solutions**:
- Ensure you're in the `adk_travel_agent` directory when running `adk web`
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify ADK installation: `pip install google-adk --upgrade`

**Problem**: ADK agent doesn't respond correctly

**Solutions**:
- Check the API keys in your `.env` file
- Run with debug mode: `adk web --debug`
- Examine logs for error messages

### LLM Integration Issues

**Problem**: OpenAI SDK integration with DeepSeek fails

**Solutions**:
- Ensure OpenAI SDK is installed: `pip install openai`
- Verify your DeepSeek API key is correct
- Check that the DeepSeek API base URL is correct (https://api.deepseek.com/v1)
- Try using Groq via LiteLLM as a fallback

### Common Error Messages

- `Module not found`: Ensure all dependencies are installed from requirements.txt
- `API key not found`: Check your `.env` file contains all required API keys
- `Port already in use`: Close other applications using the port or specify a different port

## 🧩 System Architecture

### ADK Implementation Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        ADK Travel Agent                        │
└───────────────────────────────┬────────────────────────────────┘
                                │
            ┌─────────────────────────────────────────┐
            │           LLM Agent Framework           │
            └──────────────┬──────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                          │                                    │
▼                          ▼                                    ▼
┌─────────────────┐  ┌─────────────┐                     ┌────────────────┐
│  LLM Provider   │  │ Agent Tools │                     │ User Interfaces │
├─────────────────┤  ├─────────────┤                     ├────────────────┤
│  DeepSeek       │  │ FlightTool  │                     │  ADK Web UI    │
│  (via OpenAI    │  │ HotelTool   │                     │  (primary)     │
│   SDK)          │  │ InfoTool    │                     │                │
│                 │  │ SearchTool  │                     │  Streamlit    │
│  Groq           │  │             │                     │  (alternative) │
│  (via LiteLLM)  │  │             │                     │                │
└─────────────────┘  └─────────────┘                     └────────────────┘
```

### Component Flow

```
User Query → ADK Agent → Intent Recognition → Tool Selection → External API Calls → Response Generation → User
```

### Component Descriptions

| Component | Description |
|-----------|-------------|
| ADK Agent | Core component built with Google's Agent Development Kit (ADK) |
| LLM Provider | DeepSeek (primary, via OpenAI SDK) and Groq (fallback, via LiteLLM) |
| FlightTool | Tool for searching and comparing flight options |
| HotelTool | Tool for finding and filtering hotel accommodations |
| InfoTool | Tool for retrieving travel information about destinations |
| SearchTool | Tool for performing web searches for travel data |
| ADK Web UI | Built-in web interface provided by ADK framework |
| Streamlit UI | Alternative interactive web interface built with Streamlit components |
| Conversation Manager | Handles message history and context preservation (part of ADK Flow) |
| Intent Recognition | Identifies user intent from natural language queries |
| Data Extraction | Extracts parameters like locations, dates, and preferences |
| Search Manager | Coordinates search operations across different APIs |
| Response Generator | Creates coherent, helpful responses based on available data |

## 📝 Testing

> **All tests are currently passing** ✅ - The codebase has been thoroughly tested with unit tests for all components including security, error handling, and rate limiting.

### Test Structure

The test suite is organized to cover different aspects of the application:

```
tests/
├── integration/               # Integration tests
│   ├── test_chat_flow.py      # Tests for the chat flow (adapted for ADK/Streamlit)
│   ├── test_end_to_end_flow.py # End-to-end testing
│   ├── test_parameter_extraction_integration.py # Parameter extraction
│   ├── test_redis_state_integration.py # Redis state persistence
│   └── test_search_integration.py # Search functionality
├── unit/                      # Unit tests
│   ├── test_error_handling.py # Error handling and fallbacks
│   ├── test_input_validation.py # Input validation
│   └── test_rate_limiter.py   # Rate limiting (if applicable outside web framework)
├── test_enhanced_features.py  # Enhanced feature tests
├── test_flight_search.py      # Flight search tests
└── run_tests.py               # Test runner script
```

### Running Tests

To run the complete test suite:

```bash
# From the project root
python tests/run_tests.py
```

To run specific test categories:

```bash
# Run only integration tests
python tests/run_tests.py --type integration

# Run Streamlit-specific tests (if structured separately)
# Example: pytest tests/streamlit_tests/
```

### Test Coverage

| Component | Verification Method | Success Criteria |
|-----------|---------------------|------------------|
| State Definitions | Unit tests | Models can be instantiated with valid data |
| Parameter Extraction | Parameterized tests | Correctly extracts airport codes, dates, and preferences |
| LLM Integration | Mock API tests | Client handles responses and errors with proper recovery |
| Search Tools | Cached integration tests | Search queries return expected structure with efficient caching |
| Agent Logic | Unit & integration tests | Agents produce expected outputs and handle edge cases (using ADK) |
| Streamlit UI/App Logic | Unit tests / Streamlit `AppTest` | UI components render correctly, application logic functions as expected |
| Input Validation | Unit tests | Validates and sanitizes all user inputs correctly |
| Error Handling | Unit tests | Properly tracks errors and implements fallback mechanisms |
| Rate Limiting | Unit tests | Correctly limits request rates and handles exceeded limits |

## 🔧 Development

### Code Structure

The codebase follows a modular architecture adapted for Streamlit:

- **Streamlit App (`app.py`, `pages/`)**: Handles UI presentation and user interaction.
- **Agent Layer (ADK)**: Manages conversation flow and orchestration.
- **Service Layer**: Interfaces with external services (LLMs, search APIs).
- **Model Layer**: Defines data structures and state management.
- **Config Layer**: Manages application configuration.

### Key Technical Components

#### Session Management
- **State Persistence**: Using Redis for state persistence with configurable TTL
- **Efficient Storage**: JSON serialization for storing complex state objects
- **Recovery Mechanism**: Built-in state recovery for failed sessions

#### Security Features
- **Input Validation**: Pattern-based validation using regex for all user inputs
- **XSS Prevention**: HTML escaping to prevent cross-site scripting attacks
- **Rate Limiting**: Time-based request limiting to prevent abuse
- **Session Protection**: Secure session handling and validation

### Contributing

Contributions to the Travel Agent project are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass (`python tests/run_tests.py`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework
- [Agent Development Kit (ADK) Providers](link-to-adk-if-known) (replace if specific ADK is used)
- [Redis](https://redis.io/) for state management
- [DeepSeek](https://deepseek.ai/) and [Groq](https://groq.com/) for LLM APIs
- [Google Serper](https://serper.dev/) for search functionality

## 📬 Contact

For questions or support, please open an issue on the repository or contact the maintainers directly.

---

*Last updated: April 24, 2025*
