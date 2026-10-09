<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalando o uv

[uv](https://docs.astral.sh/uv/) é o gerenciador de pacotes/ambientes Python que o Agent Canvas usa para criar seu ambiente de agent-server. Instale-o com o script oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O `uv` é instalado em `~/.local/bin`; certifique-se de que esse diretório esteja no seu `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->