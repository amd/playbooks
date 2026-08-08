<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS היא הגרסה המומלצת עבור פלטפורמה זו.

<!-- @os:windows -->

1. הורידו את מתקין 64-bit עבור Windows מתוך [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
2. הריצו את המתקין ופעלו לפי ההנחיות
3. וודאו שההתקנה בוצעה בהצלחה:
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