<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка uv

[uv](https://docs.astral.sh/uv/) — это менеджер пакетов/окружений Python, который Agent Canvas использует для создания среды агент-сервера. Установите его с помощью официального скрипта:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` устанавливается в `~/.local/bin`; убедитесь, что этот каталог указан в вашей переменной `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->