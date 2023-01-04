import logging
from gettext import gettext
from gettext import translation
from typing import Callable


_default_lang = None

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGE = ["ru", "en"]
DOMAIN = 'messages'
LOCALEDIR = 'locale'


def active_translation(lang: str):
    global _default_lang
    _default_lang = (
        DEFAULT_LANGUAGE if lang not in SUPPORTED_LANGUAGE else lang
    )


def _gettext(message: str):
    if _default_lang:
        try:
            return translation(
                DOMAIN,
                localedir=LOCALEDIR,
                languages=[_default_lang]
            ).gettext(message=message)

        except FileNotFoundError:
            logging.exception(
                'FileNotFoundError localization for domain(%s) dir(%s) lang(%s)',
                DOMAIN,
                LOCALEDIR,
                _default_lang
            )
    return gettext(message=message)


_: Callable[[str], str] = _gettext
