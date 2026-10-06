<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### uv:n asentaminen

[uv](https://docs.astral.sh/uv/) on Python-paketti-/ympäristönhallintatyökalu, jota Agent Canvas käyttää agentti-palvelinympäristönsä rakentamiseen. Asenna se virallisella skriptillä:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` asennetaan hakemistoon `~/.local/bin`; varmista, että kyseinen hakemisto on `PATH`-muuttujassa.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->