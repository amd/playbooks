<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка OpenClaw

Установите OpenClaw с помощью официального установщика:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Флаги `--no-prompt --no-onboard` пропускают интерактивный мастер настройки, что необходимо для автоматических установок без участия пользователя; бэкенд модели настраивается отдельно.

> **Совет:** Если после установки появляется сообщение `command not found`, добавьте глобальную директорию bin из npm в PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Чтобы сделать это постоянным, добавьте строку выше в файл `~/.bashrc` или `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->