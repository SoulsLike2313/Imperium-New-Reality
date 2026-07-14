# IMPERIUM_PHASE6_TOOL_PATH_IDENTITY_FIX_0004

Этот пакет не запускает diagnostic повторно. Он использует уже созданный единственный live evidence и исправляет только сравнение одного и того же Windows executable в формах `\\?\C:\...` и `C:\...`. SHA-256 и запрет PATH resolution остаются обязательными.
