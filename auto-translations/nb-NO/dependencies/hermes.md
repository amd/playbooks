<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installere Hermes

Installer Hermes agent-CLI-et med den offisielle installasjonsprogrammet. Flagget `--skip-setup` gjør at installasjonen skjer uten interaksjon:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes installeres i `~/.local/bin`; sørg for at denne mappen er inkludert i `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->