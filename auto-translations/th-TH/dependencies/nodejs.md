<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Node.js

Node.js 22.22.1 LTS เป็นเวอร์ชันที่แนะนำสำหรับแพลตฟอร์มนี้

<!-- @os:windows -->

1. ดาวน์โหลด Windows 64-bit Installer จาก [nodejs.org](https://nodejs.org/dist/v20.19.2/node-v20.19.2-x64.msi)
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

> **หมายเหตุ**: ดู [Node.js Downloads](https://nodejs.org/en/download/) สำหรับตัวเลือกการติดตั้งเพิ่มเติมและแพลตฟอร์มอื่นๆ