<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS to zalecana wersja dla tej platformy.

<!-- @os:windows -->

1. Pobierz 64-bitowy instalator dla systemu Windows ze strony [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Uruchom instalator i postępuj zgodnie z instrukcjami
3. Zweryfikuj instalację:
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

> **Uwaga**: Zobacz [Pobieranie Node.js](https://nodejs.org/en/download/), aby poznać dodatkowe opcje instalacji i platformy.