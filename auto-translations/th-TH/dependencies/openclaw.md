<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง OpenClaw

ติดตั้ง OpenClaw ด้วยตัวติดตั้งอย่างเป็นทางการ:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

แฟล็ก `--no-prompt --no-onboard` จะข้ามตัวช่วยตั้งค่าแบบโต้ตอบ ซึ่งจำเป็นสำหรับการติดตั้งแบบไม่ต้องมีผู้ดูแล ส่วนแบ็กเอนด์ของโมเดลจะถูกกำหนดค่าแยกต่างหาก

> **เคล็ดลับ:** หากคุณเห็น `command not found` หลังการติดตั้ง ให้เพิ่มไดเรกทอรี global bin ของ npm ลงใน PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> หากต้องการให้การตั้งค่านี้มีผลถาวร ให้เพิ่มบรรทัดด้านบนลงในไฟล์ `~/.bashrc` หรือ `~/.zshrc` ของคุณ

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->