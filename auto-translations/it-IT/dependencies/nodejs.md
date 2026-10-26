<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Scarica l'Installer a 64 bit per Windows da [nodejs.org](https://nodejs.org/en/download/)
2. Esegui l'installer e segui le istruzioni
3. Verifica l'installazione:
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

> **Nota**: Consulta [Node.js Downloads](https://nodejs.org/en/download/) per ulteriori opzioni di installazione e piattaforme.