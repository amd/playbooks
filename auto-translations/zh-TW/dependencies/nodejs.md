<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS 是此平台的建議版本。

<!-- @os:windows -->

1. 從 [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi) 下載 Windows 64 位元安裝程式
2. 執行安裝程式並依照提示操作
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

> **注意**：請參閱 [Node.js 下載頁面](https://nodejs.org/en/download/) 以取得其他安裝選項與平台資訊。