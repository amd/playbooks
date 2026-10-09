<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### OpenClaw Kurulumu

OpenClaw'ı resmi yükleyici ile kurun:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-prompt --no-onboard` bayrakları, etkileşimli kurulum sihirbazını atlar; bu, denetimsiz kurulumlar için gereklidir. Model arka ucu ayrı olarak yapılandırılır.

> **İpucu:** Kurulumdan sonra `command not found` hatası görürseniz, npm'in global bin dizinini PATH'inize ekleyin:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Bunu kalıcı hale getirmek için yukarıdaki satırı `~/.bashrc` veya `~/.zshrc` dosyanıza ekleyin.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->