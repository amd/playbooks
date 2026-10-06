<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation de Hermes

Installez l'interface de ligne de commande de l'agent Hermes à l'aide du programme d'installation officiel. L'indicateur `--skip-setup` permet de réaliser l'installation sans intervention de l'utilisateur :

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes s'installe dans `~/.local/bin`; assurez-vous que ce répertoire figure dans votre `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->