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

يقضي المطورون الكثير من الوقت في حلقات متكررة صغيرة: مراجعة طلبات السحب (pull requests) الموسومة، والرد على تعليقات GitHub، وفرز المشكلات الجديدة، وتحويل خيوط Slack إلى ملاحظات اجتماع يومي أو متابعات للحوادث، وتتبع إشارات الإصدار أو البحث. كل حلقة مألوفة، لكنها لا تزال تتطلب حكماً: جمع السياق الصحيح، وتحديد ما يهم، ونشر تحديث واضح حيث يعمل الفريق بالفعل.

تحوّل [أتمتة OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) تلك الحلقات إلى محادثات وكيل مجدولة أو مُشغَّلة بالأحداث: تشغيلات يمكن فيها لوكيل برمجيات الذكاء الاصطناعي قراءة السياق، واستدعاء الأدوات، وإنتاج تحديث. تتبع قوالب الأتمتة المشتركة في كتالوج ملحقات OpenHands هذا النمط لمراجعة طلبات سحب GitHub، ومراقبة المستودعات، وفرز مشكلات Linear، ومراجعات ما بعد الحوادث، وملخصات الاجتماع اليومي عبر Slack، وموجزات البحث: تستيقظ الأتمتة، وتستخدم عمليات التكامل المُهيَّأة مثل GitHub أو Slack لجلب السياق، وتفكر في هذا السياق باستخدام نموذج لغوي كبير (LLM)، وتكتب النتيجة مرة أخرى.

