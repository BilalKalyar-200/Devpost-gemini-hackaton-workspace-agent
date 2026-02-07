import google.generativeai as genai
from config import config

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        print("[GEMINI] Client initialized")
    
    async def generate(self, prompt: str) -> str:
        """
        Send prompt to Gemini and get response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[GEMINI ERROR] {e}")
            return f"Error generating response: {str(e)}"
    
    async def generate_with_json(self, prompt: str) -> dict:
        """
        Request JSON response from Gemini
        """
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON, no markdown formatting."
        
        try:
            response = self.model.generate_content(json_prompt)
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            import json
            return json.loads(text.strip())
        except Exception as e:
            print(f"[GEMINI JSON ERROR] {e}")
            return {"error": str(e)}