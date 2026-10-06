<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalarea Hermes

Instalați CLI-ul agentului Hermes folosind programul de instalare oficial. Flagul `--skip-setup` păstrează instalarea nesupravegheată:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes se instalează în `~/.local/bin`; asigurați-vă că acel director se află în `PATH`-ul dumneavoastră.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->