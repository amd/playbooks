<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Το Node.js 22.22.1 LTS είναι η συνιστώμενη έκδοση για αυτή την πλατφόρμα.

<!-- @os:windows -->

1. Κατεβάστε το Windows 64-bit Installer από το [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. Εκτελέστε το πρόγραμμα εγκατάστασης και ακολουθήστε τις οδηγίες
3. Επαληθεύστε την εγκατάσταση:
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

> **Σημείωση**: Ανατρέξτε στο [Node.js Downloads](https://nodejs.org/en/download/) για επιπλέον επιλογές εγκατάστασης και πλατφόρμες.