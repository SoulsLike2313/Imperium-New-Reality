# Compliance Checker Contract

Compliance checker V0.1 verifies at minimum:

- requirement rows with unfinished status;
- DONE rows without evidence paths;
- missing matrix file;
- malformed JSON rows.

Output:

- JSON summary
- markdown summary
- verdict (`PASS|WARN|FAIL`)

