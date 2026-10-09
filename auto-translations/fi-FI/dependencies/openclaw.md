<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### OpenClaw’n asentaminen

Asenna OpenClaw virallisella asennusohjelmalla:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Liput `--no-prompt --no-onboard` ohittavat interaktiivisen asennusvelhon, mikä on tarpeen valvomattomissa asennuksissa; mallin taustajärjestelmä määritetään erikseen.

> **Vinkki:** Jos näet asennuksen jälkeen viestin `command not found`, lisää npm:n globaali bin-hakemisto PATH-muuttujaan:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Tehdäksesi tästä pysyvän, lisää yllä oleva rivi `~/.bashrc`- tai `~/.zshrc`-tiedostoosi.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->