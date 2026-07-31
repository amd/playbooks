<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS je odporúčaná verzia pre túto platformu.

<!-- @os:windows -->

1. Stiahnite si Windows 64-bit Installer zo stránky [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Spustite inštalátor a postupujte podľa pokynov
3. Overte inštaláciu:
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

> **Poznámka**: Ďalšie možnosti inštalácie a platformy nájdete na stránke [Node.js Downloads](https://nodejs.org/en/download/).