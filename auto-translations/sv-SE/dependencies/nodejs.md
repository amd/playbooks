<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS är den rekommenderade versionen för denna plattform.

<!-- @os:windows -->

1. Ladda ner Windows 64-bit-installationsprogrammet från [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Kör installationsprogrammet och följ anvisningarna
3. Verifiera installationen:
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

> **Obs**: Se [Node.js Downloads](https://nodejs.org/en/download/) för ytterligare installationsalternativ och plattformar.