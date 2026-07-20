<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS ist die empfohlene Version für diese Plattform.

<!-- @os:windows -->

1. Laden Sie das 64-Bit-Installationsprogramm für Windows von [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi) herunter
2. Führen Sie das Installationsprogramm aus und folgen Sie den Anweisungen
3. Überprüfen Sie die Installation:
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

> **Hinweis**: Weitere Installationsoptionen und Plattformen finden Sie unter [Node.js Downloads](https://nodejs.org/en/download/).