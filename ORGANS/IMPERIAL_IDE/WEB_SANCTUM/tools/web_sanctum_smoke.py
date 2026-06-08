#!/usr/bin/env python3
import json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks={
 "package_v050": "imperium-web-sanctum-v050" in (root/'package.json').read_text(encoding='utf-8'),
 "surface_v05": "WEB_SANCTUM_OPERATIONAL_SPINE_AND_WARP_V0_5" in (root/'app'/'main.js').read_text(encoding='utf-8'),
 "warp_page_present": "data-testid=\"page-warp\"" in (root/'app'/'index.html').read_text(encoding='utf-8'),
 "task_registration_present": "data-testid=\"page-register\"" in (root/'app'/'index.html').read_text(encoding='utf-8'),
 "validation_present": "data-testid=\"page-validation\"" in (root/'app'/'index.html').read_text(encoding='utf-8'),
 "report_bundle_present": "build_report_bundle" in (root/'tools'/'local_bridge.py').read_text(encoding='utf-8'),
 "no_arbitrary_shell_endpoint": "shell=True" not in (root/'tools'/'local_bridge.py').read_text(encoding='utf-8'),
 "playwright_screenshots": "test:pw:screenshots" in (root/'package.json').read_text(encoding='utf-8'),
}
print(json.dumps({"status":"PASS" if all(checks.values()) else "FAIL", "surface":"WEB_SANCTUM_OPERATIONAL_SPINE_AND_WARP_V0_5", "checks":checks}, indent=2))
