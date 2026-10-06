<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation von Hermes

Installieren Sie die Hermes-Agent-CLI mit dem offiziellen Installer. Das Flag `--skip-setup` sorgt dafür, dass die Installation unbeaufsichtigt abläuft:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes wird in `~/.local/bin` installiert; stellen Sie sicher, dass dieses Verzeichnis in Ihrem `PATH` enthalten ist.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->