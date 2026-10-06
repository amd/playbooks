<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка OpenClaw

Установите OpenClaw с помощью официального установщика:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Флаги `--no-prompt --no-onboard` пропускают интерактивный мастер настройки, что необходимо для автоматической установки без участия пользователя; серверная часть модели настраивается отдельно.

> **Совет:** Если после установки появляется сообщение `command not found`, добавьте глобальную папку bin пакета npm в переменную PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Чтобы сделать это изменение постоянным, добавьте указанную выше строку в файл `~/.bashrc` или `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->