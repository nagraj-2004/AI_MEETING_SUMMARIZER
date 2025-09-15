import os
from dotenv import load_dotenv
import gradio as gr
from gtts import gTTS
from datetime import datetime
from pydub import AudioSegment

# Agents & integrations
from agents.transcriber import TranscriberAgent
from agents.llm_nlp import LLMNLP
from agents.highlighter import HighlightAgent
from integrations.slack_notify import send_slack_message
from integrations.emailer import send_email, RECIPIENTS
from integrations.gemini_api import get_gemini_response

load_dotenv()

# Agents
transcriber = TranscriberAgent(model_name=os.getenv("WHISPER_MODEL", "base"))
nlp = LLMNLP()
highlighter = HighlightAgent()

# Config
LANGS = ["hi", "ta", "kn", "te", "bn", "fr", "es", "en"]
DEFAULT_LANG = os.getenv("DEFAULT_TARGET_LANG", "en")


# 🔹 Helper: split audio into safe chunks
def chunk_audio_file(audio_path, chunk_length_ms=60_000):
    """Split audio into fixed chunks (default 60s)."""
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = f"{audio_path}_chunk_{i // chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


# 🔹 Helper: safe TTS with chunking
def chunked_tts(text, lang="en", max_chars=2500, out_path="outputs/summary_audio.mp3"):
    """Split long text into safe chunks for gTTS and merge into one MP3."""
    os.makedirs("outputs", exist_ok=True)
    parts = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    audio_segments = []

    for idx, part in enumerate(parts):
        tts = gTTS(part, lang=lang)
        temp_path = f"outputs/tmp_tts_{idx}.mp3"
        tts.save(temp_path)
        audio_segments.append(AudioSegment.from_mp3(temp_path))

    combined = sum(audio_segments)
    combined.export(out_path, format="mp3")
    return out_path


def pipeline_with_status(audio_path, target_lang, custom_query, extra_emails):
    status_msgs = []

    def update_status(msg):
        status_msgs.append(msg)
        return "\n".join(status_msgs)

    # 1. Check input
    if not audio_path:
        return "", "", "No audio uploaded", "", None, "(No auto insight)", "(No chatbot query)", update_status("❌ No audio uploaded")

    # 2. Language detection
    update_status("⏳ Detecting language...")
    source_lang = transcriber.detect_language(audio_path)
    update_status(f"🗣️ Detected language: {source_lang}")

    # 3. Transcription with chunking
    update_status("🎙️ Transcribing audio (chunked)...")
    try:
        chunks = chunk_audio_file(audio_path, chunk_length_ms=60_000)
        transcripts = []
        for ch in chunks:
            result = transcriber.transcribe(ch, language=source_lang)
            transcripts.append(result.get("text", ""))
        transcript = " ".join(transcripts).strip()
    except Exception as e:
        return source_lang, "", "Error in transcription", "", None, "(No auto insight)", "(No chatbot query)", update_status(f"❌ Transcription error: {e}")

    if not transcript:
        return source_lang, "", "Empty transcript", "", None, "(No auto insight)", "(No chatbot query)", update_status("❌ Transcript is empty")

    # 4. AI insights
    update_status("🤖 Generating AI insights...")
    gemini_auto_response = get_gemini_response(transcript)
    gemini_chat_response = get_gemini_response(custom_query) if custom_query.strip() else "(No custom query provided)"

    # 5. NLP analysis
    update_status("🔍 Analyzing transcript with NLP...")
    analysis = nlp.analyze(transcript, target_lang)
    summary_bullets = analysis.get("summary", [])
    action_items = analysis.get("actions", [])
    decisions = analysis.get("decisions", [])
    risks = analysis.get("risks", [])
    sentiment = analysis.get("sentiment", "neutral")

    # ✅ FIX: no more transcript[:2000], use full transcript
    translated = (
        analysis.get("translation")
        or (" ".join(summary_bullets) if summary_bullets else transcript)
    )

    if isinstance(translated, dict):
        translated = translated.get(target_lang) or translated.get("en") or str(translated)

    # 6. TTS with chunking
    update_status("🔊 Generating TTS summary audio...")
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tts_path = os.path.join("outputs", f"summary_audio_{timestamp}.mp3")

    try:
        tts_path = chunked_tts(translated, lang=target_lang if target_lang else "en", out_path=tts_path)
    except Exception as e:
        update_status(f"⚠️ TTS error: {e}")
        tts_path = None

    # 7. Build final summary text
    text_block = ["**Meeting Summary**"] + [f"• {b}" for b in summary_bullets]
    text_block += ["\n**Action Items**"] + ([f"- {a}" for a in action_items] if action_items else ["- (none)"])
    text_block += ["\n**Decisions**"] + ([f"- {d}" for d in decisions] if decisions else ["- (none)"])
    text_block += ["\n**Risks**"] + ([f"- {r}" for r in risks] if risks else ["- (none)"])
    text_block.append(f"\n**Sentiment:** {sentiment}")
    text_block.append("\n**Gemini Auto Insight:**")
    text_block.append(gemini_auto_response)
    share_text = "\n".join(text_block)

    # 8. Notifications
    update_status("📤 Sending Slack and Email notifications...")

    # Slack
    try:
        send_slack_message(share_text)
        update_status("✅ Slack message sent.")
    except Exception as e:
        update_status(f"⚠️ Slack error: {e}")

    # Email
    try:
        final_recipients = RECIPIENTS.copy() if RECIPIENTS else []
        if extra_emails:
            emails = [e.strip() for e in extra_emails.split(",") if "@" in e]
            final_recipients.extend(emails)
        if final_recipients:
            send_email(subject="Meeting Summary", body=share_text, recipients=final_recipients)
            update_status(f"✅ Email sent to: {', '.join(final_recipients)}")
        else:
            update_status("⚠️ No recipients found, email not sent.")
    except Exception as e:
        update_status(f"⚠️ Email error: {e}")

    update_status("🎉 Processing complete!")

    return (
        source_lang,
        transcript,
        share_text,
        translated,
        tts_path,
        gemini_auto_response,
        gemini_chat_response,
        "\n".join(status_msgs),
    )

