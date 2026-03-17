"""Regex-based entity extraction for engineering documents."""
import re
from typing import Dict, List

_PATTERNS = [
    ('DOC_NUM', r'\bPLW/[A-Z0-9]+/\d{4}/\d{3,6}\b'),
    ('DOC_NUM', r'\bPLW[/-][A-Z0-9]{2,10}[/-][A-Z0-9]{2,20}\b'),
    ('DOC_NUM', r'\bRDSO/[A-Z0-9/.-]{6,40}\b'),
    ('SPEC', r'\bRDSO/[A-Z0-9/.-]*SPEC[A-Z0-9/.-]*\b'),
    ('SPEC', r'\bSPEC(?:IFICATION)?\s*NO\.?\s*[A-Z0-9/-]{4,40}\b'),
    ('STD', r'\b(?:IS|DIN|IEC|ABB|BIS|IRIS|EN)\s*[: ]?[0-9]{3,6}(?:[:-][0-9A-Z]+)*\b'),
    ('DWG', r'\b(?:DRG|DWG|DRAWING)\b[. /-]*[A-Z0-9/-]{4,40}\b'),
    ('DWG', r'\b[A-Z]{2,6}/\d+/\d+/\d+(?:\s+REV(?:ISION)?\s*[A-Z0-9]+)?\b'),
    ('DATE', r'\b(0?[1-9]|[12][0-9]|3[01])[./](0?[1-9]|1[0-2])[./](19|20)\d{2}\b'),
]


def parse_entities(text: str) -> List[Dict]:
    if not text or not text.strip():
        return []

    results = []
    seen = set()
    for entity_type, pattern in _PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(0).strip()
            key = (entity_type, value.upper())
            if key in seen:
                continue
            seen.add(key)
            results.append({'type': entity_type, 'value': value})
    return results
