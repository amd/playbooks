<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Встановлення OpenClaw

Встановіть OpenClaw за допомогою офіційного інсталятора:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Прапорці `--no-prompt --no-onboard` пропускають інтерактивний майстер налаштування, що необхідно для встановлення без втручання користувача; бекенд моделі налаштовується окремо.

> **Порада:** Якщо після встановлення ви бачите `command not found`, додайте глобальний каталог bin для npm до PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Щоб зробити це постійним, додайте наведений вище рядок до файлу `~/.bashrc` або `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->