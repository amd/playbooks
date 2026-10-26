<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. הורידו את מתקין ה-Windows 64-bit מ-[nodejs.org](https://nodejs.org/en/download/)
2. הריצו את המתקין ופעלו לפי ההנחיות
3. ודאו שההתקנה בוצעה בהצלחה:
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

> **הערה**: ראו [Node.js Downloads](https://nodejs.org/en/download/) לאפשרויות התקנה ופלטפורמות נוספות.