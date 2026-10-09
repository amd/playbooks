<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installazione di Hermes

Installa la CLI dell'agente Hermes con l'installer ufficiale. Il flag `--skip-setup` mantiene l'installazione automatica:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes viene installato in `~/.local/bin`; assicurati che quella directory sia inclusa nella tua `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->