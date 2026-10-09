<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalarea uv

[uv](https://docs.astral.sh/uv/) este managerul de pachete/medii Python pe care Agent Canvas îl folosește pentru a construi mediul agent-server. Instalați-l cu scriptul oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` se instalează în `~/.local/bin`; asigurați-vă că acel director se află în `PATH`-ul dumneavoastră.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->