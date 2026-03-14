import os
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime

HISTORY_FILE = "prompt_history.json"

def save_to_history(intent, optimized_prompt):
    history_data = []
    
    # Load existing history if it exists
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history_data = json.load(f)
            except:
                history_data = []

    # Add new entry
    history_data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "intent": intent,
        "prompt": optimized_prompt[:50] + "..." # Save a snippet for the table
    })

    # Save back to file
    with open(HISTORY_FILE, "w") as f:
        json.dump(history_data, f, indent=4)

load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def optimize_intent(intent: str):
    system_instruction = (
        "You are an expert Prompt Engineer. "
        "Rewrite the user's casual intent into a professional, structured LLM prompt. "
        "Return ONLY the final prompt."
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # One of Groq's fastest/best models
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": intent}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        if "429" in str(e):
            return "⚠️ [Groq Rate Limit] Too many requests! Wait a moment."
        return f"❌ Groq Error: {str(e)}"