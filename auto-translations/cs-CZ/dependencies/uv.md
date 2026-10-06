<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalace uv

[uv](https://docs.astral.sh/uv/) je správce balíčků a prostředí Pythonu, který Agent Canvas používá k vytvoření svého prostředí agent-server. Nainstalujte ho pomocí oficiálního skriptu:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` se instaluje do `~/.local/bin`; ujistěte se, že je tento adresář zahrnut ve vaší proměnné `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->