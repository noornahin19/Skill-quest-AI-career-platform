"""
ai_service.py
--------------
Thin abstraction so the rest of the app never talks to a provider SDK
directly. Two modes, controlled by the AI_MODE env var:

  AI_MODE=demo (default) -> canned/local responses, no network calls,
                             safe for local dev and CI.
  AI_MODE=external        -> calls OpenAI or Gemini depending on which
                             API key is present.

Swapping providers means editing this file only.
"""

import os

AI_MODE = os.getenv("AI_MODE", "demo")


def generate_ai_response(prompt: str) -> str:
    if AI_MODE == "external":
        return _call_external_provider(prompt)
    return _demo_response(prompt)


def _demo_response(prompt: str) -> str:
    """
    Deterministic canned response so the app is fully usable without any
    API keys configured. Good enough for demos and local development.
    """
    lower = prompt.lower()
    if "score:" in lower or "score 0-100" in lower:
        return "SCORE: 72 | FEEDBACK: Solid structure — add a concrete example to strengthen it."
    return (
        "This is a demo-mode AI response. Set AI_MODE=external and provide "
        "OPENAI_API_KEY or GEMINI_API_KEY in .env to get real model output."
    )


def _call_external_provider(prompt: str) -> str:
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if openai_key:
        return _call_openai(prompt, openai_key)
    if gemini_key:
        return _call_gemini(prompt, gemini_key)

    # No key configured — fail soft rather than crash the request
    return _demo_response(prompt)


def _call_openai(prompt: str, api_key: str) -> str:
    import openai

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return response.choices[0].message.content or ""


def _call_gemini(prompt: str, api_key: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    response = model.generate_content(prompt)
    return response.text or ""
