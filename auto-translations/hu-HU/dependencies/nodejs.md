<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

A Node.js 22.22.1 LTS az ajánlott verzió ehhez a platformhoz.

<!-- @os:windows -->

1. Töltse le a Windows 64-bites telepítőt a [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi) oldalról
2. Futtassa a telepítőt, és kövesse az utasításokat
3. Ellenőrizze a telepítést:
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

> **Megjegyzés**: További telepítési lehetőségekért és platformokért lásd a [Node.js letöltések](https://nodejs.org/en/download/) oldalt.