<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Namestitev uv

[uv](https://docs.astral.sh/uv/) je upravljalnik paketov/okolij za Python, ki ga Agent Canvas uporablja za izgradnjo svojega okolja agent-server. Namestite ga z uradnim skriptom:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` se namesti v `~/.local/bin`; prepričajte se, da je ta mapa vključena v vašo spremenljivko `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->