<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

Installatie van ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) is een lichte terminal-UI die zorgt voor het aanmaken van toolbox-containers, het downloaden van modelgewichten en het starten van servers. Installeer het met `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` installeert het entry point in `~/.local/bin`; zorg ervoor dat die map zich in uw `PATH` bevindt.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->