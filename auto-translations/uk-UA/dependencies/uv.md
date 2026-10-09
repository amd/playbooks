<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Встановлення uv

[uv](https://docs.astral.sh/uv/) — це менеджер пакетів/середовищ Python, який Agent Canvas використовує для побудови середовища сервера агента. Встановіть його за допомогою офіційного скрипту:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` встановлюється в `~/.local/bin`; переконайтеся, що цей каталог вказано у вашому `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->