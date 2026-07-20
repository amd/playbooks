<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Bu platform için önerilen sürüm Node.js 22.22.1 LTS'dir.

<!-- @os:windows -->

1. [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi) adresinden Windows 64-bit Yükleyicisini indirin
2. Yükleyiciyi çalıştırın ve talimatları izleyin
3. Kurulumu doğrulayın:
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

> **Not**: Ek kurulum seçenekleri ve platformlar için bkz. [Node.js İndirmeleri](https://nodejs.org/en/download/)