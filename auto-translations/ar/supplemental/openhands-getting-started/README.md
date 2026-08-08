<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## نظرة عامة

[OpenHands](https://github.com/All-Hands-AI/OpenHands) هو وكيل برمجي مدعوم
بالذكاء الاصطناعي يمكنه كتابة الشيفرة البرمجية وتشغيل الأوامر وتصفح الويب
وتحرير الملفات في بيئة عمل حقيقية. بدلاً من نسخ الاقتراحات من نافذة محادثة،
توجّه الوكيل إلى مجلد مشروع وتتركه ينجز العمل: تنفيذ ميزة، أو إصلاح خطأ، أو
كتابة اختبارات، أو شرح قاعدة شيفرة برمجية.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) هو واجهة المستخدم
عبر المتصفح الموصى بها لتشغيل OpenHands. يقوم أمر واحد وهو `agent-canvas` ببدء
تشغيل خادم الوكيل، والخلفية البرمجية للأتمتة، والواجهة الأمامية للويب معًا،
مما يتيح لك إجراء محادثة مع الوكيل من متصفحك.

للحفاظ على كل شيء على نظام AMD الخاص بك، يتواصل الوكيل مع نموذج محلي يقدمه
Lemonade Server. يعرض Lemonade هذا النموذج من خلال واجهة برمجة تطبيقات متوافقة
مع OpenAI، بحيث يمكن لـ Agent Canvas تكوينه مثل أي نقطة نهاية أخرى بأسلوب
OpenAI، بينما يبقى النموذج وشيفرتك البرمجية وسياق المحادثة كلها على جهازك.

في هذا الدليل التعليمي، ستقوم ببدء تشغيل نموذج محلي، وتشغيل Agent Canvas،
وتوجيهه إلى ذلك النموذج، وتنفيذ أول مهمة برمجية لك على مجلد مشروع حقيقي.

## ما ستتعلمه

- كيفية بدء تشغيل Lemonade Server والتأكد من أن نموذجًا محليًا يستجيب لطلبات
  المحادثة
- كيفية تثبيت وتشغيل Agent Canvas من حزمة npm
- كيفية تكوين Agent Canvas لاستخدام نموذج Lemonade محلي كنموذج اللغة الكبير
  (LLM)
- كيفية بدء محادثة OpenHands ومراقبة الوكيل وهو يحرر الملفات وينفذ الأوامر في
  بيئة عمل
- كيفية مراجعة ما قام الوكيل بتغييره وتوجيهه برسائل متابعة

## المفاهيم الأساسية

| المفهوم | ما هو | مكانه في هذا الدليل التعليمي |
| --- | --- | --- |
| Lemonade Server | منصة محلية لتقديم نماذج اللغة الكبيرة مصممة لأجهزة AMD وتعرض واجهة برمجة تطبيقات متوافقة مع OpenAI. لا تغادر بياناتك جهازك أبدًا. | يشغّل النموذج الذي يشغّل الوكيل. |
| OpenHands | وكيل برمجي مدعوم بالذكاء الاصطناعي يقرأ الملفات ويحررها، وينفذ أوامر الصدفة، ويتصفح الويب داخل بيئة عمل. | الوكيل الذي توجّهه من المحادثة. |
| Agent Canvas | واجهة المستخدم عبر المتصفح والخلفية البرمجية التي تشغّل محادثات OpenHands وتعرض استدعاءات الأدوات وتغييرات الملفات. | يشغّل المكدس ويستضيف محادثتك. |
| بيئة العمل | مجلد المشروع الذي يُسمح للوكيل بقراءته وتعديله. | هدف تحريرات الوكيل وأوامره. |

<!-- @device:stx,krk -->
> [!NOTE]
> تستفيد سير عمل الوكلاء البرمجيين من نموذج أكبر ونافذة سياق أكبر. استخدم
> 32 جيجابايت على الأقل من ذاكرة النظام، ويُفضّل 64 جيجابايت أو أكثر لنماذج
> GGUF الأكبر حجمًا.
<!-- @device:end -->

## المتطلبات الأساسية

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

تحتاج إلى:

- تثبيت Lemonade Server والقدرة على تقديم النموذج أدناه.
- Node.js الإصدار 22.12 أو أحدث وأداة `npm` (تُستخدم بواسطة واجهة سطر الأوامر
  الخاصة بـ `agent-canvas`).
- `uv`، مدير حزم Python الذي يستخدمه Agent Canvas لإدارة بيئة خادم الوكيل. إذا
  لم يكن نظامك يحتوي عليه بالفعل، فقم بتثبيته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/)
  قبل تشغيل Agent Canvas.
- مجلد مشروع للعمل فيه. يمكن أن يكون هذا أي مستودع git محلي أو دليل شيفرة
  برمجية تريد أن يعمل الوكيل عليه.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. بدء تشغيل Lemonade Server

