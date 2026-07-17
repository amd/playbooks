<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS هو الإصدار الموصى به لهذه المنصة.

<!-- @os:windows -->

1. قم بتنزيل مثبّت Windows 64-bit من [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. شغّل المثبّت واتبع التعليمات
3. تحقق من التثبيت:
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

> **ملاحظة**: راجع [تنزيلات Node.js](https://nodejs.org/en/download/) للاطلاع على خيارات تثبيت إضافية ومنصات أخرى.