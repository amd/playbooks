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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# تجميع أربعة أجهزة Ryzen™ AI Halo في عنقود باستخدام RPC

## نظرة عامة

جهاز Ryzen™ AI Halo الخاص بك قادر بالفعل على تشغيل نماذج اللغة الكبيرة محليًا. ويأخذ التجميع العنقودي (Clustering) هذا الأمر إلى أبعد من ذلك عبر دمج ذاكرة GPU لعدة أنظمة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر بكثير مع قدرات استدلال أقوى، وتوليد أكواد أفضل، وفهم أعمق متعدد اللغات، وكل ذلك بالكامل على عتادك الخاص.

يعلّمك هذا الدليل كيفية تجميع أربعة أنظمة Ryzen AI Halo في عنقود واحد باستخدام محرك RPC الخاص بـ llama.cpp، وتشغيل نموذج Kimi K2.6، وهو نموذج كبير من نوع mixture-of-experts، عبر الأجهزة الأربعة كلها مع تسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm وRPC
- إعداد عمال RPC (RPC workers) وتشغيل الاستدلال الموزّع عبر أربع عقد
- تشغيل نموذج بحجم 1 تريليون معامل عبر أربعة أنظمة Ryzen AI Halo مترابطة عبر الشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على جميع الأجهزة الأربعة (الجهاز 1 إلى الجهاز 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **تشغيل نماذج قريبة من 128 جيجابايت أو تتجاوزها:** على أنظمة AMD Ryzen™ AI Max 400 Series (Gorgon Halo) التي تعمل بنظام Windows، تتطلب النماذج التي تقترب من 128 جيجابايت من الذاكرة أو تتجاوزها إعدادات إضافية للعمل بدون أخطاء. اتبع [إرشادات نظام تشغيل Windows لسلسلة AMD Ryzen AI Max PRO 400](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) قبل تحميل النموذج.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (ذاكرة VRAM الخاصة بـ iGPU).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 جيجابايت**. يُرجى إعادة تشغيل النظام ليتم تطبيق التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، يستخدم ROCm مجمع ذاكرة نظام مشترك، ويُضبط هذا المجمع افتراضيًا على نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحات Translation Table Manager (TTM) الخاصة بالنواة، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 جيجابايت).

* ثبّت أداة pipx وأضف المسار الخاص بالحزم (wheels) المثبتة عبر pipx إلى مسار بحث النظام.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ثبّت حزمة amd-debug-tools من PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* شغّل أداة amd-ttm للاستعلام عن الإعدادات الحالية للذاكرة المشتركة.
  ```bash
  amd-ttm
  ```

* أعد ضبط إعدادات الذاكرة المشتركة إلى **120 جيجابايت**:
  ```bash
  amd-ttm --set 120
  ```

* أعد تشغيل النظام ليتم تطبيق التغييرات.


<!-- @os:end -->
<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### العتاد

يتطلب هذا الدليل أربع وحدات Ryzen AI Halo ومحوّل Ethernet واحد، متصلة في طوبولوجيا نجمية مع توصيل كل وحدة مباشرة بالمحوّل.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | عقد الحوسبة التي تشكّل العنقود |
| محوّل Ethernet بسرعة 10 جيجابت | 1 | محوّل مركزي للسماح بالاتصال بين عدة عقد من Ryzen AI Halo (4 منافذ على الأقل) |
| كابل Ethernet | 4 | يصل كل وحدة Halo بالمحوّل (يُنصح باستخدام Cat 7 أو أعلى) |

> **ملاحظة**: يلزم توفر أربعة منافذ على محوّل Ethernet لتوصيل وحدات Ryzen AI Halo الأربع. ويلزم منفذ خامس إذا كنت ستصل إلى النموذج من جهاز عميل منفصل بدلاً من الوصول من إحدى وحدات Halo نفسها.

### البرمجيات
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
يُرجى تثبيت:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) مع حزمة العمل **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## إعداد العتاد الفعلي

> **ملاحظة**: أكمل هذه الخطوة على جميع الأجهزة الأربعة (الجهاز 1 إلى الجهاز 4).

صِل كل وحدة Ryzen AI Halo بمحوّل Ethernet باستخدام كابل Cat 7 (أو أعلى). يؤسس هذا الوصلة بسرعة 10 جيجابت المستخدمة للاتصال عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

على كل جهاز، ابحث عن اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه باسم `IFNAME`). شغّل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

يطبع هذا اسم الواجهة مباشرة، على سبيل المثال:

```bash
enp191s0
```

### 2. التحقق من سرعات روابط الشبكة

