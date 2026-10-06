<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง uv

[uv](https://docs.astral.sh/uv/) คือตัวจัดการแพ็กเกจ/สภาพแวดล้อม Python ที่ Agent Canvas ใช้สร้างสภาพแวดล้อมของ agent-server ติดตั้งได้ด้วยสคริปต์อย่างเป็นทางการ:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` จะถูกติดตั้งไว้ใน `~/.local/bin` ตรวจสอบให้แน่ใจว่าไดเรกทอรีดังกล่าวอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->