# Data Atlas / Evidence Migration Coupling V0.1

Data Atlas должен показывать evidence не как россыпь файлов, а как migration entities:

- source path;
- current storage zone;
- risk type;
- migration lane;
- proposed vault pack group;
- fixture exception status;
- owner-review requirement;
- safe-cache-delete flag.

Цель: увидеть, что остаётся в source, что уходит в Vault, что требует review, а что является cache.
