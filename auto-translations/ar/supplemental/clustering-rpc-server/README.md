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

# تجميع نظامي Ryzen™ AI Halo باستخدام RPC

## نظرة عامة

نظام Ryzen™ AI Halo الخاص بك قادر بالفعل على تشغيل نماذج اللغة الكبيرة محليًا. تأخذ عملية التجميع (Clustering) هذا إلى مستوى أبعد من خلال دمج ذاكرة GPU لأنظمة متعددة عبر شبكة محلية، مما يتيح لك الوصول إلى نماذج أكبر بكثير ذات قدرات استدلال أقوى، وتوليد أكواد برمجية أفضل، وفهم أعمق للغات متعددة، وكل ذلك بالكامل على أجهزتك الخاصة.

يعلّمك دليل التشغيل هذا كيفية تجميع نظامي Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp وتشغيل نموذج GLM 4.7، وهو نموذج بـ 358 مليار معلمة، عبر كلا الجهازين بتسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm وRPC
- تهيئة عامل RPC (RPC worker) وتشغيل الاستدلال الموزّع عبر عقدتين
- تشغيل نموذج بـ 358 مليار معلمة عبر نظامي Ryzen AI Halo متصلين بالشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (ذاكرة VRAM الخاصة بـ iGPU).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 GB**. يُرجى إعادة تشغيل النظام لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، يستخدم ROCm مجمع ذاكرة نظام مشترك، وهذا المجمع مُهيأ افتراضيًا ليكون نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحات مدير جدول الترجمة (TTM) الخاص بالنواة (kernel)، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 GB).

* قم بتثبيت أداة pipx وإضافة المسار الخاص بحزم wheel المثبتة عبر pipx إلى مسار بحث النظام.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* قم بتثبيت حزمة wheel الخاصة بـ amd-debug-tools من PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* شغّل أداة amd-ttm للاستعلام عن الإعدادات الحالية للذاكرة المشتركة.
  ```bash
  amd-ttm
  ```

* أعد تهيئة إعدادات الذاكرة المشتركة إلى **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* أعد تشغيل النظام لتصبح التغييرات سارية المفعول.


<!-- @os:end -->
<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### العتاد (Hardware)

يتطلب دليل التشغيل هذا وحدتي Ryzen AI Halo ومحول شبكة إيثرنت واحد، متصلين بطوبولوجيا نجمية مع توصيل كل وحدة مباشرة بالمحول.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | عقد الحوسبة التي تشكّل المجموعة |
| محول شبكة إيثرنت بسرعة 10 جيجابت | 1 | محول مركزي للسماح بالاتصال متعدد العقد بين أنظمة Ryzen AI Halo (منفذان على الأقل) |
| كابل إيثرنت | 2 | يربط كل وحدة Halo بالمحول (يُوصى بفئة Cat 7 أو أعلى) |

> **ملاحظة**: يلزم توفر منفذين على محول الشبكة لتوصيل وحدتي Ryzen AI Halo. يلزم وجود منفذ ثالث إذا كنت تصل إلى النموذج من جهاز عميل منفصل بدلاً من الوصول من إحدى وحدتي Halo.

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

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

قم بتوصيل كل وحدة Ryzen AI Halo بمحول شبكة الإيثرنت باستخدام كابل من فئة Cat 7 (أو أعلى). يؤدي هذا إلى إنشاء رابط بسرعة 10 جيجابت يُستخدم للاتصال عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

في كل جهاز، ابحث عن اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه باسم `IFNAME`). شغّل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

يعرض هذا الأمر اسم الواجهة مباشرة، على سبيل المثال:

```bash
enp191s0
```

### 2. التحقق من سرعات روابط الشبكة

