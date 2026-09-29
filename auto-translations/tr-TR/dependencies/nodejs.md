<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. [nodejs.org](https://nodejs.org/en/download/) adresinden Windows 64-bit Yükleyicisini indirin
2. Yükleyiciyi çalıştırın ve yönergeleri izleyin
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

> **Not**: Ek kurulum seçenekleri ve platformlar için [Node.js İndirmeleri](https://nodejs.org/en/download/) sayfasına bakın.