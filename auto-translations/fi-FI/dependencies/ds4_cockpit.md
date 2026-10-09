<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4-cockpit-asennus

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) on kevyt pääte-UI, joka hoitaa toolbox-konttien luomisen, mallipainojen lataamisen ja palvelinten käynnistämisen. Asenna se `pipx`-työkalulla:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` asentaa aloituspisteen hakemistoon `~/.local/bin`; varmista, että kyseinen hakemisto on `PATH`-muuttujassa.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->