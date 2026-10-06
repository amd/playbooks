<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermes installeren

Installeer de Hermes agent CLI met het officiële installatieprogramma. De vlag `--skip-setup` zorgt ervoor dat de installatie zonder tussenkomst verloopt:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes wordt geïnstalleerd in `~/.local/bin`; zorg ervoor dat die map is opgenomen in je `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->