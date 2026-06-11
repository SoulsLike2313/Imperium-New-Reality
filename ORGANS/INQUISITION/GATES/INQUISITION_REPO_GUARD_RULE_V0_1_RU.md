
# Inquisition Repo Guard Rule V0.1

Назначение: не дать repo снова превратиться в склад времянки.

## Guard checks

Перед promotion/commit Inquisition должна уметь ответить:

1. Появились ли новые unregistered folders?
2. Появились ли runtime/evidence/screenshots/logs в source repo?
3. Появились ли tool-like scripts без Mechanicus паспорта?
4. Появились ли encoding/mojibake markers?
5. Появились ли write actions без safety декларации?
6. Есть ли local runtime outputs старше TTL-48?

## Blocking philosophy

- Новые runtime leaks в source repo: block.
- Новые unknown organ folders: block.
- Mojibake in source: block.
- Existing legacy mirror mass: не block, но остаётся visible debt lane.
- No tool passport: warning до массовой паспортизации.
