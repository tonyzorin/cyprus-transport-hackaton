"""
Text utilities for route name normalization
Route name normalization for matching GTFS and realtime feeds
"""
from typing import Dict

_GREEK_TO_LATIN: Dict[str, str] = {
    'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H',
    'Θ': 'TH', 'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X',
    'Ο': 'O', 'Π': 'P', 'Ρ': 'P', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Φ': 'F',
    'Χ': 'X', 'Ψ': 'PS', 'Ω': 'O'
}


def normalize_route_name(name: str) -> str:
    """Normalize route short names for matching GTFS and realtime feeds."""
    if not name:
        return ''

    sanitized = name.strip().upper().replace(' ', '')
    normalized_chars = [_GREEK_TO_LATIN.get(ch, ch) for ch in sanitized]
    return ''.join(normalized_chars)
