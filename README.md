# 🤖 LangGraph Chatbot

A multi-conversation AI chatbot built with **LangGraph**, **Groq**, and **Streamlit**. Chats are streamed token-by-token, and every conversation is saved in SQLite, so you can close the app and pick up right where you left off.

The repo also includes an experimental version with **tool calling** (web search, calculator) and **MCP (Model Context Protocol)** server integration.

---

## ✨ Features

- 💬 **Streaming responses**: replies appear in real time in the Streamlit chat UI
- 🗂️ **Multiple conversations**: start a new chat anytime and switch between old ones from the sidebar
- 💾 **Persistent memory**: conversation state is checkpointed to SQLite via LangGraph's `SqliteSaver`
- ⚡ **Fast inference**: powered by Groq (`openai/gpt-oss-20b`)
- 🛠️ **Tools (experimental)**: DuckDuckGo web search, a calculator, and tools from a remote MCP server
- 🔍 **LangSmith-ready**: each turn is tagged with `thread_id` metadata and a `run_name` for tracing

---

## 🏗️ Architecture

```
┌──────────────────┐      ┌─────────────────────────┐      ┌──────────────┐
│  frontend.py     │ ───▶ │  backend.py             │ ───▶ │  Groq LLM    │
│  (Streamlit UI)  │      │  (LangGraph StateGraph) │      │  gpt-oss-20b │
└──────────────────┘      └───────────┬─────────────┘      └──────────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │  chatbot.db     │
                             │  (SQLite)       │
                             └─────────────────┘
```

**Graph flow (`backend.py`):** `START → chatbot → END`

**Graph flow with tools (`chatbot.py`):** `START → chatbot ⇄ tools → END` (the LLM decides when to call a tool via `tools_condition`)

---

## 📁 Project Structure

```
.
├── frontend.py     # Streamlit UI: sidebar, thread switching, streaming chat
├── backend.py      # LangGraph graph + SQLite checkpointer + thread listing
├── chatbot.py      # Experimental: tools (search, calculator) + MCP client
├── chatbot.db      # Auto-created SQLite database (not committed)
├── .env            # API keys (not committed)
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install streamlit langgraph langgraph-checkpoint-sqlite langchain langchain-core \
            langchain-groq langchain-community langchain-mcp-adapters \
            duckduckgo-search python-dotenv
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here

# Only needed for chatbot.py (MCP server)
MCP_AUTH_TOKEN=your_mcp_token_here

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
```

Get a free Groq API key from [console.groq.com](https://console.groq.com).

### 5. Run the app

```bash
streamlit run frontend.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

---

## 🧪 Running the Tools + MCP Version

`chatbot.py` is a standalone script that demonstrates tool calling and MCP:

```bash
python chatbot.py
```

It connects to an MCP server, loads its tools, and asks the agent a sample question. Tools available:

| Tool | Description |
|------|-------------|
| `DuckDuckGoSearchRun` | Search the web for up-to-date information |
| `calculator` | Basic arithmetic: `add`, `sub`, `mul`, `div` |
| MCP tools | Loaded dynamically from the remote MCP server |

---

## 🧠 How It Works

1. **New chat**: each conversation gets a unique `thread_id` (UUID).
2. **Sending a message**: the user's message is passed to the LangGraph graph with that `thread_id`, so the checkpointer loads and saves the correct history.
3. **Streaming**: `chatbot.stream(..., stream_mode="messages")` yields chunks that Streamlit renders live with `st.write_stream`.
4. **Switching chats**: clicking a thread in the sidebar reloads its messages from SQLite via `chatbot.get_state(...)`.
5. **Restart-proof**: on startup, all past thread IDs are read from the checkpoint database.

---

## 🛠️ Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph): stateful agent workflows
- [LangChain](https://github.com/langchain-ai/langchain): LLM abstractions and tools
- [Groq](https://groq.com): fast LLM inference
- [Streamlit](https://streamlit.io): chat UI
- [SQLite](https://www.sqlite.org): conversation persistence
- [MCP](https://modelcontextprotocol.io): external tool integration

---

## 🗺️ Roadmap

- [ ] Integrate tools and MCP into the Streamlit app
- [ ] Auto-generate conversation titles instead of showing raw thread IDs
- [ ] RAG over uploaded documents
- [ ] Delete / rename conversations
- [ ] Dockerize the app

---

## 🔒 Security Note

Never commit your `.env` file or `chatbot.db`. Add them to `.gitignore`:

```gitignore
.env
chatbot.db
__pycache__/
venv/
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## 👤 Author

**Aditya Mali**
B.Tech CSE, NIT Jalandhar

- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)

## 📄 License

This project is licensed under the MIT License.
