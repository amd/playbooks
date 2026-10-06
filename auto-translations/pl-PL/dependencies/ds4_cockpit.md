<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalacja ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) to lekki interfejs terminalowy, który zajmuje się tworzeniem kontenerów toolbox, pobieraniem wag modeli i uruchamianiem serwerów. Zainstaluj go za pomocą `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` instaluje punkt wejścia w `~/.local/bin`; upewnij się, że ten katalog znajduje się w Twojej zmiennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->