<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS on suositeltu versio tälle alustalle.

<!-- @os:windows -->

1. Lataa Windows 64-bit -asennusohjelma osoitteesta [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Suorita asennusohjelma ja seuraa ohjeita
3. Vahvista asennus:
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

> **Huomautus**: Katso [Node.js-lataukset](https://nodejs.org/en/download/) saadaksesi lisää asennusvaihtoehtoja ja alustoja.