# Gradio UI
with gr.Blocks(css="""
    footer {visibility: hidden}
    #logo img {max-height: 120px; object-fit: contain;}  /* ✅ show full logo */
    .gr-button {background: #2563eb !important; color: white !important; font-weight: bold;}
""") as ui:

    # 🔹 Header with Logo + Title
    with gr.Row():
        with gr.Column(scale=1):
            if os.path.exists("assets/logo.png"):
                gr.Image(
                    value="assets/logo.png",
                    elem_id="logo",
                    show_label=False,
                    type="filepath",
                    interactive=False   # ✅ prevents cropping UI
                )
        with gr.Column(scale=4):
            gr.Markdown("## 🚀 AI Meeting Summarizer\n Dashboard with Insights, Audio & Export")

    with gr.Row():
        # 📥 Input Panel
        with gr.Column(scale=1):
            audio_input = gr.Audio(label="🎙️ Upload Meeting Audio", type="filepath")
            lang_input = gr.Dropdown(LANGS, value=DEFAULT_LANG, label="🌍 Target Language")
            custom_query = gr.Textbox(label="💡 Ask AI Insight", placeholder="Type your question here...")
            extra_emails = gr.Textbox(label="📧 Extra Emails", placeholder="Enter emails separated by commas")
            submit_btn = gr.Button("🔎 Process Audio", variant="primary")

        # 📤 Output Panel
        with gr.Column(scale=2):
            status_display = gr.Markdown("⏳ Waiting for input...")

            with gr.Tab("📄 Transcript"):
                output_lang = gr.Textbox(label="Detected Language", interactive=False)
                output_transcript = gr.Textbox(
                    label="Transcript",
                    lines=5,    
                    max_lines=30,  # expands dynamically
                    interactive=False,
                    show_copy_button=True
                )
                download_transcript = gr.File(label="⬇️ Download Transcript")

            with gr.Tab("📝 Summary"):
                output_summary = gr.Markdown()
                download_summary = gr.File(label="⬇️ Download Summary")

            with gr.Tab("🌐 Translation"):
                output_translated = gr.Textbox(
                    label="Translated Summary",
                    lines=10,
                    interactive=False,
                    show_copy_button=True
                )

            with gr.Tab("🔊 Audio Summary"):
                output_tts = gr.Audio(label="Download Summary Audio", type="filepath")

            with gr.Tab("🤖 AI Insights"):
                output_auto = gr.Textbox(label="Gemini Auto Insight", lines=5, interactive=False)
                output_chat = gr.Textbox(label="Gemini Chatbot Response", lines=5, interactive=False)

    # 🔗 Helper to save files
    def save_files(lang, transcript, summary):
        """Save transcript & summary as downloadable files."""
        os.makedirs("outputs", exist_ok=True)
        ts_path, sm_path = None, None
        if transcript:
            ts_path = os.path.join("outputs", "transcript.txt")
            with open(ts_path, "w", encoding="utf-8") as f:
                f.write(transcript)
        if summary:
            sm_path = os.path.join("outputs", "summary.txt")
            with open(sm_path, "w", encoding="utf-8") as f:
                f.write(summary)
        return ts_path, sm_path

    # 🔗 Button actions
    submit_btn.click(
        fn=pipeline_with_status,
        inputs=[audio_input, lang_input, custom_query, extra_emails],
        outputs=[
            output_lang,
            output_transcript,
            output_summary,
            output_translated,
            output_tts,
            output_auto,
            output_chat,
            status_display,
        ],
    ).then(
        fn=save_files,
        inputs=[output_lang, output_transcript, output_summary],
        outputs=[download_transcript, download_summary],
    )

if __name__ == "__main__":
    ui.launch()
