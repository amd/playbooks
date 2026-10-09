<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو واجهة المستخدم الخاصة بالمتصفح/سطر الأوامر الخاصة بـ OpenHands، ويتم توزيعه كحزمة npm باسم `@openhands/agent-canvas`. يتطلب **Node.js 24 أو إصدارًا أحدث**. قم بتثبيته بشكل عام:

```bash
npm install -g @openhands/agent-canvas
```

يتم وضع الملف الثنائي `agent-canvas` في المجلد العام الخاص بـ npm (مثل `~/.npm-global/bin`)؛ تأكد من أن هذا المجلد موجود ضمن `PATH` الخاص بك.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->