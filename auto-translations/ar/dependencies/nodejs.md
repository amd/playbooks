<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. قم بتنزيل مثبت Windows 64-bit من [nodejs.org](https://nodejs.org/en/download/)
2. شغّل المثبت واتبع التعليمات
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

> **ملاحظة**: راجع [تنزيلات Node.js](https://nodejs.org/en/download/) للحصول على خيارات ومنصات تثبيت إضافية.