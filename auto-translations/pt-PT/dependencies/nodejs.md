<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Transfira o Instalador para Windows 64-bit em [nodejs.org](https://nodejs.org/en/download/)
2. Execute o instalador e siga as instruções
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

> **Nota**: Consulte [Transferências do Node.js](https://nodejs.org/en/download/) para obter opções de instalação adicionais e plataformas suportadas.