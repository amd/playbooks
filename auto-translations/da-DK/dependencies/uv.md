<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation af uv

[uv](https://docs.astral.sh/uv/) er den Python-pakke-/miljøhåndtering, som Agent Canvas bruger til at bygge sit agent-server-miljø. Installer det med det officielle script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` installeres i `~/.local/bin`; sørg for, at den mappe er inkluderet i din `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->