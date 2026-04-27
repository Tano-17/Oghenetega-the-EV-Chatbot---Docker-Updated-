import json
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (API Key) from .env file
load_dotenv()

class PersonalityBot:
    def __init__(self, history_file="chat_history.json"):
        self.history_file = history_file
        self.history = []
        self.total_tokens_used = 0
        
        # 1. Define the Bot's Personality (System Prompt)
        self.system_prompt = """
        You are Oghenetega, an enthusiastic, high-energy expert on all things electric vehicles (EVs).
        You love talking about battery technology, charging networks, motors, and EV models.
        You occasionally use car-related puns (like 'let's accelerate' or 'you're fully charged').
        Keep your answers relatively concise but very knowledgeable.
        """
        
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("System Error: GEMINI_API_KEY not found in .env file.")
            sys.exit(1)
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=self.system_prompt
        )
        
        self.load_history()
        self.start_new_chat_session()

    def start_new_chat_session(self):
        """Initializes the Gemini chat session with existing history."""
        gemini_history = []
        for msg in self.history:
            # Map our roles to Gemini's expected roles
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        self.chat_session = self.model.start_chat(history=gemini_history)

    def load_history(self):
        """Stretch Goal: Load conversation history from a JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                print(f"System: Loaded {len(self.history)} previous messages.")
            except Exception as e:
                print(f"System Error loading history: {e}")

    def save_history(self):
        """Stretch Goal: Save conversation history to a JSON file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"System Error saving history: {e}")

    def reset_history(self):
        """Core Requirement: Clear history."""
        self.history = []
        self.save_history()
        self.start_new_chat_session()
        print("\n[System: Conversation history has been cleared (Memory wiped).]")

    def summarise_history(self):
        """Stretch Goal: Summarize the conversation so far."""
        if not self.history:
            print("\n[System: No history to summarise.]")
            return
            
        print("\n[System: Summarising conversation...]")
        try:
            summary_prompt = "Briefly summarize this conversation in a couple of sentences:\n" + str(self.history)
            # Generate summary outside of the main chat session so it doesn't pollute history
            summary_response = self.model.generate_content(summary_prompt)
            print(f"\n[Summary: {summary_response.text.strip()}]\n")
        except Exception as e:
            print(f"[System Error summarising: {e}]")

    def generate_response(self, user_input):
        """Handles the AI API call, memory, token tracking, and streaming."""
        # 1. Add user message to local history
        self.history.append({"role": "user", "content": user_input})
        
        try:
            # 2 & 3. API Call with Streaming
            response_stream = self.chat_session.send_message(user_input, stream=True)
            
            print(f"\nOghenetega: ", end="", flush=True)
            full_response = ""
            for chunk in response_stream:
                text = chunk.text
                # Some API versions return the full accumulated text instead of just the delta.
                # This checks if it's accumulating and only prints the new part.
                if text.startswith(full_response):
                    print(text[len(full_response):], end="", flush=True)
                    full_response = text
                else:
                    print(text, end="", flush=True)
                    full_response += text
            print() # Print new line when streaming finishes
            
            # 4. Token Tracking
            if response_stream.usage_metadata:
                self.total_tokens_used += response_stream.usage_metadata.total_token_count
            
            # 5. Save assistant response
            self.history.append({"role": "assistant", "content": full_response})
            self.save_history()
            
        except Exception as e:
            print(f"\n[API Error: Something went wrong - {e}]. Let's try again.")
            self.history.pop() # Remove failed user input from memory so it doesn't break future calls

    def chat_loop(self):
        print("===================================================")
        print(" Welcome to Oghenetega, the EV Whiz Bot! ")
        print(" Commands: /quit, /reset, /summarise")
        print("===================================================\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['/quit', 'exit']:
                    print("Oghenetega: Plugging back into the charging station. Catch you later!")
                    break
                elif user_input.lower() == '/reset':
                    self.reset_history()
                    continue
                elif user_input.lower() == '/summarise':
                    self.summarise_history()
                    continue
                
                # Generate response (Streaming handles the printing)
                self.generate_response(user_input)
                
                # Token tracking display
                print(f"\n[System: Total tokens used this session: {self.total_tokens_used}]\n")
                
            except KeyboardInterrupt:
                print("\n[System: Interrupted. Exiting...]")
                break
            except Exception as e:
                print(f"\n[System Error: {e}]. Let's try again.")

if __name__ == "__main__":
    bot = PersonalityBot()
    bot.chat_loop()
