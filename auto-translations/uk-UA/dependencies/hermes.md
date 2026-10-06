<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Встановлення Hermes

Встановіть CLI агента Hermes за допомогою офіційного інсталятора. Прапорець `--skip-setup` дозволяє виконати встановлення без інтерактивного режиму:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes встановлюється в `~/.local/bin`; переконайтеся, що цей каталог є у вашому `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->