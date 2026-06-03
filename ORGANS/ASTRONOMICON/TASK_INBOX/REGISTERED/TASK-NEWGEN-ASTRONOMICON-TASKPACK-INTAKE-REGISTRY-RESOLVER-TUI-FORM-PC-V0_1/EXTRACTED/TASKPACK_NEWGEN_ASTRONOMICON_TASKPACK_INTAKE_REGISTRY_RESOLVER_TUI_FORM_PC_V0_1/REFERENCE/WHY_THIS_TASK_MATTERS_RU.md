# Зачем нужен этот шаг простыми словами

Это превращает taskpack ZIP в настоящую задачу IMPERIUM.

Раньше ZIP просто давался Servitor-у.
Теперь Astronomicon должен принять ZIP, проверить, распаковать, зарегистрировать, пометить как следующий ожидаемый task и дать Owner-у task_id.

После этого Owner сможет сказать Servitor-у только:
`TASK_ID: ...`
`start task`

И Servitor должен сам найти задачу через Astronomicon.
