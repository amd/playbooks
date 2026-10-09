<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Namestitev ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je lahek terminalski uporabniški vmesnik, ki poskrbi za ustvarjanje vsebnikov toolbox, prenos uteži modelov in zagon strežnikov. Namestite ga z `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` namesti vstopno točko v `~/.local/bin`; poskrbite, da je ta mapa vključena v vaš `PATH`.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->