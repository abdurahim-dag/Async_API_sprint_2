from dataclasses import dataclass
from gettext import gettext as _


@dataclass
class Film:
    not_found: str = _('film not found')
    not_founds: str = _('films not found')


@dataclass
class Genre:
    not_found: str = _('genre not found')
    not_founds: str = _('genres not found')


@dataclass
class Person:
    not_found: str = _('person not found')
    not_founds: str = _('persons not found')

