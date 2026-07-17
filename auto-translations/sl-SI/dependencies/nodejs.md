<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS je priporočena različica za to platformo.

<!-- @os:windows -->

1. Prenesite namestitveni program za Windows 64-bit s [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Zaženite namestitveni program in sledite navodilom
3. Preverite namestitev:
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

> **Opomba**: Za dodatne možnosti namestitve in platforme glejte [Prenosi Node.js](https://nodejs.org/en/download/).