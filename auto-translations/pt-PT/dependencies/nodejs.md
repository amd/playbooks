<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

O Node.js 22.22.1 LTS é a versão recomendada para esta plataforma.

<!-- @os:windows -->

1. Transfira o Instalador Windows de 64 bits em [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Execute o instalador e siga as instruções apresentadas
3. Verifique a instalação:
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

> **Nota**: Consulte [Node.js Downloads](https://nodejs.org/en/download/) para mais opções de instalação e plataformas.