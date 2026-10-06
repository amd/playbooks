<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instaliranje uv alata

[uv](https://docs.astral.sh/uv/) je Python menadžer paketa/okruženja koji Agent Canvas koristi za izgradnju svog agent-server okruženja. Instalirajte ga pomoću zvaničnog skripta:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` se instalira u `~/.local/bin`; proverite da li se taj direktorijum nalazi u vašem `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->