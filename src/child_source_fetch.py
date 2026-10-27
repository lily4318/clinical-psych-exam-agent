"""Read limited clinical guidance excerpts from *allowlisted* official NICE pages.

This is a transport/provenance helper, NOT a clinical fact checker, search
engine, or verification of the semantic support for generated answers.
All HTTP requests use the free Python standard library.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

_MAX_PAGE_BYTES = 3 * 1024 * 1024
_MAX_EXCERPT_CHARS = 8000
_MIN_EXCERPT_CHARS = 400
_ASSESSMENT_SECTIONS = {
    # Original first-8k excerpts may omit later assessment recommendations.
    "NICE-NG87": (r"\b1\.3\s+Diagnosis\b", r"\b1\.3\.1\b"),
    "NICE-CG128": (r"\b1\.5\s+Autism diagnostic assessment\b", r"\b1\.5\.1\b"),
    "NICE-NG11": (r"\b1\.5\s+Assessment of behaviour that challenges\b", r"\b1\.5\.1\b"),
}
_ALLOWED_HOST = "www.nice.org.uk"
_ALLOWED_PATH = re.compile(r"^/guidance/(ng|cg)[0-9]+/chapter/", re.IGNORECASE)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _GuidanceText(HTMLParser):
    """Extract visible text from the document's main region only."""

    VOID_ELEMENTS = frozenset(
        {"area", "base", "br", "col", "embed", "hr", "img", "input",
         "link", "meta", "param", "source", "track", "wbr"}
    )
    HIDDEN_ELEMENTS = frozenset(
        {"script", "style", "noscript", "nav", "footer", "aside", "svg", "button"}
    )

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._inside_main = False
        self._depth = 0
        self._hidden = 0
        self._parts: list[str] = []
        self.saw_main = False

    def handle_starttag(self, tag, attrs):
        if tag == "main" and not self._inside_main:
            self._inside_main = True
            self._depth = 1
            self.saw_main = True
            return
        if self._inside_main:
            if tag not in self.VOID_ELEMENTS:
                self._depth += 1
            if tag in self.HIDDEN_ELEMENTS:
                self._hidden += 1

    def handle_endtag(self, tag):
        if self._inside_main:
            if tag in self.HIDDEN_ELEMENTS and self._hidden:
                self._hidden -= 1
            if tag not in self.VOID_ELEMENTS:
                self._depth -= 1
            if self._depth <= 0:
                self._inside_main = False

    def handle_data(self, data):
        if self._inside_main and not self._hidden:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self._parts.append(cleaned)

    def text(self) -> str:
        return " ".join(self._parts)


def _check_official_url(url: str, *, source_id: str) -> None:
    try:
        parts = urlsplit(url)
        port = parts.port
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError(f"{source_id}: invalid guidance URL.") from exc
    if (
        parts.scheme != "https"
        or parts.hostname != _ALLOWED_HOST
        or port not in (None, 443)
        or parts.username is not None
        or parts.password is not None
        or not _ALLOWED_PATH.match(parts.path)
        or parts.query
        or parts.fragment
    ):
        raise ValueError(f"{source_id}: URL is not an allowlisted official NICE guidance page.")


