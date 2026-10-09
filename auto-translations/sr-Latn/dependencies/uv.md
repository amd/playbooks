<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instaliranje uv

[uv](https://docs.astral.sh/uv/) je Python menadžer paketa/okruženja koji Agent Canvas koristi za izgradnju svog agent-server okruženja. Instalirajte ga pomoću zvanične skripte:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` se instalira u `~/.local/bin`; proverite da se taj direktorijum nalazi u vašoj `PATH` promenljivoj.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->