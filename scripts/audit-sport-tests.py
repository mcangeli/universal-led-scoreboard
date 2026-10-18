#!/usr/bin/env python3
"""Report brittle test assertions that can block adding another sport.

Run: python3 scripts/audit-sport-tests.py
This is a review report, not a replacement for behavior-based regression tests.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
PATTERNS = {
    "literal sport roster": re.compile(r"""\[(?:['"](?:mlb|nhl|nba|wnba|nfl|mls|nwsl|english)['"],?\s*){3,}\]"""),
    "exact scheduler constructor": re.compile(r"""assert(?:In|Equal)\(.*MultiSportRenderer\(renderer"""),
    "exact sport count": re.compile(r"""assert(?:Equal|CountEqual)\(.*(?:panels|sports).*\b[6789]\b"""),
}

def audit():
    findings = []
    for path in sorted(TESTS.glob("test_*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for kind, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append((path.relative_to(ROOT), number, kind, line.strip()))
    return findings

if __name__ == "__main__":
    findings = audit()
    print(f"Scanned {len(list(TESTS.glob('test_*.py')))} test files.")
    if findings:
        print(f"{len(findings)} potential maintenance hotspots:")
        for path, number, kind, line in findings:
            print(f"  {path}:{number}: {kind}: {line[:150]}")
    else:
        print("No known hard-coded sport-roster assertions detected.")
