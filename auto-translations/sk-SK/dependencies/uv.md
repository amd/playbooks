<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Inštalácia uv

[uv](https://docs.astral.sh/uv/) je správca balíkov/prostredí Pythonu, ktorý Agent Canvas používa na zostavenie svojho prostredia agent-server. Nainštalujte ho pomocou oficiálneho skriptu:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` sa inštaluje do `~/.local/bin`; uistite sa, že tento adresár je zahrnutý vo vašej premennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->