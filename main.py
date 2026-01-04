#!/usr/bin/env python3
"""
Minimal Autonomous Agent Loop
Requires: Ollama installed locally (ollama.ai)
Run: ollama pull llama3.2  # or any other model
"""

import json
import requests
from datetime import datetime
from pathlib import Path

class AutonomousAgent:
    def __init__(self, goal, model="llama3.2", max_iterations=5):
        self.goal = goal
        self.model = model
        self.max_iterations = max_iterations
        self.storage_file = Path("agent_state.json")
        self.iteration = 0
        self.completed_tasks = []
        self.pending_tasks = []
        
    def call_llm(self, prompt):
        """Call local Ollama API"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None
    
    def save_state(self):
        """Save agent state to local JSON file"""
        state = {
            "goal": self.goal,
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks
        }
        self.storage_file.write_text(json.dumps(state, indent=2))
        print(f"💾 State saved to {self.storage_file}")
    
    def load_state(self):
        """Load agent state from local storage"""
        if self.storage_file.exists():
            state = json.loads(self.storage_file.read_text())
            self.iteration = state.get("iteration", 0)
            self.completed_tasks = state.get("completed_tasks", [])
            self.pending_tasks = state.get("pending_tasks", [])
            print(f"📂 Loaded previous state (iteration {self.iteration})")
            return True
        return False
    
    def generate_tasks(self):
        """Generate initial task list from goal"""
        prompt = f"""Goal: {self.goal}

Break this goal into 3-5 specific, actionable tasks. Return ONLY a JSON array of tasks.
Format: ["task 1", "task 2", "task 3"]

Tasks:"""
        
        response = self.call_llm(prompt)
        if not response:
            return ["Research the goal", "Create a plan", "Execute plan"]
        
        try:
            # Extract JSON array from response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != 0:
                tasks = json.loads(response[start:end])
                return tasks
        except:
            pass
        
        # Fallback: parse as lines
        lines = [line.strip().strip('"').strip("'").strip("-").strip() 
                 for line in response.split("\n") if line.strip()]
        return [line for line in lines if len(line) > 10][:5]
    
    def execute_task(self, task):
        """Execute a single task"""
        prompt = f"""Goal: {self.goal}
Current Task: {task}

Execute this task by providing a detailed response or solution. Be specific and actionable.

Response:"""
        
        response = self.call_llm(prompt)
        return response or "Task execution unclear"
    
    def evaluate_progress(self):
        """Evaluate overall progress toward goal"""
        completed_summary = "\n".join([
            f"- {t['task']}: {t['result'][:100]}..." 
            for t in self.completed_tasks[-3:]
        ])
        
        prompt = f"""Goal: {self.goal}

Completed tasks:
{completed_summary}

Pending tasks: {len(self.pending_tasks)}

Evaluate progress (0-100%) and determine if goal is achieved. 
Format: PROGRESS: [number]%, STATUS: [ACHIEVED/IN_PROGRESS/BLOCKED]

Evaluation:"""
        
        response = self.call_llm(prompt)
        
        # Parse progress
        progress = 0
        achieved = False
        if response:
            if "100%" in response or "ACHIEVED" in response.upper():
                progress = 100
                achieved = True
            else:
                # Try to extract percentage
                for word in response.split():
                    if "%" in word:
                        try:
                            progress = int(word.replace("%", ""))
                            break
                        except:
                            pass
        
        return progress, achieved, response
    
    def create_new_tasks(self):
        """Generate new tasks based on current progress"""
        if not self.completed_tasks:
            return []
        
        recent = "\n".join([
            f"- {t['task']}" for t in self.completed_tasks[-2:]
        ])
        
        prompt = f"""Goal: {self.goal}

Recently completed:
{recent}

What are the next 2-3 tasks needed to progress toward the goal? 
Return ONLY a JSON array: ["task 1", "task 2"]

Tasks:"""
        
        response = self.call_llm(prompt)
        if not response:
            return []
        
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
        except:
            pass
        
        return []
    
    def run(self):
        """Main agent loop"""
        print(f"\n🤖 Autonomous Agent Starting...")
        print(f"🎯 Goal: {self.goal}\n")
        
        # Try to load previous state
        resumed = self.load_state()
        
        # Generate initial tasks if starting fresh
        if not resumed and not self.pending_tasks:
            print("📋 Generating initial tasks...")
            self.pending_tasks = self.generate_tasks()
            print(f"Generated {len(self.pending_tasks)} tasks\n")
        
        # Main loop
        while self.iteration < self.max_iterations:
            self.iteration += 1
            print(f"\n{'='*60}")
            print(f"ITERATION {self.iteration}/{self.max_iterations}")
            print(f"{'='*60}\n")
            
            # Execute next task
            if self.pending_tasks:
                current_task = self.pending_tasks.pop(0)
                print(f"🔨 Executing: {current_task}")
                
                result = self.execute_task(current_task)
                self.completed_tasks.append({
                    "task": current_task,
                    "result": result,
                    "iteration": self.iteration
                })
                
                print(f"✅ Result: {result[:200]}...\n")
            
            # Evaluate progress
            print("📊 Evaluating progress...")
            progress, achieved, evaluation = self.evaluate_progress()
            print(f"Progress: {progress}%")
            print(f"Evaluation: {evaluation[:200]}...\n")
            
            # Check if goal achieved
            if achieved:
                print("🎉 Goal achieved!")
                self.save_state()
                break
            
            # Generate new tasks if needed
            if len(self.pending_tasks) < 2:
                print("🔄 Generating new tasks...")
                new_tasks = self.create_new_tasks()
                self.pending_tasks.extend(new_tasks)
                print(f"Added {len(new_tasks)} new tasks\n")
            
            print(f"📝 Pending tasks: {len(self.pending_tasks)}")
            for i, task in enumerate(self.pending_tasks[:3], 1):
                print(f"   {i}. {task}")
            
            # Save state after each iteration
            self.save_state()
        
        print(f"\n{'='*60}")
        print(f"🏁 Agent completed {self.iteration} iterations")
        print(f"✅ Completed {len(self.completed_tasks)} tasks")
        print(f"📋 Remaining tasks: {len(self.pending_tasks)}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Example usage
    goal = "Create a simple Python script that analyzes a text file for word frequency"
    
    agent = AutonomousAgent(
        goal=goal,
        model="llama3.2",  # Change to your installed model
        max_iterations=5
    )
    
    agent.run()
