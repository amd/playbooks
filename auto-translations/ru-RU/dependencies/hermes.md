<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка Hermes

Установите агентский CLI Hermes с помощью официального установщика. Флаг `--skip-setup` обеспечивает автоматическую установку без запросов:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes устанавливается в `~/.local/bin`; убедитесь, что этот каталог указан в вашей переменной `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->