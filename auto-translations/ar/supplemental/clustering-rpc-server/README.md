<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# تجميع نظامَي Ryzen™ AI Halo باستخدام RPC

## نظرة عامة

نظام Ryzen™ AI Halo الخاص بك قادر بالفعل على تشغيل نماذج اللغة الكبيرة محليًا. يأخذ التجميع هذا إلى مستوى أبعد من خلال دمج ذاكرة GPU لأنظمة متعددة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر بكثير تتمتع بقدرة استدلال أقوى، وتوليد أفضل للكود، وفهم متعدد اللغات أعمق، وكل ذلك على أجهزتك الخاصة تمامًا.

يعلّمك هذا الدليل كيفية تجميع نظامَي Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp وتشغيل GLM 4.7، وهو نموذج بـ 358 مليار معامل، عبر كلا الجهازين مع تسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm و RPC
- تهيئة عامل RPC وإطلاق الاستدلال الموزع عبر عقدتين
- تشغيل نموذج بـ 358 مليار معامل عبر نظامَي Ryzen AI Halo متصلَين بالشبكة

## ضبط إعداد الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على كلٍّ من الجهاز 1 والجهاز 2.

<!-- @os:windows -->
على Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (iGPU VRAM).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 GB**. يرجى إعادة تشغيل النظام لتفعيل التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على Linux، يستخدم ROCm مجموعة ذاكرة نظام مشتركة، وتُهيَّأ هذه المجموعة افتراضيًا بنصف ذاكرة النظام.

يمكن زيادة هذا المقدار عن طريق تغيير إعداد صفحة Translation Table Manager (TTM) الخاصة بالنواة، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من VRAM المخصصة في BIOS (0.5 GB).

* ثبّت أداة pipx وأضف المسار الخاص بالعجلات المثبتة عبر pipx إلى مسار البحث في النظام.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* ثبّت عجلة amd-debug-tools من PyPI.
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

* أعد تشغيل النظام لتفعيل التغييرات.


<!-- @os:end -->
<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### الأجهزة

يتطلب هذا الدليل وحدتَي Ryzen AI Halo ومحوّل Ethernet واحد، متصلَين في طوبولوجيا نجمية مع توصيل كل وحدة مباشرةً بالمحوّل.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | عقد الحوسبة التي تشكّل المجموعة |
| محوّل Ethernet بسرعة 10Gbps | 1 | محوّل مركزي يتيح التواصل بين وحدات Ryzen AI Halo المتعددة (منفذان على الأقل) |
| كابل Ethernet | 2 | يوصّل كل وحدة Halo بالمحوّل (يُوصى باستخدام Cat 7 أو أعلى) |

> **ملاحظة**: يلزم وجود منفذَي محوّل Ethernet لتوصيل وحدتَي Ryzen AI Halo. يلزم وجود منفذ ثالث إذا كنت تصل إلى النموذج من جهاز عميل منفصل بدلًا من إحدى وحدتَي Halo.

### البرامج
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
يرجى تثبيت:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) مع حمل العمل **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## إعداد الأجهزة المادية

> **ملاحظة**: أكمل هذه الخطوة على كلٍّ من الجهاز 1 والجهاز 2.

وصّل كل وحدة Ryzen AI Halo بمحوّل Ethernet باستخدام كابل Cat 7 (أو أعلى). يُنشئ هذا الاتصال رابط 10Gbps المستخدم للتواصل عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

على كل جهاز، ابحث عن اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه بـ `IFNAME`). شغّل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

يطبع هذا اسم الواجهة مباشرةً، على سبيل المثال:

```bash
enp191s0
```

### 2. التحقق من سرعات رابط الشبكة

