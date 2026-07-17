<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS はこのプラットフォームで推奨されるバージョンです。

<!-- @os:windows -->

1. [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi) から Windows 64ビット インストーラーをダウンロードします
2. インストーラーを実行し、プロンプトに従います
3. インストールを確認します:
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

> **注意**: 追加のインストールオプションやプラットフォームについては、[Node.js ダウンロード](https://nodejs.org/en/download/) を参照してください。