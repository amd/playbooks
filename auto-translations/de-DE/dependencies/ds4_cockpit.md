<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation von ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) ist eine schlanke Terminal-UI, die das Erstellen von Toolbox-Containern, das Herunterladen von Modellgewichten und das Starten von Servern übernimmt. Installiere es mit `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` installiert den Einstiegspunkt in `~/.local/bin`; stelle sicher, dass dieses Verzeichnis in deinem `PATH` enthalten ist.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->