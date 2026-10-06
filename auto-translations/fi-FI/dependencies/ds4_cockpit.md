<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4-cockpitin asentaminen

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) on kevyt pääteliittymä (terminal UI), joka hoitaa toolbox-säilöjen luomisen, mallien painojen lataamisen ja palvelinten käynnistämisen. Asenna se `pipx`-työkalulla:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` asentaa ohjelman käynnistyspisteen hakemistoon `~/.local/bin`; varmista, että kyseinen hakemisto on `PATH`-muuttujassasi.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->