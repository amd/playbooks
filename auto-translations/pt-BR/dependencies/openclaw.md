<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalando o OpenClaw

Instale o OpenClaw com o instalador oficial:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

As flags `--no-prompt --no-onboard` pulam o assistente de configuração interativo, o que é necessário para instalações automatizadas; o backend do modelo é configurado separadamente.

> **Dica:** Se você ver `command not found` após a instalação, adicione o diretório bin global do npm ao seu PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Para tornar isso permanente, adicione a linha acima ao seu arquivo `~/.bashrc` ou `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->