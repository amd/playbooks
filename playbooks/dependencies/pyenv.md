<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### pyenv

[pyenv](https://github.com/pyenv-win/pyenv-win) lets you install and switch between multiple Python versions without affecting the system Python. Playbooks use it to select the specific Python version they require.

<!-- @os:windows -->

1. Install pyenv-win from PowerShell:
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

2. **Close and reopen PowerShell** so `pyenv` is available on your `PATH`.

3. Verify the installation:
```powershell
pyenv --version
```

<!-- @os:end -->

> **Note**: See the [pyenv-win documentation](https://github.com/pyenv-win/pyenv-win) for more options. If `pyenv` is not recognized after installing, open a new terminal or confirm the pyenv paths were added to your user `PATH`.
