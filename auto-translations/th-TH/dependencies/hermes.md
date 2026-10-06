<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง Hermes

ติดตั้ง Hermes agent CLI ด้วยตัวติดตั้งอย่างเป็นทางการ แฟล็ก `--skip-setup` ช่วยให้การติดตั้งดำเนินการแบบไม่ต้องมีการโต้ตอบ:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes จะถูกติดตั้งไว้ใน `~/.local/bin` ตรวจสอบให้แน่ใจว่าไดเรกทอรีดังกล่าวอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->