تأكد من أن الرابط نشط ويعمل بالسرعة الكاملة عن طريق التحقق من سرعة واجهتك:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **ملاحظة**: استبدل `<IFNAME>` باسم الواجهة الناتج من [1. تحديد واجهات الشبكة](#1-determine-network-interfaces)

يجب أن ترى سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يتم تفعيل الرابط، تحقق من توصيل الكابل وتأكد من ضبط منفذ المحوّل على 10Gbps. تتطلب بعض المحوّلات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ ارجع إلى وثائق المحوّل الخاص بك.

<!-- @os:end -->

<!-- @os:windows -->
### التحقق من سرعة رابط الشبكة

على كل جهاز، تحقق من سرعة رابط واجهات الشبكة الخاصة بك:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

يجب أن تكون واجهة Ethernet الخاصة بك في حالة `Up` وتعمل بسرعة `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يتم تفعيل الرابط، تحقق من توصيل الكابل وتأكد من ضبط منفذ المحوّل على 10Gbps. تتطلب بعض المحوّلات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ ارجع إلى وثائق المحوّل الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على كلٍّ من الجهاز 1 والجهاز 2.

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ملفات ثنائية مبنية مسبقًا، أسرع إعداد
- [الخيار 2: البناء اليدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في أعلام البناء

### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK إصدارات ليلية من llama.cpp مع تسريع AMD ROCm 7، تستهدف GPU مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وبنيات Radeon الحديثة الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية المبنية مسبقًا

انتقل إلى صفحة الإصدار الأحدث ونزّل الأرشيف المطابق لمنصتك وهدف GPU الخاص بك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

نزّل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية

فكّ ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مُمكَّنة بـ ROCm من `llama-cli.exe` و`llama-server.exe` و`rpc-server.exe`، مُجمَّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف GPU

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
#### الخطوة 1: تنزيل الملفات الثنائية المبنية مسبقًا

انتقل إلى صفحة الإصدار الأحدث ونزّل الأرشيف المطابق لمنصتك وهدف GPU الخاص بك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

نزّل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية وإعدادها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مُمكَّنة بـ ROCm من `llama-cli` و`llama-server` و`rpc-server`، مُجمَّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف GPU

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
بعد إعداد llama.cpp على كل عقدة، انتقل إلى [تنزيل النموذج](#downloading-the-model).

### الخيار 2: البناء اليدوي من المصدر

<!-- @os:windows -->
#### الخطوة 1: بناء llama.cpp

افتح **x64 Native Tools Command Prompt** (المثبت مع Visual Studio Build Tools) واستنسخ المستودع:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

أضف HIP إلى مسارك وابنِ مع دعم ROCm و RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علم البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُمكّن مجموعة برامج ROCm/HIP |
| `-DGGML_RPC=ON` | يُمكّن RPC للاستدلال الموزع |
| `-DGPU_TARGETS=gfx1151` | يستهدف GPU الخاص بـ Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | يستخدم نظام بناء Ninja |

#### الخطوة 2: التحقق من اكتشاف GPU

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

ضبطت خطوة البناء أعلاه `%HIP_PATH%\bin` للجلسة الحالية فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط x64 Native Tools Command Prompt)، أضفها إلى `PATH` الخاص بمستخدمك بشكل دائم:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

بعد إعداد llama.cpp على كل عقدة، انتقل إلى [تنزيل النموذج](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### الخطوة 1: بناء llama.cpp

استنسخ المستودع:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

ابنِ مع دعم ROCm و RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| علم البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُمكّن مجموعة برامج ROCm |
| `-DGGML_RPC=ON` | يُمكّن RPC للاستدلال الموزع |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | يُمكّن rocWMMA لتحسين Flash Attention على GPU من AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | يستهدف GPU الخاص بـ Ryzen AI Halo (Radeon 8060s) |

لمزيد من خيارات البناء، ارجع إلى [وثائق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### الخطوة 2: التحقق من اكتشاف GPU

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

بعد إعداد llama.cpp على كل عقدة، انتقل إلى [تنزيل النموذج](#downloading-the-model).
<!-- @os:end -->

## تنزيل النموذج

يستخدم هذا الدليل [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)، وهو نموذج بـ 358 مليار معامل بتكميم `Q4_K_XL` من [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). عند هذا التكميم يتطلب النموذج ما يقارب 205GB من التخزين ويتناسب مع الذاكرة المجمّعة لـ GPU لعقدتَي Ryzen AI Halo.

نزّل ملفات GGUF باستخدام Hugging Face CLI:
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

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز 1 (وحدة التحكم). لا تحتاج عقد عامل RPC إلى نسخة محلية من ملفات النموذج.

## إطلاق النموذج على المجموعة

يتيح محرك RPC (استدعاء الإجراء عن بُعد) الخاص بـ llama.cpp لمثيل واحد من llama.cpp تفريغ طبقات النموذج إلى عمال بعيدين عبر الشبكة. يعمل أحد الأجهزة كـ **وحدة تحكم** (الجهاز 1)، يتولى الترميز والجدولة والتنسيق. يشغّل الجهاز الآخر **خادم RPC** خفيف الوزن (الجهاز 2) يكشف ذاكرة GPU وقدرة الحوسبة الخاصة به لوحدة التحكم.

عند التحميل، يقسّم llama.cpp النموذج عبر كلتا العقدتين. بمجرد التحميل، يتقدم الاستدلال كما لو كان يعمل على مسرّع واحد. يتولى RPC نقل الموترات والمزامنة خلف الكواليس.

### الخطوة 1: تشغيل خادم RPC (الجهاز 2)

على الجهاز 2، شغّل خادم RPC لكشف موارد GPU الخاصة به لوحدة التحكم:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| العلم | الغرض |
|------|---------|
| `-p` | المنفذ الذي يبث عليه خادم RPC |
| `-c` | يُمكّن ذاكرة تخزين مؤقت محلية للموترات الكبيرة، مما يتجنب عمليات النقل المتكررة عبر الشبكة أثناء تحميل النموذج |
| `--host` | عنوان IP لربط خادم RPC به (`0.0.0.0` لجميع الواجهات) |

لمزيد من الخيارات، ارجع إلى [وثائق llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: إطلاق النموذج (الجهاز 1)

مع تشغيل خادم RPC على الجهاز 2، أطلق الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.

#### llama-cli

يوفر `llama-cli` واجهة قائمة على الطرفية للتفاعل المباشر مع النموذج. وهو مثالي للقياس المعياري والتصحيح والتجريب على المستوى المنخفض.

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) للعثور على عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، يعرض `llama-cli` تقدم تحميل النموذج ويدخل في موجه تفاعلي حيث يمكنك الدردشة مباشرةً مع النموذج:

![llama-cli يشغّل GLM 4.7 عبر عقدتين](assets/llama-cli-example.png)

#### llama-server

يكشف `llama-server` نفس محرك الاستدلال من خلال عملية خادم مستمرة مع واجهة مستخدم ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. هذه هي الواجهة المفضلة للنشر طويل الأمد والوصول متعدد المستخدمين والتكامل مع الأدوات الخارجية.

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في Terminal (Powershell).

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد التشغيل، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة المستخدم الويب المدمجة. توفر هذه واجهة دردشة قائمة على المتصفح للتفاعل مع النموذج:

![واجهة مستخدم ويب llama-server تشغّل GLM 4.7 عبر عقدتين](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلم | الغرض |
|------|---------|
| `-m` | المسار إلى ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00005`) |
| `-c` | حجم السياق بالرموز. تستخدم القيم الأكبر ذاكرة أكثر |
| `-fa on` | يُمكّن rocWMMA Flash Attention لتحسين الأداء على GPU من AMD |
| `-ngl 999` | يفرّغ جميع طبقات النموذج إلى GPU |
| `--no-mmap` | يعطّل تعيين الذاكرة، مما يقلل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة RAM للنظام لكنه يتناسب مع VRAM |
| `--host` | عنوان IP لربط `llama-server` به (خاص بـ `llama-server` فقط) |
| `--port` | المنفذ لخدمة واجهة برمجة تطبيقات HTTP عليه (خاص بـ `llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل من نقاط نهاية عامل RPC (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، ارجع إلى [وثائق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[وثائق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **توصيل تطبيقات الطرف الثالث**: يكشف `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API نائب (مثل `none`) للاتصال بمجموعتك
- **استكشاف نماذج أخرى**: تصفح ملفات GGUF المكمَّمة على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تتناسب مع الذاكرة المجمّعة لـ GPU في مجموعتك
- **التوسع إلى أربع عقد**: أضف نظامَي Ryzen AI Halo إضافيَّين كعمال RPC إضافيين للوصول إلى نماذج بحجم تريليون معامل. مرّر نقاط النهاية الإضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)