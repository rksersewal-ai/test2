"""Simple regex-based entity extraction for engineering documents.

Extracts:
- Document numbers (PLW/XXX/YYY pattern)
- RDSO spec / modification notice numbers
- IS / DIN / ABB / IEC standard numbers
- Drawing numbers
- Dates (DD.MM.YYYY or DD/MM/YYYY)

This is intentionally rule-based for LAN-only, no-internet operation.
Replace with a trained NER model when offline ML infra is available.
"""
import re
from typing import List, Dict

# Pattern bank — extend as new document formats are catalogued
_PATTERNS = [
    ('DOC_NUM', r'PLW[/-][A-Z0-9]{2,10}[/-][A-Z0-9]{2,20}'),
    ('DOC_NUM', r'RDSO/[A-Z]{1,6}[/-][0-9]{4,8}(?:[/-][A-Z0-9]+)?'),
    ('SPEC', r'SPEC(?:IFICATION)?\s*NO\.?\s*[A-Z0-9/-]{4,20}'),
    ('STD', r'(?:IS|DIN|IEC|ABB|BIS|IRIS|EN)\s*[: ]?[0-9]{3,6}(?:[:-][0-9]+)?'),
    ('DWG', r'DRG(?:WG)?[. /-][A-Z0-9/-]{4,25}'),
    ('DATE', r'\b(0?[1-9]|[12][0-9]|3[01])[./](0?[1-9]|1[0-2])[./](19|20)\d{2}\b'),
]


def parse_entities(text: str) -> List[Dict]:
    results = []
    seen = set()
    for entity_type, pattern in _PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            val = match.group(0).strip()
            key = (entity_type, val.upper())
            if key not in seen:
                seen.add(key)
                results.append({'type': entity_type, 'value': val})
    return results
