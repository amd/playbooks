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

# تجميع أربعة أنظمة Ryzen™ AI Halo في عنقود باستخدام RPC

## نظرة عامة

يتمتع جهازك Ryzen™ AI Halo بالفعل بالقدرة على تشغيل نماذج اللغة الكبيرة محليًا. ويأخذ التجميع (Clustering) هذه القدرة إلى مستوى أبعد من خلال دمج ذاكرة GPU لعدة أنظمة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر بكثير تتمتع بقدرات استدلال أقوى، وتوليد أكواد برمجية أفضل، وفهم أعمق للغات متعددة، وكل ذلك يتم بالكامل على عتادك الخاص.

يشرح لك هذا الدليل كيفية تجميع أربعة أنظمة Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp، وتشغيل نموذج Kimi K2.6، وهو نموذج مزيج خبراء (mixture-of-experts) كبير، عبر الأجهزة الأربعة جميعها باستخدام تسريع AMD ROCm™.

## ما الذي ستتعلمه

- كيفية توسيع تخصيص ذاكرة VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm و RPC
- تكوين عمّال (workers) RPC وإطلاق الاستدلال الموزّع عبر أربع عقد
- تشغيل نموذج بحجم 1 تريليون معامل عبر أربعة أنظمة Ryzen AI Halo متصلة عبر الشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على جميع الأجهزة الأربعة (الجهاز 1 إلى الجهاز 4).

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (ذاكرة iGPU VRAM).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 جيجابايت**. يُرجى إعادة تشغيل النظام لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، تستخدم ROCm مجمّعًا مشتركًا لذاكرة النظام، ويُضبط هذا المجمّع افتراضيًا على نصف ذاكرة النظام.

يمكن زيادة هذا المقدار عن طريق تغيير إعداد صفحة مدير جدول الترجمة (Translation Table Manager - TTM) الخاص بالنواة (kernel)، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى لذاكرة VRAM المخصصة في الـ BIOS (0.5 جيجابايت).

* قم بتثبيت أداة pipx وأضف مسار حزم pipx المثبتة إلى مسار البحث الخاص بالنظام.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* قم بتثبيت حزمة amd-debug-tools من PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* شغّل أداة amd-ttm للاستعلام عن الإعدادات الحالية للذاكرة المشتركة.
  ```bash
  amd-ttm
  ```

* أعد تكوين إعدادات الذاكرة المشتركة لتصبح **120 جيجابايت**:
  ```bash
  amd-ttm --set 120
  ```

* أعد تشغيل النظام لتصبح التغييرات سارية المفعول.


<!-- @os:end -->
<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### الأجهزة

يتطلب هذا الدليل أربع وحدات Ryzen AI Halo ومحول شبكة إيثرنت واحد، متصلة بطوبولوجيا نجمية حيث تتصل كل وحدة مباشرة بالمحول.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | عقد الحوسبة التي تشكّل العنقود |
| محول إيثرنت بسرعة 10 جيجابت | 1 | محول مركزي للسماح بالاتصال متعدد العقد بين أنظمة Ryzen AI Halo (4 منافذ على الأقل) |
| كابل إيثرنت | 4 | يربط كل وحدة Halo بالمحول (يُوصى بكابل من فئة Cat 7 أو أعلى) |

> **ملاحظة**: يلزم توفر أربعة منافذ في محول إيثرنت لربط وحدات Ryzen AI Halo الأربع. ويلزم منفذ خامس إذا كنت تصل إلى النموذج من جهاز عميل منفصل بدلاً من أحد وحدات Halo نفسها.

### البرمجيات
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
يُرجى تثبيت:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) مع حزمة عمل **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## إعداد العتاد الفعلي

> **ملاحظة**: أكمل هذه الخطوة على جميع الأجهزة الأربعة (الجهاز 1 إلى الجهاز 4).

قم بتوصيل كل وحدة Ryzen AI Halo بمحول الإيثرنت باستخدام كابل من فئة Cat 7 (أو أعلى). يؤدي هذا إلى إنشاء رابط بسرعة 10 جيجابت يُستخدم للاتصال عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

على كل جهاز، حدد اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه باسم `IFNAME`). شغّل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

