<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Het installeren van uv

[uv](https://docs.astral.sh/uv/) is de Python package/environment manager die Agent Canvas gebruikt om zijn agent-server-omgeving te bouwen. Installeer het met het officiële script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` installeert in `~/.local/bin`; zorg ervoor dat die map zich in je `PATH` bevindt.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->