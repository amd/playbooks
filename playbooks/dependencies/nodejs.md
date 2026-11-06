<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. Download the Windows 64-bit Installer from [nodejs.org](https://nodejs.org/en/download/)
2. Run the installer and follow the prompts
3. Verify installation:
```cmd
node --version
npm --version
```

> **Check the version range your tool supports.** The current release on nodejs.org is often
> newer than a given tool's supported range, and installing outside that range can fail with
> native-build or `EBADPLATFORM` errors. Use
> [nvm-windows](https://github.com/coreybutler/nvm-windows) to install and select a specific
> version:
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

> **Note**: See [Node.js Downloads](https://nodejs.org/en/download/) for additional installation options and platforms.
