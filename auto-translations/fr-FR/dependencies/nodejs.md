<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Téléchargez le programme d'installation Windows 64 bits depuis [nodejs.org](https://nodejs.org/en/download/)
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

> **Remarque** : Consultez [Téléchargements Node.js](https://nodejs.org/en/download/) pour d'autres options d'installation et plateformes.