<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت Hermes

قم بتثبيت واجهة سطر الأوامر لوكيل Hermes باستخدام المثبت الرسمي. يحافظ العلم `--skip-setup` على التثبيت دون تدخل:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

يُثبَّت Hermes في `~/.local/bin`؛ تأكد من أن هذا الدليل موجود ضمن `PATH` الخاص بك.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->