def _extract_recommendations(body: bytes, *, source_id: str) -> str:
    try:
        html = body.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{source_id}: unsupported webpage encoding.") from exc
    parser = _GuidanceText()
    parser.feed(html)
    text = parser.text()
    if not parser.saw_main or len(text) < _MIN_EXCERPT_CHARS:
        raise ValueError(f"{source_id}: missing substantial visible guidance text.")

    # Fail on cookie notices, robot challenges, and unrelated pages.
    if not re.search(r"\bRecommendations\b", text[:3500], flags=re.IGNORECASE):
        raise ValueError(f"{source_id}: official recommendations section not identified.")
    index = re.search(r"\bRecommendations\b", text, flags=re.IGNORECASE)
    assert index is not None
    recommendations = text[index.start():]
    excerpt = recommendations[:_MAX_EXCERPT_CHARS]
    # Preserve original diagnosis/assessment guidance even when the introductory
    # material pushes it beyond the first 8,000 characters. Mark the omission.
    # This is a bounded excerpt, not claim-level semantic verification.
    section = _ASSESSMENT_SECTIONS.get(source_id)
    if section:
        heading, first_recommendation = section
        candidates = [
            match for match in re.finditer(heading, recommendations, re.IGNORECASE)
            if re.search(
                first_recommendation,
                recommendations[match.end():match.end() + 700],
                re.IGNORECASE,
            )
        ]
        if candidates:
            offset = candidates[-1].start()
            prefix_chars = 1400
            separator = " [...] "
            if offset > _MAX_EXCERPT_CHARS - prefix_chars:
                tail_chars = _MAX_EXCERPT_CHARS - prefix_chars - len(separator)
                excerpt = (
                    recommendations[:prefix_chars] + separator
                    + recommendations[offset:offset + tail_chars]
                )
    if len(excerpt) < _MIN_EXCERPT_CHARS:
        raise ValueError(f"{source_id}: recommendations excerpt is too short.")
    return excerpt


def fetch_official_guidance_evidence(
    sources: dict[str, Any],
    source_ids: set[str],
    *,
    timeout_seconds: float = 20,
) -> dict[str, dict[str, str]]:
    """Fetch each required clinical source with at most one timeout retry.

    The caller supplies the *already validated* domain blueprint's source
    catalog. User-supplied URLs never determine the destination.
    Returns prose excerpts + URL + UTC date + body SHA256 for an audit trail.
    No result is rated as clinically or semantically validated.
    """
    if isinstance(timeout_seconds, bool) or not 1 <= timeout_seconds <= 60:
        raise ValueError("timeout_seconds must be between 1 and 60.")
    if not source_ids:
        raise ValueError("At least one required clinical source is needed.")

    opener = build_opener(ProxyHandler({}), _NoRedirect())
    result: dict[str, dict[str, str]] = {}
    for source_id in sorted(source_ids):
        source = sources.get(source_id)
        if not isinstance(source, dict) or source.get("kind") != "clinical_guideline":
            raise ValueError(f"{source_id}: not a recognized clinical guidance source.")
        url = source.get("url")
        if not isinstance(url, str):
            raise ValueError(f"{source_id}: guidance URL is missing.")
        _check_official_url(url, source_id=source_id)
        request = Request(url, headers={
            "User-Agent": "ClinicalPsychExamAgent/0.2 (public-guideline-fetch)",
            "Accept": "text/html",
        })
        # Retry only a transient HTTPS timeout once; all other failures remain fatal.
        for attempt in range(2):
            try:
                with opener.open(request, timeout=timeout_seconds) as response:
                    mime = response.headers.get("Content-Type", "")
                    if "text/html" not in mime.lower():
                        raise ValueError(f"{source_id}: unexpected content type {mime!r}.")
                    # Redirects are disabled; an unexpected final URL is also rejected.
                    if response.geturl() != url:
                        raise ValueError(f"{source_id}: unexpected final URL.")
                    raw = response.read(_MAX_PAGE_BYTES + 1)
                break
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                if isinstance(exc, TimeoutError) and attempt == 0:
                    continue
                raise RuntimeError(
                    f"{source_id}: could not fetch the official guideline. "
                    "No model call or exam output is permitted without evidence."
                ) from exc

        if len(raw) > _MAX_PAGE_BYTES:
            raise ValueError(f"{source_id}: official page exceeds the size limit.")
        passage = _extract_recommendations(raw, source_id=source_id)
        result[source_id] = {
            "url": url,
            "passage": passage,
            "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "page_sha256": hashlib.sha256(raw).hexdigest(),
            "retrieval_method": "official_nice_https_html",
            "verification_status": "retrieved_excerpt_not_semantically_verified",
        }
    return result
