<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت OpenClaw

قم بتثبيت OpenClaw باستخدام المثبّت الرسمي:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

تعمل العلامتان `--no-prompt --no-onboard` على تخطي معالج الإعداد التفاعلي، وهو أمر مطلوب لعمليات التثبيت غير المراقَبة؛ أما إعداد نموذج الواجهة الخلفية فيتم بشكل منفصل.

> **ملاحظة:** إذا ظهرت لديك رسالة `command not found` بعد التثبيت، أضف دليل npm العام للملفات التنفيذية إلى متغير PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> لجعل هذا التغيير دائمًا، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc` الخاص بك.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->