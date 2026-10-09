<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง uv

[uv](https://docs.astral.sh/uv/) คือตัวจัดการแพ็กเกจ/สภาพแวดล้อม Python ที่ Agent Canvas ใช้ในการสร้างสภาพแวดล้อม agent-server ของตน ติดตั้งได้ด้วยสคริปต์ทางการ:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` จะถูกติดตั้งไว้ใน `~/.local/bin` ตรวจสอบให้แน่ใจว่าไดเรกทอรีนั้นอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->