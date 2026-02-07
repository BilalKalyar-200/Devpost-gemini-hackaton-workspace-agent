from google import genai
from google.genai import types
from config import config
import json

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash" 
        self.quota_exceeded = False
        print(f"[GEMINI] Client initialized with {self.model}")
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate with enhanced context"""
        try:
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            self.quota_exceeded = False
            return response.text
        
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "resource" in error_str:
                self.quota_exceeded = True
                print("[GEMINI] Quota exceeded - using fallback")
                return None
            print(f"[GEMINI ERROR] {e}")
            return None
    
    async def generate_with_json(self, prompt: str, system_prompt: str = None) -> dict:
        """Generate JSON with better error handling - COMPATIBILITY METHOD"""
        return await self.generate_structured(prompt, system_prompt)
    
    async def generate_structured(self, prompt: str, system_prompt: str = None) -> dict:
        """Generate JSON with better error handling"""
        json_prompt = f"""{prompt}

CRITICAL: You MUST respond with valid JSON only. No markdown, no explanations, just raw JSON.
Format your response as a proper JSON object."""

        try:
            response = await self.generate(json_prompt, system_prompt)
            
            if not response:
                return {"error": "API unavailable", "fallback": True}
            
            # Clean response
            text = response.strip()
            
            # Remove markdown
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            
            if text.endswith("```"):
                text = text[:-3]
            
            # Parse JSON
            return json.loads(text.strip())
        
        except json.JSONDecodeError as e:
            print(f"[GEMINI] JSON parse error: {e}")
            print(f"[GEMINI] Response was: {text[:200]}")
            return {
                "urgent": [],
                "important": [],
                "low_priority": [],
                "risks": [],
                "one_sentence_summary": "Unable to analyze data at this time.",
                "error": "JSON parse failed",
                "fallback": True
            }
        except Exception as e:
            print(f"[GEMINI ERROR] {e}")
            return {
                "urgent": [],
                "important": [],
                "low_priority": [],
                "risks": [],
                "one_sentence_summary": "Error during analysis.",
                "error": str(e),
                "fallback": True
            }