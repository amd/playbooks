<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Namestitev OpenClaw

Namestite OpenClaw z uradnim namestitvenim programom:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Zastavici `--no-prompt --no-onboard` preskočita interaktivnega čarovnika za nastavitev, kar je potrebno za nenadzorovane namestitve; zaledje modela se konfigurira ločeno.

> **Nasvet:** Če po namestitvi vidite `command not found`, dodajte npm-ov globalni bin direktorij v PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da bo to trajno, dodajte zgornjo vrstico v svojo datoteko `~/.bashrc` ali `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->