import os
import json
from typing import Dict
import google.generativeai as genai

# OpenAI (optional fallback)
try:
    from openai import OpenAI
    _has_openai = True
except Exception:
    _has_openai = False

SYSTEM_PROMPT = (
    "You are an AI meeting summarizer.\n"
    "1) Summarize the meeting into 3–5 bullet points.\n"
    "2) Extract key action items.\n"
    "3) List any decisions made.\n"
    "4) Identify risks.\n"
    "5) Provide a fluent translation of the summary in the target language.\n"
    "6) Perform sentiment analysis (positive, neutral, negative).\n"
    "Respond ONLY in valid JSON with keys: summary, actions, decisions, risks, translation, sentiment."
)

USER_TEMPLATE = (
    "Meeting transcript:\n"
    "{{TRANSCRIPT}}\n\n"
    "Target language: {{LANG}}"
)

class LLMNLP:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.provider = "gemini"
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        elif self.openai_key and _has_openai:
            self.provider = "openai"
            self.openai_client = OpenAI(api_key=self.openai_key)
            self.openai_model = "gpt-4o-mini"
        else:
            raise RuntimeError("No LLM provider configured. Set GEMINI_API_KEY or OPENAI_API_KEY in .env")

    def analyze(self, transcript: str, target_lang: str) -> Dict:
        user = USER_TEMPLATE.replace("{{TRANSCRIPT}}", transcript[:25000]).replace("{{LANG}}", target_lang)

        if self.provider == "gemini":
            resp = self.gemini_model.generate_content([
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "user", "parts": [user]},
            ])
            text = resp.text
        else:  # OpenAI
            msg = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ]
            resp = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=msg,
                temperature=0.2,
            )
            text = resp.choices[0].message.content

        # Parse JSON safely
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start = text.find('{')
            end = text.rfind('}')
            data = json.loads(text[start:end+1])
        return data
