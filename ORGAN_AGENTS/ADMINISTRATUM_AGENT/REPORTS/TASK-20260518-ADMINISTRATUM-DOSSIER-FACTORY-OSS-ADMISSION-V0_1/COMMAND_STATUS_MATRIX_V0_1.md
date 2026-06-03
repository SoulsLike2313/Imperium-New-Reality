# Command Status Matrix V0.1

| command | status | notes |
|---|---|---|
| `python .../administratum_agent_runner.py --help` | implemented_tested | Exit 0; command list includes `doctor-oss`, `build-dossier`, `verify-dossier`. |
| `python .../administratum_agent_runner.py --no-color status` | implemented_tested | Exit 0; compact contract output with WHY_TRUST block. |
| `python .../administratum_agent_runner.py --plain-json --no-color status` | implemented_tested | Exit 0; parseable machine-first contract shape. |
| `python .../administratum_agent_runner.py --no-color --verbose status` | implemented_tested | Exit 0; metrics/details blocks present. |
| `python .../administratum_agent_runner.py --no-color --no-rich status` | implemented_tested | Exit 0; stdlib renderer forced. |
| `python .../administratum_agent_runner.py --rich --no-color status` | implemented_tested | Exit 0; rich mode path exercised. |
| `python .../administratum_agent_runner.py --no-color doctor-rich` | implemented_tested | Exit 0; renderer diagnostics and fallback reasons reported. |
| `python .../administratum_agent_runner.py --no-color doctor-oss` | implemented_tested | Exit 0; OSS availability and PDF backend detection reported. |
| `python .../administratum_agent_runner.py --no-color inventory` | implemented_tested | Exit 0; long-running phase progression observed. |
| `python .../administratum_agent_runner.py --no-color collect-reality-snapshot` | implemented_tested | Exit 0; snapshot report/receipt generated. |
| `python .../administratum_agent_runner.py --no-color collect-continuity-pack` | implemented_tested | Exit 0 on rerun with longer timeout; maturity capsule pipeline present. |
| `python .../administratum_agent_runner.py --no-color check-all` | implemented_tested | Exit 0; suite verdict PASS. |
| `python .../administratum_agent_runner.py --no-color build-dossier --task-id TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1` | implemented_tested | Exit 0; run id `RUN-ADMINISTRATUM-20260518-164612-079fbf`, dossier verdict PASS. |
| `python .../administratum_agent_runner.py --no-color verify-dossier --latest` | implemented_tested | Exit 0; run id `RUN-ADMINISTRATUM-20260518-164627-4b6060`, hash and required files PASS. |
