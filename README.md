# 🚀 AI Meeting Summarizer + Gemini Chatbot

AI Meeting Summarizer is an intelligent dashboard that transcribes, summarizes, and analyzes meeting audio files.  
It helps teams stay aligned by generating transcripts, summaries, translations, audio narrations, and AI-powered insights — all in one place.

---

## ✨ Features

🎙️ **Audio Upload & Transcription**  
- Upload meeting recordings (supports long audio via chunking).  
- Automatically detects spoken language.  
- Generates clean transcript with copy & download options.

📝 **AI-Powered Summary**  
- Extracts key summary points, action items, decisions, and risks.  
- Performs sentiment analysis of the meeting.  
- Download summary as `.txt` file.

🌐 **Translation**  
- Translate summaries into multiple languages (English, Hindi, Tamil, Kannada, Telugu, Bengali, French, Spanish).

🔊 **Text-to-Speech (TTS)**  
- Converts AI summaries into natural-sounding speech.  
- Handles long text by splitting into safe chunks.  
- Download generated audio with timestamped filenames.

🤖 **AI Insights (Gemini API)**  
- Auto-generate intelligent insights from transcripts.  
- Ask custom chatbot-like questions about the meeting.

📤 **Team Notifications**  
- Slack Integration → auto-posts meeting summaries to channels.  
- Email Integration → send reports to multiple recipients.

📂 **Export Options**  
- Download transcripts and summaries as `.txt`.  
- Export audio summary as `.mp3`.

🎨 **Professional Dashboard (Gradio UI)**  
- Clean layout with logo branding.  
- Dynamic UI with status updates during processing.  
- Easy-to-use for non-technical users.

---

## ✅ Tech Stack

- **Frontend**: Gradio (custom dashboard with tabs & dynamic components)  
- **Speech-to-Text**: OpenAI Whisper (via TranscriberAgent)  
- **NLP & Summarization**: Custom LLM pipeline (LLMNLP)  
- **AI Insights**: Google Gemini API  
- **Text-to-Speech (TTS)**: gTTS + Pydub for audio chunking  
- **Integrations**: Slack Webhooks, SMTP Email  
- **Other Tools**: Python, dotenv, datetime, os, requests

---

##📂 Project Structure

 - AI_MEETING_SUMMARIZER/
 - ├── agents/                     # Core processing logic
 -│   ├── __init__.py
 -│   ├── highlighter.py          # Extracts summary bullets, actions, etc.
 -│   ├── llm_nlp.py              # NLP pipeline for analysis & translation
 -│   └── transcriber.py          # Whisper-based audio transcription
 -│
 -├── integrations/               # Integrations for external services
 -│   ├── __init__.py
 -│   ├── emailer.py              # SMTP email sender
 -│   ├── gemini_api.py           # Calls Gemini API for AI insights
 -│   └── slack_notify.py         # Posts messages to Slack channels
 -│
 -├── outputs/                    # Generated output files (audio, text)
 -│   └── (generated files: .mp3, .txt)
│
├── assets/                     # Static assets (e.g., logo)
│   └── logo.png
│
├── tests/                      # Test scripts
│   └── (test_slack.py, test_email.py, etc.)
│
├── .env                        # Environment variables (excluded from Git)
├── .gitignore                  # Files to ignore in git
├── main.py                     # Entry point: Launches Gradio UI
├── README.md                   # Project description & instructions
├── requirements.txt            # List of dependencies
└── LICENSE                     # (Optional) License file



---


# 🚀 Installation & Setup

1.**Clone the repository**

```bash
git clone https://github.com/your-username/AI_MEETING_SUMMARIZER.git
cd AI_MEETING_SUMMARIZER


2. **Create & activate virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate

3️. **Install dependencies**
   ```bash
   pip install -r requirements.txt

 4️. **Configure Environment Variables**
    **Create a `.env` file in the project root with the following    variables:**
    ```bash
    GEMINI_API_KEY=your_gemini_api_key
    SMTP_SENDER_EMAIL=your_email@gmail.com
    SMTP_APP_PASSWORD=your_app_password
    EMAIL_RECIPIENTS=email1@gmail.com,email2@gmail.com
    DEFAULT_TARGET_LANG=en

▶ **Running the App**
   ```bash
   python main.py



