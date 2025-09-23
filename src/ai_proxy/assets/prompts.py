"""Prompt building helpers for OpenAI payload construction."""

from __future__ import annotations

SYSTEM_INSTRUCTIONS = (
    "You are a backend service that converts raw OCR menu text into structured menu data. "
    "Always return a JSON array where each element represents a menu item with the fields "
    "`name`, `translated_name`, and `description`. Do not include any additional commentary "
    "outside of the JSON array."
)


RESPONSE_JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "MenuItems",
        "schema": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
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
                },
                "required": ["name", "translated_name", "description"],
                "additionalProperties": False,
            },
            "minItems": 1,
        },
        "strict": True,
    },
}


def build_user_prompt(texts: list[str]) -> str:
    """Return a single prompt string that enumerates provided text snippets."""

    formatted_sections = [f"Menu text {idx + 1}:\n{text.strip()}" for idx, text in enumerate(texts)]
    return (
        "Review the extracted menu text snippets below. Combine related lines when appropriate and "
        "produce a JSON array of menu items that follows the schema.\n\n"
        + "\n\n".join(formatted_sections)
    )
