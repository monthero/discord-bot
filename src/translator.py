import logging
from dataclasses import dataclass, field
from pathlib import Path
from re import (
    IGNORECASE,
    Pattern,
    compile as re_compile,
    sub as re_sub,
)
from typing import Any, Dict, List, Tuple

from google.cloud import translate_v3 as translate
from google.oauth2 import service_account


logger = logging.getLogger(__name__)


@dataclass
class Translator:
    project_id: str
    _client: translate.TranslationServiceClient = field(init=False)
    _parent: str = field(init=False)

    def __post_init__(self):
        creds = service_account.Credentials.from_service_account_file(
            Path(__file__).parent.parent.joinpath("credentials.json")
        )
        self._client = translate.TranslationServiceClient(credentials=creds)
        self._parent = f"projects/{self.project_id}/locations/global"

    def _create_request(self, **kwargs) -> Dict[str, Any]:
        return {
            "parent": self._parent,
            "mime_type": "text/plain",
        } | kwargs

    def _detect_language(self, text: str) -> str:
        response = self._client.detect_language(
            request=self._create_request(content=text)
        )

        return response.languages[0].language_code

    @staticmethod
    def _prepate_text_for_translation(text: str) -> Tuple[str, List[str]]:
        """
        Prepares text for translation by replacing tokens we don't want translated,
        such as discord emojis, mentions and urls, with placeholders.

        Returns the matched tokens and the text with the tokens replaced by the string
        ``{}``.
        """

        if not isinstance(text, str) or not text:
            return text, []

        pattern: Pattern = re_compile(r"(@everyone|@here)")

        tokens = [
            token.group() for token in pattern.finditer(text) if token is not None
        ]

        for token in tokens:
            text = re_sub(token, "{}", text, flags=IGNORECASE)

        return text, tokens

    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        prepared_text, tokens = self._prepate_text_for_translation(text)

        try:
            translated_text = (
                self._client.translate_text(
                    request=self._create_request(
                        contents=[prepared_text],
                        source_language_code=source_lang,
                        target_language_code=target_lang,
                    )
                )
                .translations[0]
                .translated_text
            )
        except Exception as exc:  # noqa: BLE001
            return f"I'm sorry, I couldn't translate that. Error: {exc}"

        # replace occurences of {} with the original tokens in order
        return translated_text.format(*tokens)

    def translate(self, text: str) -> str:
        if not isinstance(text, str) or not text:
            raise TypeError("text must be a non-empty string")

        source_lang = self._detect_language(text)

        en_flag = ":flag_gb:"
        jp_flag = ":flag_jp:"

        if source_lang.startswith("ja"):
            text = self._translate_text(text, source_lang, "en-US")
            text = f"{en_flag} {text}"
        elif source_lang.startswith("en"):
            text = self._translate_text(text, source_lang, "ja-JP")
            text = f"{jp_flag} {text}"
        else:
            text_en = self._translate_text(text, source_lang, "en-US")
            text_ja = self._translate_text(text, source_lang, "ja-JP")
            text = f"{en_flag} {text_en}\n{jp_flag} {text_ja}"

        return text
