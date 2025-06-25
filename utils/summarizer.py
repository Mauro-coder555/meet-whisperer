# utils/summarizer.py
from transformers import pipeline

# Pipe se crea una sola vez (lazy-load en la 1ª llamada)
_summer = None
def _get_pipe():
    global _summer
    if _summer is None:
        _summer = pipeline(
            "summarization",
            model="google/mt5-small",      # multilingüe, liviano
            tokenizer="google/mt5-small",
            framework="pt",
            device=0 if torch.cuda.is_available() else -1,
        )
    return _summer

def summarize(text: str, max_words: int = 120) -> str:
    pipe = _get_pipe()
    summary = pipe(
        text,
        max_length=max_words,
        min_length=max_words // 4,
        do_sample=False,
    )[0]["summary_text"]
    return summary.strip()
