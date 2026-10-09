<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Namestitev Hermes

Namestite agentski CLI Hermes z uradnim namestitvenim programom. Zastavica `--skip-setup` poskrbi, da namestitev poteka brez posredovanja uporabnika:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes se namesti v `~/.local/bin`; prepričajte se, da je ta mapa vključena v vaš `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->