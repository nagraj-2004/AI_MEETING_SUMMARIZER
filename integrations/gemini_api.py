import os
import google.generativeai as genai

def get_gemini_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("⚠️ Gemini API error:", e)
        return "(Gemini API failed)"
