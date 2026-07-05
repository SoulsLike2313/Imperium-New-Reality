# TESTS — MECHANICUS-STRICT-BUILD-LANE-RUNNER-EXIT-CODE-FIX-0001

Validator checks:

- patcher installed and applies cleanly;
- runner contains v0.2 marker and legacy v0.1 marker;
- runner exits 0 when report is PASS;
- all detected build targets still pass;
- base strict build validator passes;
- false-negative warning is removed;
- planner still does not report STRICT_BUILD_LANE_REQUIRED.
