<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation de Hermes

Installez l'interface en ligne de commande de l'agent Hermes avec l'installateur officiel. Le drapeau `--skip-setup` permet une installation sans intervention :

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes s'installe dans `~/.local/bin` ; assurez-vous que ce répertoire se trouve dans votre `PATH`.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->