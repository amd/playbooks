<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Ladda ner installationsprogrammet för Windows 64-bitar från [nodejs.org](https://nodejs.org/en/download/)
2. Kör installationsprogrammet och följ instruktionerna
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