يعرض هذا الأمر اسم الواجهة مباشرة، على سبيل المثال:

```bash
enp191s0
```

### 2. التحقق من سرعات رابط الشبكة

تأكد من أن الرابط نشط ويعمل بأقصى سرعة عن طريق التحقق من سرعة واجهتك:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **ملاحظة**: استبدل `<IFNAME>` باسم واجهة الإخراج من [1. تحديد واجهات الشبكة](#1-determine-network-interfaces)

يجب أن ترى سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من ضبط منفذ المحول على 10 جيجابت. تتطلب بعض المحولات تعطيل التفاوض التلقائي (auto-negotiation) وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

<!-- @os:end -->

<!-- @os:windows -->
### التحقق من سرعة رابط الشبكة

على كل جهاز، تحقق من سرعة رابط واجهات الشبكة الخاصة بك:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

يجب أن تكون واجهة الإيثرنت الخاصة بك `Up` وتعمل بسرعة `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من ضبط منفذ المحول على 10 جيجابت. تتطلب بعض المحولات تعطيل التفاوض التلقائي (auto-negotiation) وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على جميع الأجهزة الأربعة (الجهاز 1 إلى الجهاز 4).

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات معدة مسبقًا، الإعداد الأسرع
- [الخيار 2: بناء يدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في خيارات البناء

### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK نسخًا بنائية ليلية (nightly builds) من llama.cpp مع تسريع AMD ROCm 7، تستهدف وحدات GPU مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وبنى Radeon الحديثة الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) لديك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية

قم بفك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مبنية مسبقًا ومفعّلة لـ ROCm من `llama-cli.exe` و`llama-server.exe` و`ggml-rpc-server.exe`، مُجمَّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

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

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) لديك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية وتجهيزها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مبنية مسبقًا ومفعّلة لـ ROCm من `llama-cli` و`llama-server` و`rpc-server`، مُجمَّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

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

أضف HIP إلى مسارك وقم بالبناء مع دعم ROCm وRPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | تفعيل حزمة برمجيات ROCm/HIP |
| `-DGGML_RPC=ON` | تفعيل RPC للاستدلال الموزع |
| `-DGPU_TARGETS=gfx1151` | استهداف وحدة معالجة رسومات Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | استخدام نظام بناء Ninja |

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

قامت خطوة البناء أعلاه بضبط `%HIP_PATH%\bin` للجلسة الحالية فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في x64 Native Tools Command Prompt)، أضفها بشكل دائم إلى `PATH` الخاص بالمستخدم:

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
| `-DGGML_HIP=ON` | تفعيل حزمة برمجيات ROCm |
| `-DGGML_RPC=ON` | تفعيل RPC للاستدلال الموزع |
| `-DAMDGPU_TARGETS="gfx1151"` | استهداف وحدة معالجة رسومات Ryzen AI Halo (Radeon 8060s) |

للمزيد من خيارات البناء، راجع [وثائق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

يستخدم هذا الدليل [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) بترميز `UD-Q2_K_XL` من [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). يتناسب هذا الترميز مع ذاكرة وحدة معالجة الرسومات المجمعة لأربع عقد Ryzen AI Halo.

قم بتنزيل ملفات GGUF باستخدام واجهة سطر الأوامر الخاصة بـ Hugging Face:
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

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز 1 (وحدة التحكم). لا تحتاج عقد العمل الخاصة بـ RPC (الأجهزة 2 و3 و4) إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يتيح محرك RPC (Remote Procedure Call) الخاص بـ llama.cpp لمثيل واحد من llama.cpp تفويض طبقات النموذج إلى عمال بعيدين عبر الشبكة. يعمل جهاز واحد بصفته **وحدة التحكم** (الجهاز 1)، حيث يتولى الترميز والجدولة والتنسيق. تشغّل الأجهزة الثلاثة الأخرى كل منها **خادم RPC** خفيف الوزن (الأجهزة 2 و3 و4) يعرض ذاكرة وحدة معالجة الرسومات الخاصة به وقدراته الحوسبية لوحدة التحكم.

في وقت التحميل، يقوم llama.cpp بتقسيم النموذج عبر جميع العقد الأربع. بمجرد التحميل، يستمر الاستدلال كما لو كان يعمل على مسرّع واحد. يتعامل RPC مع عمليات نقل المصفوفات (tensors) والتزامن خلف الكواليس.

### الخطوة 1: بدء تشغيل خوادم RPC (الأجهزة 2 و3 و4)

على كل من الأجهزة 2 و3 و4، ابدأ تشغيل خادم RPC لعرض موارد وحدة معالجة الرسومات الخاصة به على وحدة التحكم:
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
| `-p` | المنفذ الذي سيُبث عليه خادم RPC |
| `-c` | تفعيل ذاكرة تخزين مؤقت محلية للمصفوفات (tensors) الكبيرة، مما يتجنب عمليات النقل الشبكية المتكررة أثناء تحميل النموذج |
| `--host` | عنوان IP الذي سيُربط به خادم RPC (`0.0.0.0` لجميع الواجهات) |

للمزيد من الخيارات، راجع [وثائق RPC الخاصة بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خوادم RPC على الأجهزة 2 و3 و4، قم بتشغيل الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.
#### llama-cli

توفر `llama-cli` واجهة قائمة على الطرفية (terminal) للتفاعل المباشر مع النموذج. وهي مثالية لقياس الأداء وتصحيح الأخطاء والتجريب على مستوى منخفض.

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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الجهاز 2 والجهاز 3 والجهاز 4، شغّل الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في الطرفية (Powershell).

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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الجهاز 2 والجهاز 3 والجهاز 4، شغّل الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، تعرض `llama-cli` تقدم تحميل النموذج وتدخل في موجّه تفاعلي حيث يمكنك الدردشة مباشرة مع النموذج:

![تشغيل llama-cli لنموذج Kimi K2.6 عبر أربع عقد](assets/llama-cli-example.png)

#### llama-server

تعرض `llama-server` نفس محرك الاستدلال من خلال عملية خادم دائمة مع واجهة مستخدم ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. وهذه هي الواجهة المفضلة للنشر طويل الأمد، والوصول متعدد المستخدمين، والتكامل مع الأدوات الخارجية.

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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الجهاز 2 والجهاز 3 والجهاز 4، شغّل الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في الطرفية (Powershell).

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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: على كل من الجهاز 2 والجهاز 3 والجهاز 4، شغّل الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد البدء، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة الويب المدمجة. توفر هذه الواجهة واجهة دردشة قائمة على المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server أثناء تشغيل نموذج Kimi K2.6 عبر أربع عقد](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00008`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | يمكّن rocWMMA Flash Attention لتحسين الأداء على وحدات معالجة الرسومات AMD |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسومات |
| `-lm none` | يضبط وضع تحميل النموذج على `none`، مما يعطل التخطيط في الذاكرة (memory-mapping) لتقليل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام (RAM) لكنه يناسب ذاكرة الفيديو (VRAM) |
| `-b` | حجم الدفعة المنطقية بالرموز (tokens). ضبطها على 4096 يوازن بين الإنتاجية واستخدام الذاكرة عبر العقد |
| `-ub` | حجم الدفعة الفعلية (المصغرة) لمعالجة الموجّه (prompt). مطابقتها مع `-b` تتجنب أعباء التقسيم غير الضرورية |
| `--host` | عنوان IP لربط `llama-server` به (خاص بـ `llama-server` فقط) |
| `--port` | المنفذ لتقديم واجهة برمجة تطبيقات HTTP عليه (خاص بـ `llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل من نقاط نهاية عامل RPC (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، راجع [وثائق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[وثائق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: تعرض `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` باستخدام أي مفتاح API نائب (مثل `none`) للاتصال بمجموعتك
- **استكشاف نماذج أخرى**: تصفح ملفات GGUF المكمّمة على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تناسب ذاكرة وحدة معالجة الرسومات المجمعة لمجموعتك
- **التوسع لما بعد أربع عقد**: أضف المزيد من أنظمة Ryzen AI Halo كعمال RPC إضافيين للوصول إلى نماذج تتجاوز مقياس التريليون معامل. مرر نقاط نهاية إضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)