يُعد [Agent Canvas](https://github.com/OpenHands/agent-canvas) مستوى التحكم المحلي لبناء واختبار تلك الأتمتة. في هذا الدليل الإرشادي، يقوم بتشغيل OpenHands Agent Server، وهي العملية الخلفية التي تنفذ محادثات الوكيل، وتربط الوكيل بالخدمات الخارجية مثل GitHub وSlack.

للحفاظ على سير العمل على نظام AMD الخاص بك، يتحدث الوكيل إلى نموذج محلي يقدمه Lemonade Server. يعرض Lemonade هذا النموذج من خلال واجهة برمجة تطبيقات متوافقة مع OpenAI، بحيث يمكن لـ Agent Canvas تهيئته كنقطة نهاية بعيدة من نمط OpenAI بينما يبقى النموذج والمطالبة (prompt) وسياق سير العمل محلياً.

في هذا الدليل الإرشادي، ستبني أتمتة ملموسة واحدة: موجز تطوير مجدول من GitHub إلى Slack. يستخدم GitHub لفحص نشاط المستودع الأخير، وSlack لنشر الموجز، واستدعاءات واجهة برمجة تطبيقات Agent Canvas لتهيئة الأتمتة واختبارها، وLemonade لتشغيل النموذج اللغوي الكبير محلياً.

![مخطط معماري يوضح GitHub MCP، وأتمتة OpenHands، وLemonade Server، وSlack MCP](assets/00-architecture-overview.png)

## ماذا ستتعلم

- كيفية تشغيل Lemonade Server والتحقق من أن النموذج المحلي يجيب على طلبات المحادثة
- كيفية تشغيل Agent Canwas وتوجيه Agent Server الخاص به نحو نموذج لغوي كبير محلي
- كيفية تثبيت خوادم بروتوكول سياق النموذج (MCP) لكل من GitHub وSlack من خلال واجهة برمجة تطبيقات Agent Server
- كيفية إنشاء وتشغيل أتمتة OpenHands مجدولة تنشر موجز تطوير على Slack
- كيفية استكشاف أكثر أعطال النموذج المحلي والأتمتة شيوعاً وإصلاحها

## المفاهيم الأساسية

| المفهوم | ما هو | أين يندرج في هذا الدليل الإرشادي |
| --- | --- | --- |
| Lemonade Server | منصة تقديم نموذج لغوي كبير محلية مصممة لأجهزة AMD تعرض واجهة برمجة تطبيقات متوافقة مع OpenAI. بياناتك لا تغادر جهازك أبداً. | يشغل النموذج الذي يشغّل الوكيل. |
| OpenHands Agent Server | العملية الخلفية التي تنفذ محادثات وكيل OpenHands. | يستضيف الوكيل، وملف تعريف النموذج اللغوي الكبير الخاص به، وخوادم MCP الخاصة به. |
| Agent Canvas | مستوى التحكم المحلي لـ OpenHands الذي يشغّل Agent Server وواجهة مستخدم لفحص تشغيلات الوكيل. | يشغّل الخلفيات ويوفر واجهة برمجة التطبيقات التي تستدعيها. |
| خادم MCP | خادم بروتوكول سياق النموذج الذي يمنح الوكيل أدوات لخدمة خارجية مثل GitHub أو Slack. | يتيح للوكيل قراءة GitHub والكتابة إلى Slack. |
| أتمتة OpenHands | محادثة وكيل مجدولة أو مُشغَّلة بالأحداث تجلب السياق، وتفكر فيه، وتكتب نتيجة في مكان ما. | موجز GitHub إلى Slack الذي تبنيه هنا. |

<!-- @device:stx,krk -->
> [!NOTE]
> تستفيد سير عمل الوكيل البرمجي من نموذج أكبر ونافذة سياق أكبر. استخدم ما لا يقل عن 32 جيجابايت من ذاكرة النظام، ويُفضل 64 جيجابايت أو أكثر لنماذج GGUF الأكبر حجماً.
<!-- @device:end -->

## المتطلبات الأساسية

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

أنت بحاجة إلى:

- تثبيت Lemonade Server باتباع [دليل تثبيت Lemonade](https://lemonade-server.ai/docs/guide/install/) القياسي.
- Node.js الإصدار 22.12 أو أحدث و`npm`، المستخدمان لتثبيت واجهة سطر أوامر Agent Canvas المنشورة وتشغيل خوادم MCP باستخدام `npx`.
- حزمة `@openhands/agent-canvas` منشورة حديثاً مع إعدادات وكيل قائمة على المخطط (schema-driven)، و`LLMSummarizingCondenserSettings.max_tokens`، ودعم `custom_tokenizer` للنموذج اللغوي الكبير.
- حزمة Python `transformers` متاحة في بيئة Agent Server. وهي مطلوبة لعد الرموز المميزة (tokens) لقالب المحادثة عند تعيين `custom_tokenizer`.
- رمز GitHub برمز وصول للقراءة إلى المستودع الذي تريد تلخيصه.
- رمز بوت Slack (`xoxb-...`) بصلاحيات `chat:write` وصلاحية قراءة القناة.
- معرّف فريق Slack (`T...`).
- معرّف قناة Slack (`C...`) حيث يجب نشر الموجز.

قم بدعوة تطبيق Slack إلى القناة المستهدفة قبل اختبار الأتمتة.

## المتغيرات المستخدمة في هذا الدليل الإرشادي

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

يتم إدخال القيم التالية في واجهة مستخدم Agent Canvas في خطوات لاحقة. قم بتعيينها هنا حتى تتمكن من نسخها لاحقاً:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

استخدم قيمة صريحة بالصيغة `owner/repo` لـ `GITHUB_REPO_FILTER`. يمكن للأحرف البديلة الواسعة على مستوى المؤسسة إرجاع سياق MCP أكبر من اللازم للنماذج المحلية.

## 1. تشغيل Lemonade Server

قم بتشغيل النموذج من واجهة سطر أوامر Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

يعرض Lemonade واجهة برمجة تطبيقات متوافقة مع OpenAI على العنوان التالي:

```text
http://127.0.0.1:13305/api/v1
```

اختياري: إذا لم يكن Agent Canvas أو مُشغِّل الأتمتة على نفس الجهاز، فانشر نقطة نهاية Lemonade عبر نفق آمن واستخدم عنوان URL بصيغة HTTPS كعنوان URL أساسي للنموذج اللغوي الكبير:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. التحقق من النموذج المحلي

تأكد من أن Lemonade يمكنه تقديم النموذج المحدد:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

ثم أرسل طلب محادثة صغيراً:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

إذا أعاد ذلك مصفوفة `choices`، فإن Lemonade جاهز لـ Agent Canvas.
## 3. تشغيل Agent Canvas

قم بتثبيت حزمة Agent Canvas المنشورة وشغّل المجموعة الكاملة:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

إذا فشل تثبيت npm العام بسبب خطأ في الأذونات، راجع إدخال استكشاف أخطاء
أذونات npm أدناه.

بشكل افتراضي، يبدأ Agent Canvas على `http://localhost:8000`. افتح هذا الرابط في
متصفحك. يجب أن تظهر الواجهة الخلفية المحلية الافتراضية بحالة سليمة على شاشة
البداية.

يبدأ الأمر `agent-canvas` خادم الوكيل، والواجهة الخلفية للأتمتة، والواجهة
الأمامية للويب معًا. لا تحتاج سوى إلى هذا الأمر الواحد لتشغيل OpenHands
محليًا. يقوم باقي هذا الدليل بتهيئة كل شيء من خلال واجهة مستخدم Agent
Canvas في متصفحك.

## 4. تهيئة نموذج LLM المحلي في واجهة المستخدم

عند التشغيل لأول مرة، يفتح Agent Canvas تدفق إعداد أولي. ضمن هذا التدفق:

1. أبقِ **OpenHands** محددًا كوكيل واضغط **Next**.
2. في **Set up your LLM**، اختر **Advanced**.
3. أبقِ **Authentication** مضبوطًا على **API key**.
4. اضبط **Custom Model** على قيمة `OPENHANDS_LLM_MODEL`،
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. اضبط **Base URL** على `http://127.0.0.1:13305/api/v1`.
6. في **API Key**، أدخل أي قيمة نائبة غير فارغة مثل `lemonade-local`.
   لا يتطلب Lemonade مفتاحًا حقيقيًا، لكن عميل OpenHands يحتاج إلى قيمة
   لإرسالها.

يجب أن تبدو حقول الاتصال كما يلي. حقل API key مخفي (masked) بواسطة واجهة
المستخدم.

![إعدادات LLM Advanced عند أول استخدام لـ Agent Canvas مع نموذج Lemonade والرابط الأساسي المحلي](assets/01-llm-advanced-settings.png)

بعد ذلك، اختر **All** واضبط الحقول الإضافية للنموذج المحلي:

1. مرر إلى **Custom Tokenizer** واضبطه على `Qwen/Qwen3.6-35B-A3B`.
2. مرر إلى **LiteLLM Extra Body** واضبطه على
   `{"enable_thinking": true}`.
3. اضغط **Next**.

![تبويب All لإعدادات LLM عند أول استخدام لـ Agent Canvas مع محلل Qwen المخصص للرموز](assets/02-llm-all-tokenizer-settings.png)

![تبويب All لإعدادات LLM عند أول استخدام لـ Agent Canvas مع تهيئة LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

يجب أن تُظهر إعدادات LLM ما يلي:

| الحقل | القيمة |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

بادئة `openai/` تخبر LiteLLM باستخدام تنسيق طلب متوافق مع OpenAI
عند التواصل مع نقطة نهاية Lemonade. محلل الرموز المخصص هو محلل الرموز الأصلي
من Hugging Face لنموذج GGUF؛ فهو يتيح لـ OpenHands عدّ نفس رموز قالب
المحادثة (chat-template) التي يراها خادم النموذج المحلي. نموذج LLM الحالي
عند أول استخدام لا يعرض إعدادات condenser. إذا كانت نسخة Agent Canwas لديك
تعرض إعدادات condenser لاحقًا ضمن **Settings > LLM**، استخدم `llm_summarizing`
واضبط الحد الأقصى للرموز أقل من نافذة سياق Lemonade، مثل `56000`.

## 5. تثبيت خوادم GitHub وSlack MCP

في واجهة مستخدم Agent Canvas، افتح **Customize** (أو **Settings > MCP**) لإضافة
خوادم MCP التي تمنح الوكيل أدوات للعمل مع GitHub وSlack. تُرسل قيم الرموز
(tokens) فقط إلى خادم الوكيل المحلي الخاص بك وتُحفظ كإعدادات مشفّرة.

### خادم GitHub MCP

أضف خادم MCP جديدًا بهذه الإعدادات:

| الحقل | القيمة |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = رمز GitHub الخاص بك |

استخدم رمز GitHub بصلاحية قراءة على المستودع الذي تريد تلخيصه.

### خادم Slack MCP

أضف خادم MCP ثانيًا بهذه الإعدادات:

| الحقل | القيمة |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = معرّف قناة الملخص لديك |

اضبط `SLACK_CHANNEL_IDS` على معرّف قناة الملخص (نفس قيمة
`SLACK_DIGEST_CHANNEL`) حتى لا يحتاج الوكيل إلى تصفح كل قناة على Slack.

بعد إضافة كلا الخادمين، استخدم زر **Test** على كل منهما للتأكد من أنه
يتصل ويعرض الأدوات المتاحة. يجب أن يعرض خادم GitHub أدوات GitHub، ويعرض
خادم Slack أدوات Slack.

![صفحة MCP في Agent Canvas مع تثبيت خادمي GitHub وSlack](assets/04-mcp-servers-installed.png)

## 6. إنشاء أتمتة الملخص

في واجهة مستخدم Agent Canvas، افتح صفحة **Automations** وأنشئ أتمتة جديدة:

1. اختر **Create automation** وحدد النوع **Prompt preset**.
2. اضبط **Name** على `GitHub Development Digest to Slack`.
3. اضبط **Prompt** على النص التالي، مع استبدال العناصر النائبة للمستودع
   والقناة بقيمك الخاصة:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. اضبط **Trigger** على **Cron** بالجدول الزمني `0 9 * * 1-5` (الساعة 9
   صباحًا في أيام الأسبوع) واضبط **Timezone** على منطقتك الزمنية، على سبيل
   المثال `America/New_York`.
5. اضبط **Timeout** على `900` ثانية.
6. احفظ الأتمتة.

تعرض صفحة تفاصيل الأتمتة الأتمتة الجديدة مع محفّز cron الخاص بها ونقطة
دخول prompt-preset التي تم إنشاؤها.

![صفحة تفاصيل الأتمتة في Agent Canvas بعد الإنشاء](assets/05-automation-created.png)
## 7. اختبار الأتمتة

من صفحة تفاصيل الأتمتة في واجهة Agent Canvas:

1. انقر على **Run now** (أو **Dispatch**) لتشغيل الأتمتة مرة واحدة فورًا.
2. راقب قائمة عمليات التشغيل في نفس الصفحة. يجب أن تنتقل حالة أحدث عملية تشغيل إلى
   `COMPLETED`.
3. افتح قناة Slack المستهدفة. يجب أن تحتوي على الملخص الذي تم إنشاؤه.

لست بحاجة إلى الانتظار حتى يتم تشغيل جدول cron—فزر **Run now** يؤدي إلى تشغيل
عملية عند الطلب حتى تتمكن من التأكد من أن الطلب النصي واتصالات MCP والنشر على
Slack تعمل جميعها بشكل صحيح قبل الاعتماد على الجدول الزمني.

![اكتملت عملية تشغيل أتمتة Agent Canvas بنجاح](assets/06-automation-run-completed.png)

![قناة Slack تعرض ملخص OpenHands الذي تم إنشاؤه](assets/07-slackbot-message.png)

## استكشاف الأخطاء وإصلاحها

- **Lemonade متوقف:** أعد تشغيله باستخدام أمر
  `lemonade run "${LEMONADE_MODEL}"` في الخطوة 1، ثم أعد تشغيل فحص السلامة.
- **يفشل `npm install -g` بخطأ صلاحيات:** على Linux أو WSL،
  قم بتهيئة دليل npm عام مملوك للمستخدم، وأضفه إلى ملف بدء تشغيل الشل الخاص بك، ثم قم بتثبيت Agent Canvas مرة أخرى:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  إذا كنت تستخدم `zsh`، أضف نفس السطر `export PATH=...` إلى `~/.zshrc` بدلاً
  من `~/.bashrc`.
- **يرفض Agent Canvas إعدادات LLM بعد ضبط `custom_tokenizer`:**
  قم بتثبيت `transformers` في بيئة Python الخاصة بـ Agent Server، وأعد تشغيل Agent
  Canvas إذا لزم الأمر، وأعد محاولة حفظ إعدادات LLM. يتطلب OpenHands وجود
  Transformers لتحميل قالب محادثة المُرمِّز عند ضبط `custom_tokenizer`.
- **لا يستطيع Agent Canvas الوصول إلى Lemonade:** تحقق من
  `curl -fsS "${LEMONADE_BASE_URL}/health"` وتأكد من أن عنوان URL الأساسي المُدخل في
  نموذج LLM عند أول استخدام أو في **Settings > LLM** يطابق نقطة النهاية المحلية
  قيد التشغيل أو نفق HTTPS.
- **لم يتم حفظ إعدادات LLM:** تأكد من أنك نقرت على **Next** بعد
  إدخال القيم. أعد فتح **Settings > LLM** للتأكد من أن القيم قد تم حفظها.
- **لا يستطيع GitHub MCP رؤية المستودعات الخاصة:** تأكد من أن رمز GitHub لديه
  صلاحية قراءة للمستودع المستهدف وأن زر **Test** الخاص بـ MCP في
  **Customize** يعلن عن أدوات GitHub.
- **يستطيع Slack قراءة القنوات لكن لا يستطيع النشر:** ادعُ تطبيق Slack إلى
  القناة المستهدفة وتأكد من أن البوت يملك صلاحية `chat:write`.
- **تسرد الأتمتة عددًا كبيرًا جدًا من قنوات Slack:** استخدم معرّف قناة Slack
  واضبط `SLACK_CHANNEL_IDS` على خادم Slack MCP في **Customize**.
- **تفشل عملية تشغيل الأتمتة أو تتجاوز السياق:** تأكد من أن Lemonade تم تشغيله
  بـ `ctx_size=65536`، وتأكد من أن LLM الخاص بـ OpenHands يحتوي على `custom_tokenizer` مضبوطًا،
  واستخدم مستودعًا محددًا مع تحديد مجموعات نتائج GitHub بحد أقصى 3 إلى 5
  عناصر. إذا كان إصدار Agent Canvas الخاص بك يعرض إعدادات condenser، فاضبط الحد الأقصى
  للرموز الخاصة بـ condenser أقل من نافذة سياق Lemonade.

## الخطوات التالية

- إضافة ملخص أسبوعي خاص بالإصدارات فقط.
- إضافة أتمتة تُشغَّل بواسطة أحداث GitHub لتنبيهات أسرع لطلبات السحب أو عمليات الدفع.
- توجيه نفس الملخص إلى Notion أو Linear أو أداة أخرى مدعومة بـ MCP.

## الموارد

- [كتب اللعب الخاصة بالذكاء الاصطناعي من AMD](https://developer.amd.com/playbooks/)
- [وثائق Lemonade Server](https://lemonade-server.ai/docs)
- [مستودع امتدادات OpenHands](https://github.com/OpenHands/extensions)
- [خوادم بروتوكول سياق النموذج](https://github.com/modelcontextprotocol/servers)
- [حزمة Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)