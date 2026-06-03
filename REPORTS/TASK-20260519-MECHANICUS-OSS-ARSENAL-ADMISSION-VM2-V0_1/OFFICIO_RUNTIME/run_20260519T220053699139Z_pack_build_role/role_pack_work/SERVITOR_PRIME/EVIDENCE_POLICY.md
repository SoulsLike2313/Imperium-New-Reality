# Evidence Policy V0.1

Core law:

- No evidence = no DONE.
- No screenshot = no visual DONE.
- No remote hash = no transfer DONE.
- No git status = no clean claim.
- No requirement matrix row = missing requirement.

Minimum evidence map:

| Claim type | Required evidence |
|---|---|
| UI/visual change | before/after screenshot or `BLOCKED_VISUAL_EVIDENCE_MISSING` |
| Color/rich claim | screenshot or terminal ANSI diagnostic |
| Git clean claim | `git status --short` output |
| Push claim | remote HEAD/hash proof or exact GitHub commit URL |
| Transfer claim | exact path + SHA256 + timestamp receipt |
| Schema claim | validator/check output |
| Response contract claim | compliance-check output |
| Done claim | requirement matrix row evidence |

