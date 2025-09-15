class HighlightAgent:
    def extract(self, text: str):
        keywords = ["decide", "plan", "deadline", "assign", "action", "important", "deliverable", "risk"]
        sentences = [s.strip() for s in text.split('.')]
        return [s for s in sentences if any(k in s.lower() for k in keywords) and len(s) > 0]
