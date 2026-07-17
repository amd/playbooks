<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS는 이 플랫폼에 권장되는 버전입니다.

<!-- @os:windows -->

1. [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)에서 Windows 64비트 설치 프로그램을 다운로드합니다.
2. 설치 프로그램을 실행하고 안내에 따릅니다.
3. 설치를 확인합니다:
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

> **참고**: 추가 설치 옵션 및 플랫폼에 대해서는 [Node.js 다운로드](https://nodejs.org/en/download/)를 참조하십시오.