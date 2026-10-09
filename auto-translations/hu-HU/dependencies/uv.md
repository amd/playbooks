<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A uv telepítése

A [uv](https://docs.astral.sh/uv/) az a Python csomag-/környezetkezelő, amelyet az Agent Canvas az ügynök-szerver (agent-server) környezetének felépítéséhez használ. Telepítsd a hivatalos szkripttel:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

A `uv` a `~/.local/bin` könyvtárba települ; győződj meg róla, hogy ez a könyvtár szerepel a `PATH` változódban.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->