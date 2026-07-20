<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS es la versión recomendada para esta plataforma.

<!-- @os:windows -->

1. Descarga el instalador de 64 bits para Windows desde [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Ejecuta el instalador y sigue las indicaciones
3. Verifica la instalación:
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

> **Nota**: Consulta [Descargas de Node.js](https://nodejs.org/en/download/) para ver opciones de instalación adicionales y otras plataformas.