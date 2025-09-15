# import whisper

# class TranscriberAgent:
#     def __init__(self, model_name: str = "base"):
#         self.model = whisper.load_model(model_name)
#         self.detected_lang = "en"

#     def transcribe(self, audio_path: str) -> str:
#         result = self.model.transcribe(audio_path)
#         self.detected_lang = result.get("language", "en")
#         return result.get("text", "").strip()


# agents/transcriber.py
import whisper
import os
from typing import Dict, Optional

class TranscriberAgent:
    """
    Loads a Whisper model once. Provides:
      - detect_language(audio_path) -> language code (e.g. 'en')
      - transcribe(audio_path, language=None) -> dict with text, language, segments
    """
    def __init__(self, model_name: str = "base"):
        # choice: "tiny", "base", "small", "medium", "large"
        # use smaller models for faster startup during dev
        print(f"Loading Whisper model: {model_name} ...")
        self.model = whisper.load_model(model_name)
        self.detected_lang = "en"

    def detect_language(self, audio_path: str) -> str:
        """
        Returns a language code (e.g. 'en', 'hi', 'es') using Whisper's detect_language.
        """
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        # model.detect_language returns (lang, probs) in some versions; handle both shapes.
        try:
            lang_probs = self.model.detect_language(mel)
            # some versions return (lang, probs); some return probs dict
            if isinstance(lang_probs, tuple) and len(lang_probs) == 2:
                _, probs = lang_probs
            else:
                probs = lang_probs
            detected = max(probs, key=probs.get)
        except Exception:
            # fallback: transcribe a short chunk and trust result language field
            result = self.model.transcribe(audio_path, verbose=False)
            detected = result.get("language", "en")
        self.detected_lang = detected
        return detected

    def transcribe(self, audio_path: str, language: Optional[str] = None, task: str = "transcribe") -> Dict:
        """
        Transcribe the audio. If language is provided, pass it to Whisper to force that language.
        Returns: {"text": str, "language": str, "segments": list}
        """
        kwargs = {}
        if language:
            kwargs["language"] = language
            kwargs["task"] = task

        result = self.model.transcribe(audio_path, **kwargs)
        text = result.get("text", "").strip()
        lang = result.get("language", language or self.detected_lang or "en")
        segments = result.get("segments", [])
        self.detected_lang = lang
        return {"text": text, "language": lang, "segments": segments}
