<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS er den anbefalte versjonen for denne plattformen.

<!-- @os:windows -->

1. Last ned Windows 64-bit-installasjonsprogrammet fra [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Kjør installasjonsprogrammet og følg instruksjonene
3. Bekreft installasjonen:
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

> **Merk**: Se [Node.js-nedlastinger](https://nodejs.org/en/download/) for flere installasjonsalternativer og plattformer.