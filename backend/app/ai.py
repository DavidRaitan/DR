import json
import logging
import urllib.error
import urllib.request
from typing import Optional

from .config import ACTIVE_PROVIDER, AI_ENABLED, ANTHROPIC_API_KEY, GEMINI_API_KEY, MODEL_CLAUDE, GEMINI_MODELS, GEMINI_TIMEOUT

log = logging.getLogger(__name__)


def _claude_text(system: str, user: str, max_tokens: int) -> Optional[str]:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=MODEL_CLAUDE, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text
    except Exception as e:
        log.warning("Claude text failed: %s", e)
        return None


def _claude_json(system: str, user: str, schema: dict, max_tokens: int) -> Optional[dict]:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=MODEL_CLAUDE, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        return json.loads(msg.content[0].text)
    except Exception as e:
        log.warning("Claude JSON failed: %s", e)
        return None


def _gemini_call(system: str, user: str, max_tokens: int, json_mode: bool) -> Optional[str]:
    gen = {"maxOutputTokens": max_tokens + 2048}
    if json_mode:
        gen["responseMimeType"] = "application/json"
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": gen,
    }).encode()
    for model in GEMINI_MODELS:
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            data=body,
            headers={"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY},
        )
        try:
            with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT) as resp:
                data = json.load(resp)
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts) or None
        except urllib.error.HTTPError as e:
            log.warning("Gemini %s returned %s", model, e.code)
            if e.code not in (404, 429, 500, 503):
                return None
        except Exception as e:
            log.warning("Gemini %s failed: %s", model, e)
    return None


def _gemini_text(system: str, user: str, max_tokens: int) -> Optional[str]:
    return _gemini_call(system, user, max_tokens, json_mode=False)


def _gemini_json(system: str, user: str, schema: dict, max_tokens: int) -> Optional[dict]:
    prompt = f"{user}\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(schema)}"
    text = _gemini_call(system, prompt, max_tokens, json_mode=True)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        log.warning("Gemini returned invalid JSON")
        return None


def generate_text(system: str, user: str, max_tokens: int = 800) -> Optional[str]:
    if not AI_ENABLED:
        return None
    if ACTIVE_PROVIDER == "claude":
        return _claude_text(system, user, max_tokens)
    if ACTIVE_PROVIDER == "gemini":
        return _gemini_text(system, user, max_tokens)
    return None


def generate_json(system: str, user: str, schema: dict, max_tokens: int = 1200) -> Optional[dict]:
    if not AI_ENABLED:
        return None
    if ACTIVE_PROVIDER == "claude":
        return _claude_json(system, user, schema, max_tokens)
    if ACTIVE_PROVIDER == "gemini":
        return _gemini_json(system, user, schema, max_tokens)
    return None


def provider_info() -> dict:
    return {
        "ai_enabled": AI_ENABLED,
        "provider": ACTIVE_PROVIDER,
        "model": MODEL_CLAUDE if ACTIVE_PROVIDER == "claude" else (
            GEMINI_MODELS[0] if ACTIVE_PROVIDER == "gemini" else None
        ),
    }
