<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

<!-- @os:windows -->

1. ดาวน์โหลดตัวติดตั้งสำหรับ Windows 64-bit จาก [nodejs.org](https://nodejs.org/en/download/)
2. เรียกใช้ตัวติดตั้งและทำตามขั้นตอนที่แนะนำ
3. ตรวจสอบการติดตั้ง:
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

> **หมายเหตุ**: ดู [Node.js Downloads](https://nodejs.org/en/download/) สำหรับตัวเลือกการติดตั้งและแพลตฟอร์มเพิ่มเติม