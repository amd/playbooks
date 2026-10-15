<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Download de Windows 64-bit installer van [nodejs.org](https://nodejs.org/en/download/)
2. Voer het installatieprogramma uit en volg de instructies
3. Controleer de installatie:
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

> **Opmerking**: Zie [Node.js Downloads](https://nodejs.org/en/download/) voor aanvullende installatieopties en platforms.