تأكد من أن الرابط نشط ويعمل بأقصى سرعة عن طريق فحص سرعة واجهتك:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **ملاحظة**: استبدل `<IFNAME>` باسم واجهة المخرجات من [1. تحديد واجهات الشبكة](#1-determine-network-interfaces)

يجب أن ترى سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحول مضبوط على 10 جيجابت. قد تتطلب بعض المحولات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

<!-- @os:end -->

<!-- @os:windows -->
### التحقق من سرعة رابط الشبكة

في كل جهاز، تحقق من سرعة رابط واجهات الشبكة الخاصة بك:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

يجب أن تكون واجهة الإيثرنت الخاصة بك `Up` وتعمل بسرعة `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحول مضبوط على 10 جيجابت. قد تتطلب بعض المحولات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات جاهزة مسبقة البناء، الإعداد الأسرع
- [الخيار 2: بناء يدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في خيارات البناء

### الخيار 1: Lemonade SDK (موصى به)

يوفّر Lemonade SDK إصدارات ليلية (nightly builds) من llama.cpp بتسريع AMD ROCm 7، تستهدف وحدات معالجة رسومية مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وبنيات Radeon الحديثة الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) الخاصة بك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية

قم بفك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مبنية بدعم ROCm من `llama-cli.exe` و`llama-server.exe` و`rpc-server.exe`، مُجمّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) الخاصة بك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج وتجهيز الملفات الثنائية

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مبنية بدعم ROCm من `llama-cli` و`llama-server` و`rpc-server`، مُجمّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

افتح **موجه أوامر أدوات x64 الأصلية** (المثبت مع Visual Studio Build Tools) واستنسخ المستودع:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

أضف HIP إلى مسارك وابنِ مع دعم ROCm وRPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علم البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُفعّل حزمة برمجيات ROCm/HIP |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزع |
| `-DGPU_TARGETS=gfx1151` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | يستخدم نظام بناء Ninja |

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

قامت خطوة البناء أعلاه بتعيين `%HIP_PATH%\bin` للجلسة الحالية فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في موجه أوامر أدوات x64 الأصلية)، أضفها بشكل دائم إلى `PATH` الخاص بمستخدمك:

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

ابنِ مع دعم ROCm وRPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| علم البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُفعّل حزمة برمجيات ROCm |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزع |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | يُفعّل rocWMMA لتحسين Flash Attention على وحدات معالجة الرسومات AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (Radeon 8060s) |

لمزيد من خيارات البناء، راجع [وثائق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

يستخدم هذا الدليل [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)، وهو نموذج بـ358 مليار معلمة بتكميم `Q4_K_XL` من [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). عند هذا التكميم، يتطلب النموذج حوالي 205 جيجابايت من مساحة التخزين ويتناسب مع ذاكرة وحدة معالجة الرسومات المجمعة لعقدتي Ryzen AI Halo.

قم بتنزيل ملفات GGUF باستخدام واجهة سطر أوامر Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز 1 (المتحكم). لا تحتاج عقد العمال RPC إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يتيح محرك RPC (استدعاء الإجراءات عن بُعد) الخاص بـ llama.cpp لمثيل واحد من llama.cpp تفريغ طبقات النموذج إلى عمال عن بُعد عبر الشبكة. يعمل جهاز واحد بمثابة **المتحكم** (الجهاز 1)، حيث يتولى الترميز والجدولة والتنسيق. ويشغّل الجهاز الآخر **خادم RPC** خفيف الوزن (الجهاز 2) الذي يعرض ذاكرة وحدة معالجة الرسومات والحوسبة الخاصة به للمتحكم.

عند وقت التحميل، يقسّم llama.cpp النموذج عبر كلا العقدتين. بمجرد التحميل، يستمر الاستدلال كما لو كان يعمل على مسرّع واحد. يتعامل RPC مع عمليات نقل الموترات (tensor) والمزامنة خلف الكواليس.

### الخطوة 1: بدء تشغيل خادم RPC (الجهاز 2)

على الجهاز 2، ابدأ تشغيل خادم RPC لعرض موارد وحدة معالجة الرسومات الخاصة به على المتحكم:
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

| العلم | الغرض |
|------|---------|
| `-p` | المنفذ الذي سيُبث عليه خادم RPC |
| `-c` | يُفعّل ذاكرة تخزين مؤقت محلية للموترات الكبيرة، مما يتجنب عمليات نقل الشبكة المتكررة أثناء تحميل النموذج |
| `--host` | عنوان IP الذي سيُربط به خادم RPC (`0.0.0.0` لجميع الواجهات) |

لمزيد من الخيارات، راجع [وثائق RPC الخاصة بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خادم RPC على الجهاز 2، ابدأ الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.

#### llama-cli

يوفر `llama-cli` واجهة قائمة على الطرفية للتفاعل المباشر مع النموذج. وهو مثالي لقياس الأداء وتصحيح الأخطاء والتجريب على مستوى منخفض.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، يعرض `llama-cli` تقدّم تحميل النموذج ويدخل في موجه تفاعلي حيث يمكنك الدردشة مباشرة مع النموذج:

![تشغيل llama-cli لنموذج GLM 4.7 عبر عقدتين](assets/llama-cli-example.png)
#### llama-server

يوفّر `llama-server` نفس محرك الاستدلال من خلال عملية خادم مستمرة مزوّدة بواجهة ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. تُعد هذه الواجهة الخيار المفضّل لعمليات النشر طويلة الأمد، والوصول المتعدد المستخدمين، والتكامل مع الأدوات الخارجية.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل الأمر `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: نفّذ هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد التشغيل، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة الويب المدمجة. توفّر هذه الواجهة تجربة دردشة عبر المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server أثناء تشغيل GLM 4.7 عبر عقدتين](assets/llama-server-example.png)

<!-- @os:linux -->
> **العثور على `<HOST_IP>`**: على الجهاز 1، شغّل الأمر `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **العثور على `<HOST_IP>`**: على الجهاز 1، شغّل الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة (Flag) | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00005`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | تفعيل rocWMMA Flash Attention لتحسين الأداء على معالجات AMD الرسومية |
| `-ngl 999` | نقل جميع طبقات النموذج إلى المعالج الرسومي (GPU) |
| `--no-mmap` | تعطيل التخطيط الذاكري (memory-mapping)، مما يقلل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام العشوائية لكنه يتناسب مع ذاكرة VRAM |
| `--host` | عنوان IP لربط `llama-server` به (خاص بـ `llama-server` فقط) |
| `--port` | المنفذ الذي تُقدَّم عليه واجهة برمجة التطبيقات HTTP (خاص بـ `llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل لنقاط نهاية عمّال RPC (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، راجع [وثائق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[وثائق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات خارجية**: يوفّر `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API افتراضي (مثل `none`) للاتصال بمجموعتك
- **استكشاف نماذج أخرى**: تصفّح ملفات GGUF المُكمّمة على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تتناسب مع إجمالي ذاكرة المعالج الرسومي في مجموعتك
- **التوسع إلى أربع عقد**: أضف نظامي Ryzen AI Halo إضافيين كعمّال RPC إضافيين للوصول إلى نماذج بحجم تريليون معامل. مرّر نقاط النهاية الإضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)