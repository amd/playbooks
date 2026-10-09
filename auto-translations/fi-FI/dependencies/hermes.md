<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermesin asentaminen

Asenna Hermes-agentin CLI virallisella asennusohjelmalla. `--skip-setup`-lippu pitää asennuksen ilman valvontaa:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes asentuu hakemistoon `~/.local/bin`; varmista, että kyseinen hakemisto on `PATH`-muuttujassa.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->