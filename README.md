# Autonomous-Agent-Loop
A minimal autonomous agent loop using Python + a free/open-source LLM + local storage. Start with Goal → Task list → Execute → Evaluate → Create new tasks → Repeat. No cloud, no paid APIs.


I've created a minimal autonomous agent loop that runs completely locally! Here's what you need to know:
Setup

Install Ollama (free, open-source LLM runtime):

bash   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from ollama.ai

Pull a model:

bash   ollama pull llama3.2        # Recommended: fast, capable
   # or: ollama pull mistral
   # or: ollama pull phi3

Install Python dependency:

bash   pip install requests
How It Works
The agent implements the exact loop you requested:

Goal → Define what to achieve
Task List → LLM breaks goal into actionable tasks
Execute → Run each task through the LLM
Evaluate → Assess progress (0-100%)
Create New Tasks → Generate next steps based on what's done
Repeat → Loop until goal achieved or max iterations

Features

✅ 100% Local - No cloud services, no API keys
💾 Persistent Storage - Saves state to agent_state.json
🔄 Resume Support - Can continue from where it left off
🎯 Goal-Oriented - Stays focused on the objective
📊 Progress Tracking - Evaluates completion percentage

Run It
bashpython autonomous_agent.py
Change the goal variable in the script to whatever you want the agent to accomplish!
