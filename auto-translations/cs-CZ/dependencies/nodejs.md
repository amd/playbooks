<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Doporučenou verzí pro tuto platformu je Node.js 22.22.1 LTS.

<!-- @os:windows -->

1. Stáhněte instalační program pro Windows 64-bit z [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Spusťte instalační program a postupujte podle pokynů
3. Ověřte instalaci:
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

> **Poznámka**: Další možnosti instalace a platformy naleznete v části [Node.js Downloads](https://nodejs.org/en/download/).