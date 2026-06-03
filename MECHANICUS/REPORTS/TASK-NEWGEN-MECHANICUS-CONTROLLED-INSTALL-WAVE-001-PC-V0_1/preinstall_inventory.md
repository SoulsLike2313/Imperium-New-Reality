# Preinstall Inventory

- task_id: TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1
- generated_at_utc: 2026-05-25T22:44:27Z

## State summary
- winget: True
- node: True
- npm: True
- python: True
- pip: True
- tool_7zip_cli: True
- tool_markdownlint: False
- tool_check_jsonschema: False
- tool_yamllint: False

## Fallback 7-Zip paths
- ProgramFiles: C:\Program Files\7-Zip\7z.exe (exists=True)
- ProgramFiles(x86): C:\Program Files (x86)\7-Zip\7z.exe (exists=False)

## Command checks
- [winget_where] exit=0 cmd=$ where winget
- [winget_version] exit=0 cmd=$ winget --version
- [winget_source_list] exit=0 cmd=$ winget source list
- [node_where] exit=0 cmd=$ where node
- [node_version] exit=0 cmd=$ node --version
- [npm_where] exit=0 cmd=$ where npm
- [npm_version] exit=0 cmd=$ npm --version
- [npm_prefix] exit=0 cmd=$ npm config get prefix
- [py_where] exit=0 cmd=$ where py
- [py_version] exit=0 cmd=$ py -V
- [py_pip_version] exit=0 cmd=$ py -m pip --version
- [python_where] exit=0 cmd=$ where python
- [python_version] exit=0 cmd=$ python --version
- [python_pip_version] exit=0 cmd=$ python -m pip --version
- [python_user_base] exit=0 cmd=$ python -m site --user-base
- [python_user_site] exit=0 cmd=$ python -m site --user-site
- [tool_7z_where] exit=1 cmd=$ where 7z
- [tool_7z_info] exit=1 cmd=$ 7z i
- [tool_markdownlint_where] exit=1 cmd=$ where markdownlint
- [tool_markdownlint_version] exit=1 cmd=$ markdownlint --version
- [tool_check_jsonschema_where] exit=1 cmd=$ where check-jsonschema
- [tool_check_jsonschema_version] exit=1 cmd=$ check-jsonschema --version
- [tool_python_module_check_jsonschema_version] exit=1 cmd=$ python -m check_jsonschema --version
- [tool_yamllint_where] exit=1 cmd=$ where yamllint
- [tool_yamllint_version] exit=1 cmd=$ yamllint --version
- [tool_python_module_yamllint_version] exit=1 cmd=$ python -m yamllint --version
