<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalar o uv

O [uv](https://docs.astral.sh/uv/) é o gestor de pacotes/ambientes Python que o Agent Canvas utiliza para criar o seu ambiente de agent-server. Instale-o com o script oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O `uv` é instalado em `~/.local/bin`; certifique-se de que esse diretório está no seu `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->