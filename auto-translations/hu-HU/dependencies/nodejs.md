<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Töltsd le a Windows 64-bites telepítőt a [nodejs.org](https://nodejs.org/en/download/) oldalról
2. Futtasd a telepítőt, és kövesd az utasításokat
3. Ellenőrizd a telepítést:
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

> **Megjegyzés**: A további telepítési lehetőségekért és platformokért lásd a [Node.js Downloads](https://nodejs.org/en/download/) oldalt.