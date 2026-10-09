<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง Hermes

ติดตั้ง Hermes agent CLI ด้วยตัวติดตั้งอย่างเป็นทางการ แฟล็ก `--skip-setup` จะทำให้การติดตั้งเป็นแบบไม่ต้องโต้ตอบ (unattended):

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes จะถูกติดตั้งไว้ใน `~/.local/bin` โปรดตรวจสอบให้แน่ใจว่าไดเรกทอรีดังกล่าวอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->