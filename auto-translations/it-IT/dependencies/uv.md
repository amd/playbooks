<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installazione di uv

[uv](https://docs.astral.sh/uv/) è il gestore di pacchetti/ambienti Python che Agent Canvas utilizza per costruire il proprio ambiente agent-server. Installalo con lo script ufficiale:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` si installa in `~/.local/bin`; assicurati che quella directory sia inclusa nel tuo `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->