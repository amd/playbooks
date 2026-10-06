<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalace Hermes

Nainstalujte agenta Hermes CLI pomocí oficiálního instalačního programu. Příznak `--skip-setup` zajistí instalaci bez nutnosti zásahu uživatele:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes se nainstaluje do `~/.local/bin`; ujistěte se, že je tento adresář ve vaší proměnné `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->