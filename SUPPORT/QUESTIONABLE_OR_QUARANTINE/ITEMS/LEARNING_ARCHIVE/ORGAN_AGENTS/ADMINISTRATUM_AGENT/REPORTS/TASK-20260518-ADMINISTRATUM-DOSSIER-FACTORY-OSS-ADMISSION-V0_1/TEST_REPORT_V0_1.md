# Test Report V0.1

## Environment
- repo_root: `E:\IMPERIUM`
- branch: `master`
- head: `2b43737f46595fe9e7f2837276724db2ef56a24e`
- precondition: Owner-authorized continuation with dirty tree.

## Command execution matrix
| Command | Exit code | Classification | Evidence |
|---|---:|---|---|
| `python .../administratum_agent_runner.py --help` | 0 | pass | help shows new commands. |
| `python .../administratum_agent_runner.py --no-color status` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162453-faea10` |
| `python .../administratum_agent_runner.py --plain-json --no-color status` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162453-af4db2` |
| `python .../administratum_agent_runner.py --no-color doctor-rich` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162459-ccf173` |
| `python .../administratum_agent_runner.py --no-color doctor-oss` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162459-ccf173` |
| `python .../administratum_agent_runner.py --no-color inventory` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162459-adf934` |
| `python .../administratum_agent_runner.py --no-color collect-reality-snapshot` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162548-4e6e8e` |
| `python .../administratum_agent_runner.py --no-color collect-continuity-pack` | 124 | timeout | first attempt timeout (insufficient timeout budget). |
| `python .../administratum_agent_runner.py --no-color collect-continuity-pack` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162858-cd4720` |
| `python .../administratum_agent_runner.py --no-color --verbose status` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162548-ab9eae` |
| `python .../administratum_agent_runner.py --no-color --no-rich status` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162858-b0dff4` |
| `python .../administratum_agent_runner.py --rich --no-color status` | 0 | pass_with_warnings | run id `RUN-ADMINISTRATUM-20260518-162858-e25a3f` |
| `python .../administratum_agent_runner.py --no-color check-all` | 0 | pass | run id `RUN-ADMINISTRATUM-20260518-163500-32697b` |
| `python .../administratum_agent_runner.py --no-color build-dossier --task-id TASK-20260518-ADMINISTRATUM-DOSSIER-FACTORY-OSS-ADMISSION-V0_1` | 0 | pass | final run id `RUN-ADMINISTRATUM-20260518-164612-079fbf`; dossier zip created. |
| `python .../administratum_agent_runner.py --no-color verify-dossier --latest` | 0 | pass | final run id `RUN-ADMINISTRATUM-20260518-164627-4b6060`; hash verification OK. |

## Static validation
| Validation | Result |
|---|---|
| JSON parse: all new schema files | pass |
| JSON parse: OSS register | pass |
| JSON parse: task receipt | pass |
| JSON parse: `--plain-json status` output pipeline | pass |
| Python compile: runner + dossier module | pass |
