<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalace Hermes

Nainstalujte agentní CLI Hermes pomocí oficiálního instalátoru. Příznak `--skip-setup` zajistí neinteraktivní instalaci:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes se instaluje do `~/.local/bin`; ujistěte se, že je tento adresář zahrnut ve vaší proměnné `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->