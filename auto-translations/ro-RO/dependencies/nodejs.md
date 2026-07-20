<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS este versiunea recomandată pentru această platformă.

<!-- @os:windows -->

1. Descărcați programul de instalare Windows pe 64 de biți de la [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Rulați programul de instalare și urmați instrucțiunile
3. Verificați instalarea:
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

> **Notă**: Consultați [Node.js Downloads](https://nodejs.org/en/download/) pentru opțiuni suplimentare de instalare și platforme.