<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation de uv

[uv](https://docs.astral.sh/uv/) est le gestionnaire de paquets/d'environnements Python qu'utilise Agent Canvas pour construire son environnement de serveur d'agent. Installez-le avec le script officiel :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` s'installe dans `~/.local/bin`; assurez-vous que ce répertoire figure dans votre `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->