"""Prompt building helpers for OpenAI payload construction."""

from __future__ import annotations

from copy import deepcopy

__all__ = [
    "SYSTEM_INSTRUCTIONS",
    "JSON_SCHEMA_NAME",
    "RESPONSE_JSON_SCHEMA",
    "build_response_object_schema",
    "build_text_format_config",
    "build_user_prompt",
]

SYSTEM_INSTRUCTIONS = (
    "You convert raw OCR menu text into structured menu data. Follow these rules strictly: "
    "1) Extract distinct dish names from the text (ignore prices and merge near-duplicates). "
    "2) Preserve the original dish wording in `original_name` and translate it into the requested "
    "output language for `translated_name`. "
    "3) For each dish, write a short descriptive sentence in the output language that includes "
    "typical ingredients, preparation method, and expected flavour profile (for example sweet, "
    "savory, spicy). Use natural phrasing rather than bullet lists."
    "4) Extract (meat or vegetable type) and (flavor, spicy, sweet, salty, etc.) from the text that describe the dish as tags. Tags should be short and concise, just one word, and in the translated language. "
    "5) Return only a JSON array and ensure every object contains `original_name`, `translated_name`, "
    "`description` and `tags`. No extra commentary or keys."
)

JSON_SCHEMA_NAME = "menu_items"

RESPONSE_JSON_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "original_name": {
                "type": "string",
                "description": "Menu item name in the source language.",
            },
            "translated_name": {
                "type": "string",
                "description": "Menu item name translated into the target language (typically English).",
            },
            "description": {
                "type": "string",
                "description": "Supporting description or key ingredients.",
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "description": "Tags for the menu item. should be in the translated language.",
            }
        },
        "required": ["original_name", "translated_name", "description", "tags"],
        "additionalProperties": False,
    },
    "minItems": 1,
}


def build_response_object_schema() -> dict[str, object]:
    """Return top-level object schema required by OpenAI Responses."""

    return {
        "type": "object",
        "properties": {
            "items": deepcopy(RESPONSE_JSON_SCHEMA),
        },
        "required": ["items"],
        "additionalProperties": False,
    }


def build_text_format_config() -> dict[str, object]:
    """Return JSON schema formatting config for OpenAI Responses API."""

    return {
        "type": "json_schema",
        "name": JSON_SCHEMA_NAME,
        "schema": build_response_object_schema(),
        "strict": True,
    }


def build_user_prompt(text: str, lang_in: str | None, lang_out: str) -> str:
    """Return the prompt used for OpenAI call."""

    language_hint = [
        f"Input language: {lang_in if lang_in else 'unspecified (detect automatically)'}",
        f"Output language: {lang_out}",
    ]
    return (
        "Review the extracted menu text below. Combine related lines when appropriate and produce "
        "a JSON array of menu items that follows the schema.\n"
        + "\n".join(language_hint)
        + "\n\nMenu text:\n"
        + text.strip()
    )
