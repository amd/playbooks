<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4-cockpit Kurulumu

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox), toolbox konteynerleri oluşturmayı, model ağırlıklarını indirmeyi ve sunucuları başlatmayı yöneten hafif bir terminal arayüzüdür. `pipx` ile kurun:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx`, giriş noktasını `~/.local/bin` dizinine kurar; bu dizinin `PATH` üzerinde olduğundan emin olun.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->