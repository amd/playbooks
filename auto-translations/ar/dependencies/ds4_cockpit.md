<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) هو واجهة طرفية خفيفة تتولى إنشاء حاويات toolbox، وتنزيل أوزان النماذج، وتشغيل الخوادم. ثبّتها باستخدام `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

تقوم `pipx` بتثبيت نقطة الدخول في `~/.local/bin`؛ تأكد من أن هذا المسار موجود ضمن `PATH` الخاص بك.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->