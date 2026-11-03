<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Baixe o instalador de 64 bits para Windows em [nodejs.org](https://nodejs.org/en/download/)
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

> **Observação**: Consulte [Node.js Downloads](https://nodejs.org/en/download/) para outras opções de instalação e plataformas.