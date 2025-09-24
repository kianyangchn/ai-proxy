"""Prompt building helpers for OpenAI payload construction."""

from __future__ import annotations

SYSTEM_INSTRUCTIONS = (
    "You convert raw OCR menu text into structured menu data. Follow these rules strictly: "
    "1) Extract distinct dish names from the text, merging duplicates when wording differs slightly. "
    "2) Preserve the original dish wording in `original_name` and translate it into the requested "
    "output language for `translated_name`. "
    "3) For each dish, write a short descriptive sentence in the output language that includes "
    "typical ingredients, preparation method, and expected flavour profile (for example sweet, "
    "savory, spicy). Use natural phrasing rather than bullet lists. "
    "4) Return only a JSON array and ensure every object contains `original_name`, `translated_name`, "
    "and `description`. No extra commentary or keys."
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
                },
                "required": ["original_name", "translated_name", "description"],
                "additionalProperties": False,
            },
            "minItems": 1,
        },
        "strict": True,
    },
}


def build_user_prompt(texts: list[str], lang_in: str | None, lang_out: str) -> str:
    """Return a single prompt string that enumerates provided text snippets."""

    formatted_sections = [f"Menu text {idx + 1}:\n{text.strip()}" for idx, text in enumerate(texts)]
    language_hint = [
        f"Input language: {lang_in if lang_in else 'unspecified (detect automatically)'}",
        f"Output language: {lang_out}",
    ]
    return (
        "Review the extracted menu text snippets below. Combine related lines when appropriate and "
        "produce a JSON array of menu items that follows the schema.\n"
        + "\n".join(language_hint)
        + "\n\n"
        + "\n\n".join(formatted_sections)
    )
