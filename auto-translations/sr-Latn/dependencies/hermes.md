<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instaliranje Hermes-a

Instalirajte Hermes agent CLI pomoću zvaničnog instalacionog programa. Oznaka `--skip-setup` omogućava nenadgledanu instalaciju:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes se instalira u `~/.local/bin`; obavezno se postarajte da se taj direktorijum nalazi u vašoj promenljivoj `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->