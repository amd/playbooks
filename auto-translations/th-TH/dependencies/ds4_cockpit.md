<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) เป็น UI แบบเทอร์มินัลที่มีขนาดเล็ก ซึ่งจัดการการสร้างคอนเทนเนอร์ toolbox การดาวน์โหลดน้ำหนักของโมเดล และการเริ่มต้นเซิร์ฟเวอร์ ติดตั้งได้ด้วย `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` จะติดตั้ง entry point ไว้ที่ `~/.local/bin` โปรดตรวจสอบให้แน่ใจว่าไดเรกทอรีดังกล่าวอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->