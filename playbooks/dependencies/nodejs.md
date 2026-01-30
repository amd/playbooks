### Node.js

Node.js 20.19.2 LTS (Iron) is the recommended version for this platform.

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
curl -fsSL https://nodejs.org/dist/v20.19.2/node-v20.19.2-linux-x64.tar.xz | tar -xJ
sudo mv node-v20.19.2-linux-x64 /usr/local/node
sudo ln -s /usr/local/node/bin/node /usr/local/bin/node
sudo ln -s /usr/local/node/bin/npm /usr/local/bin/npm
```

<!-- @os:end -->

> **Note**: See [Node.js Downloads](https://nodejs.org/en/download/) for additional installation options and platforms.
