这是一个命令行AI助手，包括可以处理多模态文件（PNG，PDF等等），也有help系统助手，可以记录一定的对话历史，和创建临时文件或者本地文件，也可以显示本地所处时间戳。流式处理，
# AI Terminal Agent

A lightweight, highly available Command-Line Interface (CLI) application powered by Large Language Models (OpenAI API). Designed with enterprise-grade error handling and streaming capabilities.

## 💡 Why this project?
Standard API wrappers often fail under poor network conditions or suffer from high latency during long context generation. This project solves these issues by implementing a robust data pipeline and state management.

## ✨ Core Features
* **Streaming Output (流式解析):** Abandons traditional blocking requests. Responses are streamed character-by-character to the terminal, drastically reducing Time-To-First-Token (TTFT) and improving user experience.
* **Error Retry Mechanism (网络异常重试):** Built-in network jitter detection. Automatically retries failed requests with exponential backoff, ensuring uninterrupted service in unstable environments.
* **Context Persistence (上下文记忆):** Modular state management logic that locally caches dialogue history, enabling coherent multi-turn conversations.
* **System Logging:** Comprehensive runtime logging for easy debugging and API status tracking.

## 🛠 Tech Stack
- Python 3.x
- `openai` Python SDK
- `requests`

## 🚀 Usage

1. Clone the repo:
```bash
git clone https://github.com/shuiguodao111/AI-.git
cd AI-
Export your API Key:
code
Bash
export OPENAI_API_KEY="your-api-key-here"
Run the Agent:
code
Bash
python main.py
