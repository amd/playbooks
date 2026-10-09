<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت uv

[uv](https://docs.astral.sh/uv/) هو مدير حزم/بيئات Python الذي يستخدمه Agent Canvas لبناء بيئة خادم الوكيل (agent-server) الخاصة به. قم بتثبيته باستخدام السكربت الرسمي:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

يتم تثبيت `uv` في `~/.local/bin`؛ تأكد من أن هذا الدليل موجود ضمن `PATH` الخاص بك.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->