تأكد من أن الرابط نشط ويعمل بأقصى سرعة عن طريق التحقق من سرعة واجهتك:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **ملاحظة**: استبدل `<IFNAME>` باسم واجهة الإخراج الناتج من [1. تحديد واجهات الشبكة](#1-determine-network-interfaces)

يجب أن ترى سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحوّل مضبوط على 10 جيجابت. قد تتطلب بعض المحوّلات تعطيل التفاوض التلقائي (auto-negotiation) وضبط سرعة الرابط يدويًا؛ راجع وثائق المحوّل الخاص بك.

<!-- @os:end -->

<!-- @os:windows -->
### التحقق من سرعة رابط الشبكة

على كل جهاز، تحقق من سرعة رابط واجهات الشبكة الخاصة بك:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

يجب أن تكون واجهة Ethernet الخاصة بك `Up` وتعمل بسرعة `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحوّل مضبوط على 10 جيجابت. قد تتطلب بعض المحوّلات تعطيل التفاوض التلقائي (auto-negotiation) وضبط سرعة الرابط يدويًا؛ راجع وثائق المحوّل الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على جميع الأجهزة الأربعة (الجهاز 1 إلى الجهاز 4).

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات (binaries) جاهزة مسبقًا، أسرع إعداد
- [الخيار 2: البناء اليدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في رايات البناء (build flags)
### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK إصدارات ليلية (nightly builds) من llama.cpp مع تسريع AMD ROCm 7، تستهدف وحدات معالجة رسومية مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وبنيات Radeon الحديثة الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لنظامك الأساسي والهدف الخاص بوحدة معالجة الرسومات:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية

قم بفك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مزودة بدعم ROCm من `llama-cli.exe` و`llama-server.exe` و`ggml-rpc-server.exe`، مُجمّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات

```bash
.\llama-cli.exe --list-devices
```

الناتج المتوقع:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لنظامك الأساسي والهدف الخاص بوحدة معالجة الرسومات:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية وتجهيزها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مزودة بدعم ROCm من `llama-cli` و`llama-server` و`rpc-server`، مُجمّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات

```bash
./llama-cli --list-devices
```

الناتج المتوقع:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
بعد تجهيز llama.cpp على كل عقدة، تابع إلى [تنزيل النموذج](#downloading-the-model).

### الخيار 2: البناء اليدوي من المصدر

<!-- @os:windows -->
#### الخطوة 1: بناء llama.cpp

افتح **x64 Native Tools Command Prompt** (المثبت مع Visual Studio Build Tools) واستنسخ المستودع:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

أضف HIP إلى المسار الخاص بك وقم بالبناء مع دعم ROCm وRPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُفعّل حزمة برامج ROCm/HIP |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزّع |
| `-DGPU_TARGETS=gfx1151` | يستهدف وحدة معالجة الرسومات الخاصة بـ Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | يستخدم نظام البناء Ninja |

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

الناتج المتوقع:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### الخطوة 3: إضافة HIP إلى مسار المستخدم الخاص بك

قامت خطوة البناء أعلاه بتعيين `%HIP_PATH%\bin` للجلسة الحالية فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في x64 Native Tools Command Prompt)، أضفها بشكل دائم إلى `PATH` الخاص بالمستخدم:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

بعد تجهيز llama.cpp على كل عقدة، تابع إلى [تنزيل النموذج](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### الخطوة 1: بناء llama.cpp

استنسخ المستودع:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

قم بالبناء مع دعم ROCm وRPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُفعّل حزمة برامج ROCm |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزّع |
| `-DAMDGPU_TARGETS="gfx1151"` | يستهدف وحدة معالجة الرسومات الخاصة بـ Ryzen AI Halo (Radeon 8060s) |

لمزيد من خيارات البناء، راجع [وثائق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات

```bash
cd rocm/bin
./llama-cli --list-devices
```

الناتج المتوقع:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

بعد تجهيز llama.cpp على كل عقدة، تابع إلى [تنزيل النموذج](#downloading-the-model).
<!-- @os:end -->

## تنزيل النموذج

يستخدم هذا الدليل [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) بتكميم `UD-Q2_K_XL` من [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). يتناسب هذا التكميم مع إجمالي ذاكرة وحدة معالجة الرسومات لأربع عقد من Ryzen AI Halo.

قم بتنزيل ملفات GGUF باستخدام أداة سطر الأوامر Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز 1 (المتحكم). لا تحتاج عقد العمل RPC (الأجهزة 2 و3 و4) إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يسمح محرك llama.cpp RPC (استدعاء الإجراء عن بُعد) بإسناد (offload) طبقات النموذج من نسخة واحدة من llama.cpp إلى عمال عن بُعد عبر الشبكة. يعمل جهاز واحد بصفته **المتحكم** (الجهاز 1)، حيث يتولى عملية الترميز (tokenization) والجدولة والتنسيق. ويقوم كل من الأجهزة الثلاثة الأخرى بتشغيل **خادم RPC** خفيف (الأجهزة 2 و3 و4) يكشف ذاكرة وحدة معالجة الرسومات الخاصة به وقدرته الحسابية للمتحكم.

عند وقت التحميل، يقوم llama.cpp بتقسيم النموذج عبر جميع العقد الأربع. وبمجرد التحميل، يتم الاستدلال كما لو كان يعمل على مسرّع واحد. يتولى RPC عمليات نقل الموترات (tensor) والمزامنة خلف الكواليس.

### الخطوة 1: بدء خوادم RPC (الأجهزة 2 و3 و4)

على كل من الأجهزة 2 و3 و4، قم ببدء خادم RPC لكشف موارد وحدة معالجة الرسومات الخاصة به للمتحكم:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| العلامة | الغرض |
|------|---------|
| `-p` | المنفذ الذي يُبث عليه خادم RPC |
| `-c` | يُفعّل ذاكرة تخزين مؤقت محلية للموترات الكبيرة، مما يتجنب عمليات النقل المتكررة عبر الشبكة أثناء تحميل النموذج |
| `--host` | عنوان IP الذي يُربط به خادم RPC (`0.0.0.0` لجميع الواجهات) |

لمزيد من الخيارات، راجع [وثائق RPC الخاصة بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خوادم RPC على الأجهزة 2 و3 و4، قم بتشغيل الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.
#### llama-cli

يوفر `llama-cli` واجهة قائمة على الطرفية (terminal) للتفاعل المباشر مع النموذج. وهو مثالي لإجراء القياسات المرجعية (benchmarking)، وتصحيح الأخطاء، والتجريب على المستوى المنخفض.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الأجهزة 2 و3 و4، نفّذ الأمر `hostname -I | awk '{print $1}'` لمعرفة عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: نفّذ هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الأجهزة 2 و3 و4، نفّذ الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لمعرفة عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، يعرض `llama-cli` تقدّم تحميل النموذج ويدخل إلى موجّه تفاعلي حيث يمكنك الدردشة مع النموذج مباشرة:

![تشغيل llama-cli لنموذج Kimi K2.6 عبر أربع عُقد](assets/llama-cli-example.png)

#### llama-server

يتيح `llama-server` نفس محرك الاستدلال من خلال عملية خادم دائمة تتضمن واجهة مستخدم ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. تُعد هذه الواجهة الخيار المفضّل للنشر طويل المدى، والوصول متعدد المستخدمين، والتكامل مع الأدوات الخارجية.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الأجهزة 2 و3 و4، نفّذ الأمر `hostname -I | awk '{print $1}'` لمعرفة عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: نفّذ هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الأجهزة 2 و3 و4، نفّذ الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لمعرفة عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد بدء التشغيل، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة الويب المدمجة. توفّر هذه الواجهة تجربة دردشة قائمة على المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server أثناء تشغيل نموذج Kimi K2.6 عبر أربع عُقد](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، نفّذ الأمر `hostname -I | awk '{print $1}'` لمعرفة عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، نفّذ الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لمعرفة عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00008`) |
| `-c` | حجم السياق بعدد الرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | يفعّل ميزة rocWMMA Flash Attention لتحسين الأداء على معالجات AMD الرسومية |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسومات (GPU) |
| `-lm none` | يضبط وضع تحميل النموذج على `none`، مما يعطّل التعيين إلى الذاكرة (memory-mapping) لتقليل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام RAM لكنه يتسع ضمن ذاكرة VRAM |
| `-b` | حجم الدفعة المنطقية (logical batch) بعدد الرموز. ضبط القيمة على 4096 يوازن بين الإنتاجية واستخدام الذاكرة عبر العُقد |
| `-ub` | حجم الدفعة الفعلية (الصغرى) لمعالجة الموجّه (prompt). مطابقة هذه القيمة مع `-b` يتجنب أعباء التقسيم غير الضرورية |
| `--host` | عنوان IP لربط `llama-server` به (خاص بـ `llama-server` فقط) |
| `--port` | المنفذ الذي سيتم تقديم واجهة برمجة تطبيقات HTTP من خلاله (خاص بـ `llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل بنقاط نهاية عامل RPC (بصيغة `IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، يُرجى الرجوع إلى [توثيق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[توثيق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: يوفّر `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` باستخدام أي مفتاح API وهمي (مثلاً، `none`) للاتصال بعنقودك (cluster)
- **استكشاف نماذج أخرى**: تصفّح نماذج GGUF المُكمَّمة (quantized) على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تتناسب مع إجمالي ذاكرة GPU في عنقودك
- **التوسّع إلى أكثر من أربع عُقد**: أضف أنظمة Ryzen AI Halo إضافية كعمّال RPC إضافيين للوصول إلى نماذج تتجاوز مقياس التريليون معامل (parameter). مرّر نقاط نهاية إضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثلاً، `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)