<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A ds4-cockpit telepítése

A [ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) egy könnyű terminálfelület, amely kezeli a toolbox konténerek létrehozását, a modellsúlyok letöltését és a szerverek indítását. Telepítsd `pipx` segítségével:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

A `pipx` a belépési pontot a `~/.local/bin` könyvtárba telepíti; győződj meg róla, hogy ez a könyvtár szerepel a `PATH` változódban.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->