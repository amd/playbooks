### Node.js

Node.js 22.22.1 LTS is the recommended version for this platform.

<!-- @os:windows -->

1. Download the Windows 64-bit Installer from [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Run the installer and follow the prompts
3. Verify installation:
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

> **Note**: See [Node.js Downloads](https://nodejs.org/en/download/) for additional installation options and platforms.
