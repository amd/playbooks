<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalowanie uv

[uv](https://docs.astral.sh/uv/) to menedżer pakietów/środowisk Pythona, którego Agent Canvas używa do budowania środowiska agent-server. Zainstaluj go za pomocą oficjalnego skryptu:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` instaluje się w `~/.local/bin`; upewnij się, że ten katalog znajduje się w Twojej zmiennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->