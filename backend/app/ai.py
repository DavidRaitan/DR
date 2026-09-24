import json
import logging
from typing import Optional

from .config import ACTIVE_PROVIDER, AI_ENABLED, ANTHROPIC_API_KEY, GEMINI_API_KEY, MODEL_CLAUDE, MODEL_GEMINI

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


def _gemini_text(system: str, user: str, max_tokens: int) -> Optional[str]:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=MODEL_GEMINI, system_instruction=system,
            generation_config={"max_output_tokens": max_tokens},
        )
        return model.generate_content(user).text
    except Exception as e:
        log.warning("Gemini text failed: %s", e)
        return None


def _gemini_json(system: str, user: str, schema: dict, max_tokens: int) -> Optional[dict]:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        prompt = f"{user}\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        model = genai.GenerativeModel(
            model_name=MODEL_GEMINI, system_instruction=system,
            generation_config={"max_output_tokens": max_tokens, "response_mime_type": "application/json"},
        )
        return json.loads(model.generate_content(prompt).text)
    except Exception as e:
        log.warning("Gemini JSON failed: %s", e)
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
            MODEL_GEMINI if ACTIVE_PROVIDER == "gemini" else None
        ),
    }
