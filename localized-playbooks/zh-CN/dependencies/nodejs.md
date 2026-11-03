<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS 是此平台的推荐版本。

<!-- @os:windows -->

1. 从 [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi) 下载 Windows 64-bit Installer
2. 运行安装程序并按照提示操作
3. 验证安装：
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

> **注意**：有关更多安装选项和平台，请参阅 [Node.js Downloads](https://nodejs.org/en/download/)。
