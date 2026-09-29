<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. 從 [nodejs.org](https://nodejs.org/en/download/) 下載 Windows 64 位元安裝程式
2. 執行安裝程式並依照提示進行操作
3. 驗證安裝：
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

> **注意**：如需其他安裝選項與平台資訊，請參閱 [Node.js 下載頁面](https://nodejs.org/en/download/)。