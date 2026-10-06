<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalando o Hermes

Instale o CLI do agente Hermes com o instalador oficial. A flag `--skip-setup` mantém a instalação não interativa:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

O Hermes é instalado em `~/.local/bin`; certifique-se de que esse diretório esteja no seu `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->