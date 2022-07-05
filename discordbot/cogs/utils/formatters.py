import re
import string
from typing import List

IP_REGEX = re.compile(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}')
URL_REGEX = re.compile(
    r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
    r'[-a-zA-Z0-9()@:%_\+.~#?&//=]*'
)
MENTION_REGEX = re.compile(r'\<\@(\!)?\d+\>')
EMOJI_REGEX = re.compile(r'\<:\w+:\d+\>')
MULTIPLE_SPACES_REGEX = re.compile(r'\s+')
MARKOV_REGEXES = [
    URL_REGEX, MENTION_REGEX, EMOJI_REGEX, MULTIPLE_SPACES_REGEX
]


def ru_plural(value: int, quantitative: list) -> str:
    if value % 100 in (11, 12, 13, 14):
        return quantitative[2]
    if value % 10 == 1:
        return quantitative[0]
    if value % 10 in (2, 3, 4):
        return quantitative[1]
    return quantitative[2]


def add_punctuation(text: str) -> str:
    if not any(text.endswith(y) for y in string.punctuation) and len(text) > 1:
        return f'{text}.'
    return text


def clean_text(text: str) -> str:
    """Cleans up discord message from mentions, links and emojis"""
    for regex_pattern in MARKOV_REGEXES:
        text = regex_pattern.sub(' ', text.strip())
    if not text or text.startswith('!'):
        return ''
    return add_punctuation(text).strip().capitalize()


def extract_urls(text: str) -> List[str]:
    return URL_REGEX.findall(text)