ابدأ تشغيل النموذج من واجهة سطر أوامر Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

يعرض Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI على:

```text
http://127.0.0.1:13305/api/v1
```



## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade يمكنه تقديم النموذج المحدد:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

ثم أرسل طلب محادثة صغيرًا:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

إذا أعاد ذلك مصفوفة `choices`، فإن Lemonade جاهز لـ Agent Canvas.

## 3. تثبيت Agent Canvas وتشغيله

قم بتثبيت حزمة Agent Canvas المنشورة بشكل عام (global):

```bash
npm install -g @openhands/agent-canvas
```

ثم ابدأ تشغيل المكدس الكامل من طرفية:

```bash
agent-canvas
```

افتراضيًا، يبدأ Agent Canvas على `http://localhost:8000`. افتح ذلك العنوان
في متصفحك. إذا كان المنفذ 8000 مستخدمًا بالفعل، مرّر `--port` (أو `-p`) عند
تشغيل Agent Canvas:

```bash
agent-canvas --port 3000
```

يعمل نفس الأمر في PowerShell على Windows. ثم افتح `http://localhost:3000`
بدلاً من ذلك. يجب أن تظهر الخلفية البرمجية المحلية الافتراضية بحالة سليمة
(healthy) في الشاشة الرئيسية.

يبدأ أمر `agent-canvas` تشغيل خادم الوكيل، والخلفية البرمجية للأتمتة، والواجهة
الأمامية للويب معًا. تحتاج فقط إلى هذا الأمر الواحد لتشغيل OpenHands محليًا.

## 4. تكوين نموذج اللغة الكبير المحلي

عند التشغيل الأول، يفتح Agent Canvas سير عمل تعريفي (onboarding). في ذلك
السير:

1. أبقِ **OpenHands** محددًا كوكيل وانقر على **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** على `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
6. في **API Key**، أدخل أي قيمة نائبة غير فارغة مثل `lemonade-local`. لا
   يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة لإرسالها.
7. انقر على **Next**.

يجب أن تبدو إعدادات Advanced المكتملة كما يلي. حقل مفتاح واجهة برمجة التطبيقات
مقنّع بواسطة الواجهة.

![إعدادات Advanced لنموذج اللغة الكبير عند أول استخدام لـ Agent Canvas مع نموذج Lemonade وعنوان URL الأساسي المحلي](assets/01-llm-advanced-settings.png)

يحفظ Agent Canvas هذه القيم كملف تعريف لنموذج اللغة الكبير (LLM profile). إذا
طلب إصدارك تسمية ذلك الملف الشخصي، استخدم اسمًا بدون مسافات مثل
`lemonade-local`. إذا غيّرت النماذج لاحقًا، افتح **Settings > LLM** وحدّث نفس
حقول Advanced. يمكنك التبديل بين الملفات الشخصية المحفوظة من إدخال المحادثة
باستخدام الأمر `/model`.

## 5. فتح بيئة عمل

يمكن للوكيل فقط قراءة الملفات وتعديلها داخل بيئة العمل التي تختارها. قبل بدء
مهمة، وجّه Agent Canvas إلى مجلد مشروعك:

1. من الشاشة الرئيسية، اختر **Open Workspace**.
2. حدد المجلد الذي يحتوي على مشروعك (على سبيل المثال، مستودع git تريد أن
   يعمل الوكيل عليه).
3. ابدأ محادثة جديدة في بيئة العمل تلك.

كل ما يفعله الوكيل - قراءة الملفات، وتنفيذ الأوامر، وتحرير الشيفرة البرمجية -
مقتصر على تلك بيئة العمل.

![الشاشة الرئيسية لـ Agent Canvas بعد التعريف الأولي](assets/02-agent-canvas-home.png)
## 6. نفّذ أول مهمة برمجية

بعد فتح مساحة العمل واختيار نموذج اللغة الكبير المحلي، اكتب مهمة محددة في المحادثة. من المهام الجيدة للبداية أن تكون صغيرة وقابلة للتحقق، مثل:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

راقب سلسلة زمنية للمحادثة. سيقوم OpenHands بما يلي:

- قراءة مساحة العمل لفهم البنية.
- إنشاء `hello.py` مع الدالة المطلوبة وكتلة الاختبار.
- تشغيل `python3 hello.py` اختياريًا للتحقق من الناتج.
- الإبلاغ عمّا قام به وأي ناتج للأوامر في المحادثة.

يجب أن ترى الملف الجديد يظهر في مساحة العمل، وأن تصف رسالة العميل الأخيرة التغيير الذي أجراه. هذه هي اللحظة الفارقة: كتب العميل وشغّل كودًا حقيقيًا في مجلد مشروعك.

## 7. راجع عمل العميل ووجّهه

بعد أن ينتهي العميل من خطوة ما، راجع عمله قبل قبول الخطوة التالية:

- **تغييرات الملفات**: استخدم متصفح ملفات مساحة العمل أو عرض الفروقات (diff) الخاص بالعميل لترى بالضبط ما تمت إضافته أو تغييره أو حذفه.
- **ناتج الأوامر**: وسّع أي أمر نفّذه العميل لترى المخرجات القياسية (stdout) والأخطاء القياسية (stderr) ورمز الخروج.
- **المتابعات**: إذا لم تكن النتيجة كما تريد، أجب في نفس المحادثة بتصحيح. يحتفظ العميل بالسياق السابق ويكرر العمل على نفس الملفات.

على سبيل المثال، إذا لم يطبع الاختبار التحية المتوقعة، أجب بـ:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

سيعيد العميل قراءة الملف، وتشغيل الأمر، وتشخيص المشكلة، ثم يعدّل الملف مرة أخرى—كل ذلك في نفس المحادثة.

## استكشاف الأخطاء وإصلاحها

- **`agent-canvas` غير موجود في PATH:** أعد التثبيت باستخدام
  `npm install -g @openhands/agent-canvas` وتأكد من أن دليل الملفات الثنائية العام لـ npm موجود في PATH لديك. على نظام Windows، شغّل `npm config get prefix`؛ يجب أن يكون الدليل المُعاد، غالبًا `%APPDATA%\npm` أو `%USERPROFILE%\.npm-global`،
  موجودًا في PATH الخاص بمستخدمك قبل أن يمكن تشغيل `agent-canvas` من طرفية جديدة.
- **يفشل `npm install -g` بخطأ في الأذونات:** قم بتهيئة دليل npm عام مملوك للمستخدم، ثم أعد فتح الطرفية وثبّت Agent Canvas مرة أخرى.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  لجعل تغيير PATH في Windows دائمًا، أضف `%USERPROFILE%\.npm-global` إلى
  PATH الخاص بمستخدمك من **الإعدادات > النظام > حول > إعدادات النظام المتقدمة >
  متغيرات البيئة**، ثم افتح طرفية جديدة.
  <!-- @os:end -->
- **تُحمَّل الواجهة لكن الخلفية تظهر غير سليمة:** انتظر بضع ثوانٍ حتى ينتهي خادم العميل من بدء التشغيل، ثم قم بالتحديث. إذا بقيت غير سليمة، أعد تشغيل
  `agent-canvas` وتحقق من ناتج الطرفية بحثًا عن الأخطاء.
- **تفشل طلبات محادثة Lemonade بخطأ في الاتصال:** تأكد من نجاح
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` وأن
  Lemonade لا يزال يقدّم النموذج باستخدام `lemonade status`.
