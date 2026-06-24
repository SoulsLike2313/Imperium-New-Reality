"""E3 self-test for EYES-V2-CODEBOOK-0001.

Validates the doctrinal markdown is well-formed and contains the
ratified spec values. All paths resolve relative to PACK_ROOT.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # files/ORGANS/INQUISITION/TESTS
PACK_ROOT = HERE.parents[3]                          # pack root
DOC = PACK_ROOT / "files" / "ORGANS" / "DOCTRINARIUM" / "EYES_V2.md"

results = []

def check(name, ok, detail=""):
    results.append(bool(ok))
    suffix = (" -> " + detail) if (detail and not ok) else ""
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, suffix))

# T1: doc exists and parses as UTF-8
try:
    text = DOC.read_text(encoding="utf-8-sig")
    check("T1_doc_parses_utf8", len(text) > 1000, "too short: %d bytes" % len(text))
except Exception as e:
    check("T1_doc_parses_utf8", False, str(e))
    print("\n0/6 PASSED\nE3 RESULT: FAILURES PRESENT")
    sys.exit(1)

# T2: all required sections present
required_sections = [
    "TONAL_FIELD", "ACCENT_DISCIPLINE", "COMPOSITION_CLASS",
    "COSMIC_VOLUME", "GAZE_AXIS", "TPS_SPIRIT",
    "FORBIDDEN", "OPERATIONAL_ARTIFACTS", "VERSIONING", "SIGNATURE",
]
missing = [s for s in required_sections if s not in text]
check("T2_all_sections_present", not missing, "missing: %s" % missing)

# T3: ratified numeric ranges are present
required_numbers = [
    "240..290",     # tonal hue
    "100..180",     # tonal saturation
    "50..70",       # accent yellow hue
    "5..10%",       # accent area (the 0.2 update vs draft 0.1)
    "5..25%",       # subject area
]
missing_n = [n for n in required_numbers if n not in text]
check("T3_numeric_ranges_present", not missing_n, "missing: %s" % missing_n)

# T4: GAZE default is A_INWARD
check("T4_gaze_default_inward",
      "A_INWARD" in text and "gaze_default  : A_INWARD" in text)

# T5: TPS is explicitly softened to posture, not literal syntax
tps_softened = ("posture, not as syntax" in text) and ("Inherit the attitude. Drop the brushstrokes." in text)
check("T5_tps_is_posture_not_syntax", tps_softened)

# T6: v0.2 ratification line and #17-class forbidden
ratified = "v0.2" in text and "#17-class" in text
check("T6_v02_ratified_and_17_forbidden", ratified)

total = len(results)
passed = sum(1 for r in results if r)
print("\n%d/%d PASSED" % (passed, total))
print("E3 RESULT: " + ("ALL PASSED" if passed == total else "FAILURES PRESENT"))
sys.exit(0 if passed == total else 1)
