# TESTS — MECHANICUS-STRICT-BUILD-LANE-RUNNER-EXIT-CODE-FIX-0002

Validator checks:

- runner v0.2 full replacement installed with legacy marker;
- runner exits 0 when report is PASS;
- all detected build targets still pass;
- base strict build validator passes;
- false-negative warning is removed;
- planner still does not report STRICT_BUILD_LANE_REQUIRED.