- **يظهر خطأ لدى العميل يتعلق بطول السياق أو حد الرموز:** أعد تشغيل
  Lemonade بقيمة أكبر لـ `ctx_size` (على سبيل المثال `ctx_size=65536`)، وابدأ
  محادثة جديدة حتى لا يحمل العميل سجلاً ضخمًا للغاية.
- **ينتج العميل تعديلات منخفضة الجودة أو غير مكتملة:** انتقل إلى نموذج أكبر في Lemonade، أو أعطِ العميل مهمة أصغر وأكثر تحديدًا ودعه ينهيها قبل طلب التغيير التالي.
- **`uv` غير موجود:** ثبّته من
  [دليل تثبيت uv](https://docs.astral.sh/uv/getting-started/installation/).
  يستخدم Agent Canvas أداة `uv` لإدارة بيئة Python الخاصة بخادم العميل.

## الخطوات التالية

- جرّب مهمة أكبر في نفس مساحة العمل، مثل إضافة ملف اختبار وحدة أو
  إصلاح خطأ معروف، وراجع الفروقات (diff) الخاصة بالعميل قبل الإبقاء على التغيير.
- اربط خادم MCP مثل GitHub أو Slack ضمن **Customize** حتى
  يتمكن العميل من قراءة المشكلات (issues) أو نشر التحديثات أثناء عمله.
- احفظ عدة ملفات تعريف لنماذج اللغة الكبيرة (نموذج صغير سريع ونموذج كبير أقوى) وقم
  بالتبديل بينها باستخدام `/model` أثناء المحادثة.
- انتقل إلى [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) لتحويل
  دورات التطوير المتكررة إلى تشغيلات مجدولة أو مُفعَّلة بالأحداث للعميل.

## الموارد

- [توثيق OpenHands](https://docs.openhands.dev/)
- [نظرة عامة على Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [إعداد Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [ملفات تعريف نماذج اللغة الكبيرة وتهيئة النموذج](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [توثيق Lemonade Server](https://lemonade-server.ai/docs)