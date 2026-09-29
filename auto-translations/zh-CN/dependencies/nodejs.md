<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. 从 [nodejs.org](https://nodejs.org/en/download/) 下载 Windows 64 位安装程序
2. 运行安装程序并按照提示进行操作
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

> **注意**：有关其他安装选项和平台的信息，请参阅 [Node.js Downloads](https://nodejs.org/en/download/)。