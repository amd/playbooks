<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installera uv

[uv](https://docs.astral.sh/uv/) är den Python-pakethanterare/miljöhanterare som Agent Canvas använder för att bygga sin agent-servermiljö. Installera den med det officiella skriptet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` installeras i `~/.local/bin`; se till att den katalogen finns med i din `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->