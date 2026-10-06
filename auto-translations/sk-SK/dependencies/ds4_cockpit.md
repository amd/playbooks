<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Inštalácia ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) je ľahké terminálové rozhranie (UI), ktoré sa stará o vytváranie toolbox kontajnerov, sťahovanie váh modelov a spúšťanie serverov. Nainštalujte ho pomocou `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` nainštaluje vstupný bod do `~/.local/bin`; uistite sa, že tento adresár je zahrnutý vo vašej premennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->