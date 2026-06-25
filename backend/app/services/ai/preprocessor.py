from bs4 import BeautifulSoup
import re
import html


# -----------------------------
# SIGNATURE PATTERNS (ROBUST)
# -----------------------------
SIGNATURE_PATTERNS = [
    r"--\s*\n",
    r"(?i)best regards.*",
    r"(?i)kind regards.*",
    r"(?i)thanks and regards.*",
    r"(?i)regards.*",
    r"(?i)sent from my (iphone|android|samsung).*",
]


# -----------------------------
# HTML → TEXT CLEANER
# -----------------------------
def html_to_text(raw_html: str) -> str:
    try:
        soup = BeautifulSoup(raw_html, "html.parser")

        # remove noise tags
        for tag in soup(["script", "style", "head", "meta", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        # decode HTML entities
        text = html.unescape(text)

        # normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()

    except Exception:
        # fallback (never crash pipeline)
        return raw_html


# -----------------------------
# SIGNATURE REMOVAL (FIXED)
# -----------------------------
def remove_signature(text: str) -> str:

    for pattern in SIGNATURE_PATTERNS:
        match = re.search(pattern, text)

        if match:
            return text[:match.start()].strip()

    return text


# -----------------------------
# MAIN CLEANER
# -----------------------------
def clean_email_body(raw_body: str, is_html: bool = False) -> str:

    # step 1: HTML cleanup
    text = html_to_text(raw_body) if is_html else raw_body

    # step 2: signature removal
    text = remove_signature(text)

    # step 3: final cleanup
    text = re.sub(r"\n\s*\n", "\n\n", text).strip()

    return text
