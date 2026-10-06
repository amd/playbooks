<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation von uv

[uv](https://docs.astral.sh/uv/) ist der Python-Paket-/Umgebungsmanager, den Agent Canvas zum Erstellen seiner Agent-Server-Umgebung verwendet. Installieren Sie es mit dem offiziellen Skript:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` wird in `~/.local/bin` installiert; stellen Sie sicher, dass sich dieses Verzeichnis in Ihrem `PATH` befindet.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->