import pytest
import requests

from core.language_tool_client import (LanguageToolClient, LanguageToolError,
                                       Match, RateLimiter, apply_matches)


class FakeResponse:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload or {}
        self.text = str(payload)

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, data=None, timeout=None):
        self.calls.append(data)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def lt_payload(offset, length, value, category="GRAMMAR", issue="grammar"):
    return {"matches": [{
        "offset": offset, "length": length, "message": "msg",
        "replacements": [{"value": value}],
        "rule": {"id": "RULE", "issueType": issue, "category": {"id": category}},
    }]}


def client(responses, **kw):
    session = FakeSession(responses)
    return LanguageToolClient(url="http://lt/v2/check", language="en-US", session=session,
                              sleep=lambda s: None, **kw), session


def test_check_applies_suggestions():
    text = "The results shows that emissions was increased."
    payload = {"matches": [
        lt_payload(4, 13, "results show")["matches"][0],
        lt_payload(23, 13, "emissions were")["matches"][0],
    ]}
    lt, session = client([FakeResponse(200, payload)])
    assert lt.check(text) == "The results show that emissions were increased."
    assert session.calls[0]["language"] == "en-US"


def test_empty_text_makes_no_request():
    lt, session = client([])
    assert lt.check("   ") == "   "
    assert session.calls == []


def test_utf16_offsets_are_mapped():
    text = "😀 teh cat"  # emoji is 2 UTF-16 code units
    lt, _ = client([FakeResponse(200, lt_payload(3, 3, "the", "TYPOS", "misspelling"))])
    (match,) = lt.check_matches(text)
    assert text[match.start:match.end] == "teh"
    assert match.group == "spelling"


def test_retries_then_succeeds():
    lt, session = client([requests.ConnectionError("down"), FakeResponse(503),
                          FakeResponse(200, lt_payload(0, 3, "The"))], max_retries=4)
    assert lt.check("teh") == "The"
    assert len(session.calls) == 3


def test_gives_up_after_max_retries():
    lt, _ = client([FakeResponse(429)] * 3, max_retries=3)
    with pytest.raises(LanguageToolError):
        lt.check_matches("some text")


def test_client_error_is_not_retried():
    lt, session = client([FakeResponse(400, {"error": "bad"})])
    with pytest.raises(LanguageToolError):
        lt.check_matches("some text")
    assert len(session.calls) == 1


def test_results_are_cached():
    lt, session = client([FakeResponse(200, {"matches": []})])
    lt.check_matches("same text")
    lt.check_matches("same text")
    assert len(session.calls) == 1


def test_credentials_and_picky_are_sent():
    lt, session = client([FakeResponse(200, {"matches": []})], username="me", api_key="k", picky=True)
    lt.check_matches("x y")
    assert session.calls[0]["username"] == "me" and session.calls[0]["apiKey"] == "k"
    assert session.calls[0]["level"] == "picky"


def test_apply_matches_skips_overlaps_and_empty():
    text = "abc def"
    matches = [Match(0, 3, ["X"], "", "", "", ""), Match(2, 5, ["Y"], "", "", "", ""),
               Match(4, 7, [], "", "", "", "")]
    assert apply_matches(text, matches) in ("X def", "abYef")


def test_rate_limiter_waits():
    now = [0.0]
    slept = []

    def sleep(s):
        slept.append(s)
        now[0] += s

    limiter = RateLimiter(requests_per_minute=2, clock=lambda: now[0], sleep=sleep)
    for _ in range(3):
        limiter.acquire(10)
    assert slept and now[0] >= 60
