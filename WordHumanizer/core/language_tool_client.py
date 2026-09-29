"""LanguageTool HTTP client with retries, rate limiting, caching and filtering."""

import threading
import time
from collections import deque
from dataclasses import dataclass

import requests
from tenacity import (Retrying, retry_if_exception, stop_after_attempt,
                      wait_exponential)

from utils.logger import get_logger
from utils.text_utils import needs_utf16_mapping, utf16_offset_map

log = get_logger("languagetool")

# LanguageTool category ids -> the four user-facing option groups.
CATEGORY_GROUPS = {
    "TYPOS": "spelling",
    "GRAMMAR": "grammar",
    "CONFUSED_WORDS": "grammar",
    "CASING": "grammar",
    "COLLOCATIONS": "grammar",
    "SEMANTICS": "grammar",
    "NONSTANDARD_PHRASES": "grammar",
    "MISC": "grammar",
    "PUNCTUATION": "punctuation",
    "TYPOGRAPHY": "punctuation",
    "COMPOUNDING": "punctuation",
    "STYLE": "style",
    "REDUNDANCY": "style",
    "PLAIN_ENGLISH": "style",
    "WIKIPEDIA": "style",
    "REPETITIONS_STYLE": "style",
    "REPETITIONS": "style",
    "CREATIVE_WRITING": "style",
    "GENDER_NEUTRALITY": "style",
    "TEXT_ANALYSIS": "style",
}

ISSUE_TYPE_GROUPS = {
    "misspelling": "spelling",
    "typographical": "punctuation",
    "whitespace": "punctuation",
    "style": "style",
    "register": "style",
    "locale-violation": "style",
    "duplication": "style",
}


@dataclass
class Match:
    start: int
    end: int
    replacements: list
    rule_id: str
    category: str
    issue_type: str
    message: str

    @property
    def group(self):
        return CATEGORY_GROUPS.get(self.category) or ISSUE_TYPE_GROUPS.get(self.issue_type, "grammar")

    @property
    def replacement(self):
        return self.replacements[0] if self.replacements else None


class LanguageToolError(RuntimeError):
    pass


class _RetryableError(LanguageToolError):
    pass


class RateLimiter:
    """Sliding one-minute window limiting requests and characters."""

    def __init__(self, requests_per_minute=0, chars_per_minute=0, clock=time.monotonic, sleep=time.sleep):
        self.rpm = requests_per_minute
        self.cpm = chars_per_minute
        self.clock = clock
        self.sleep = sleep
        self.events = deque()
        self.lock = threading.Lock()

    def acquire(self, chars):
        if not self.rpm and not self.cpm:
            return
        with self.lock:
            while True:
                now = self.clock()
                while self.events and now - self.events[0][0] >= 60:
                    self.events.popleft()
                used_chars = sum(c for _, c in self.events)
                ok_requests = not self.rpm or len(self.events) < self.rpm
                ok_chars = not self.cpm or not self.events or used_chars + chars <= self.cpm
                if ok_requests and ok_chars:
                    self.events.append((now, chars))
                    return
                wait = 60 - (now - self.events[0][0]) + 0.05
                self.sleep(max(wait, 0.05))


class LanguageToolClient:

    def __init__(self, url=None, language=None, username="", api_key="", timeout=60,
                 max_retries=4, requests_per_minute=0, chars_per_minute=0, session=None,
                 picky=False, disabled_rules=(), sleep=time.sleep):
        if url is None or language is None:
            from config import LANGUAGE, LANGUAGETOOL_URL
            url = url or LANGUAGETOOL_URL
            language = language or LANGUAGE
        self.url = url
        self.language = language
        self.username = username
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max(1, max_retries)
        self.session = session or requests.Session()
        self.picky = picky
        self.disabled_rules = list(disabled_rules)
        self.limiter = RateLimiter(requests_per_minute, chars_per_minute, sleep=sleep)
        self._sleep = sleep
        self._cache = {}
        self.request_count = 0

    @classmethod
    def from_settings(cls, settings, language=None, picky=False):
        return cls(
            url=settings.languagetool_url,
            language=language or settings.language,
            username=settings.languagetool_username,
            api_key=settings.languagetool_api_key,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
            requests_per_minute=settings.requests_per_minute,
            chars_per_minute=settings.chars_per_minute,
            picky=picky,
        )

    # ----------------------------------------------------------------- API
    def check_matches(self, text):
        """Return LanguageTool matches for ``text`` with Python string offsets."""
        if not text.strip():
            return []
        key = (self.language, self.picky, text)
        if key in self._cache:
            return self._cache[key]
        payload = self._request(text)
        matches = self._parse(text, payload.get("matches", []))
        self._cache[key] = matches
        return matches

    def check(self, text):
        """Return ``text`` with the first suggestion of every match applied."""
        return apply_matches(text, self.check_matches(text))

    # ------------------------------------------------------------ internals
    def _request(self, text):
        data = {"language": self.language, "text": text}
        if self.username and self.api_key:
            data.update(username=self.username, apiKey=self.api_key)
        if self.picky:
            data["level"] = "picky"
        if self.disabled_rules:
            data["disabledRules"] = ",".join(self.disabled_rules)

        retrying = Retrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=2, min=2, max=60),
            retry=retry_if_exception(lambda e: isinstance(e, _RetryableError)),
            sleep=self._sleep,
            reraise=True,
        )
        for attempt in retrying:
            with attempt:
                self.limiter.acquire(len(text))
                return self._post(data)

    def _post(self, data):
        self.request_count += 1
        try:
            response = self.session.post(self.url, data=data, timeout=self.timeout)
        except (requests.ConnectionError, requests.Timeout) as error:
            log.warning("LanguageTool connection problem: %s", error)
            raise _RetryableError(f"Cannot reach LanguageTool at {self.url}: {error}") from error
        if response.status_code == 429 or response.status_code >= 500:
            log.warning("LanguageTool HTTP %s, retrying", response.status_code)
            raise _RetryableError(f"LanguageTool returned HTTP {response.status_code}")
        if response.status_code >= 400:
            raise LanguageToolError(
                f"LanguageTool rejected the request (HTTP {response.status_code}): {response.text[:300]}")
        try:
            return response.json()
        except ValueError as error:
            raise _RetryableError("LanguageTool returned invalid JSON") from error

    @staticmethod
    def _parse(text, raw_matches):
        mapping = utf16_offset_map(text) if needs_utf16_mapping(text) else None
        matches = []
        for raw in raw_matches:
            offset, length = raw.get("offset", 0), raw.get("length", 0)
            if mapping is not None:
                start = mapping[min(offset, len(mapping) - 1)]
                end = mapping[min(offset + length, len(mapping) - 1)]
            else:
                start, end = offset, offset + length
            rule = raw.get("rule") or {}
            matches.append(Match(
                start=start,
                end=end,
                replacements=[r.get("value", "") for r in raw.get("replacements", [])],
                rule_id=rule.get("id", ""),
                category=(rule.get("category") or {}).get("id", ""),
                issue_type=rule.get("issueType", ""),
                message=raw.get("message", ""),
            ))
        return matches


def apply_matches(text, matches):
    """Apply first suggestions right-to-left, skipping overlapping matches."""
    edits = []
    last_start = None
    for match in sorted(matches, key=lambda m: m.start, reverse=True):
        if match.replacement is None:
            continue
        if last_start is not None and match.end > last_start:
            continue
        edits.append(match)
        last_start = match.start
    for match in edits:
        text = text[:match.start] + match.replacement + text[match.end:]
    return text
