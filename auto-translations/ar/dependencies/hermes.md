<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت Hermes

قم بتثبيت واجهة سطر الأوامر لوكيل Hermes باستخدام المُثبِّت الرسمي. تحافظ العلامة `--skip-setup` على التثبيت بدون تدخل يدوي:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

يتم تثبيت Hermes في `~/.local/bin`؛ تأكد من أن هذا المسار موجود ضمن متغير `PATH` الخاص بك.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->