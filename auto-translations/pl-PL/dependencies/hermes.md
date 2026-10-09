<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalacja Hermes

Zainstaluj CLI agenta Hermes za pomocą oficjalnego instalatora. Flaga `--skip-setup` pozwala przeprowadzić instalację bez interakcji użytkownika:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes instaluje się w `~/.local/bin`; upewnij się, że ten katalog znajduje się w Twojej zmiennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->