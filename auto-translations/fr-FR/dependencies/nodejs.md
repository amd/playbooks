<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS est la version recommandée pour cette plateforme.

<!-- @os:windows -->

1. Téléchargez le programme d'installation Windows 64 bits depuis [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Exécutez le programme d'installation et suivez les instructions
3. Vérifiez l'installation :
```cmd
node --version
npm --version
```

<!-- @os:end -->

<!-- @os:linux -->

```bash
# Download and install Homebrew
curl -o- https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash

# Download and install Node.js:
brew install node@22

# Verify the Node.js version:
node -v # Should print "v22.22.1".

# Verify npm version:
npm -v # Should print "10.9.4".
```

<!-- @os:end -->

> **Remarque** : Consultez [Téléchargements Node.js](https://nodejs.org/en/download/) pour des options d'installation supplémentaires et d'autres plateformes.