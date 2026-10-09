<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A Hermes telepítése

Telepítsd a Hermes agent CLI-t a hivatalos telepítővel. A `--skip-setup` jelző felügyelet nélküli telepítést tesz lehetővé:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

A Hermes a `~/.local/bin` könyvtárba települ; győződj meg róla, hogy ez a könyvtár szerepel a `PATH` változódban.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->