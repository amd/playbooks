<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installere uv

[uv](https://docs.astral.sh/uv/) er Python-pakke-/miljøbehandleren Agent Canvas bruker til å bygge sitt agent-server-miljø. Installer den med det offisielle skriptet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` installeres i `~/.local/bin`; sørg for at denne mappen er i `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->