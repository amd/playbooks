<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. 从 [nodejs.org](https://nodejs.org/en/download/) 下载 Windows 64 位安装程序
2. 运行安装程序并按照提示操作
3. 验证安装：
```cmd
node --version
npm --version
```

> **检查你的工具所支持的版本范围。** nodejs.org 上的当前发行版通常比某个工具所支持的版本范围要新，
> 安装超出该范围的版本可能会出现原生构建错误或 `EBADPLATFORM` 错误。可以使用
> [nvm-windows](https://github.com/coreybutler/nvm-windows) 来安装并选择特定版本：
>
> ```cmd
> nvm install 24.10.0
> nvm use 24.10.0
> ```

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

> **注意**：有关其他安装选项和平台，请参阅 [Node.js 下载](https://nodejs.org/en/download/)。