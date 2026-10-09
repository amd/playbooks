<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installera Hermes

Installera agent-CLI:t Hermes med det officiella installationsprogrammet. Flaggan `--skip-setup` gör installationen obevakad:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes installeras i `~/.local/bin`; se till att den katalogen finns med i din `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->