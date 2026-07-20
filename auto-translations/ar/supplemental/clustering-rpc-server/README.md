<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل الإرشادي علامات خاصة لا يمكن لـ GitHub عرضها. يرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

# تجميع نظامين من Ryzen™ AI Halo باستخدام RPC

## نظرة عامة

يتمتع نظام Ryzen™ AI Halo لديك بالفعل بالقدرة على تشغيل نماذج اللغة الكبيرة محليًا. يأخذ التجميع هذا إلى مستوى أبعد من خلال دمج ذاكرة GPU الخاصة بأنظمة متعددة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر بقدرات استدلال أقوى، وتوليد أكواد أفضل، وفهم متعدد اللغات أعمق، كل ذلك على عتادك الخاص بالكامل.

يعلّمك هذا الدليل الإرشادي كيفية تجميع نظامين من Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp وتشغيل GLM 4.7، وهو نموذج بحجم 358 مليار معامل، عبر كلا الجهازين بتسريع من AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm وRPC
- إعداد عامل RPC (RPC worker) وتشغيل الاستدلال الموزع عبر عقدتين
- تشغيل نموذج بحجم 358 مليار معامل عبر نظامين من Ryzen AI Halo متصلين بشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

<!-- @os:windows -->
على Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (iGPU VRAM).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. عيّن القيمة إلى **96 جيجابايت**. يرجى إعادة تشغيل النظام لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على Linux، يستخدم ROCm مجمّع ذاكرة نظام مشترك، ويُضبط هذا المجمّع افتراضيًا على نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحة مدير جدول الترجمة (TTM) الخاص بالنواة، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 جيجابايت).

* ثبّت أداة pipx وأضف مسار الحزم المثبتة عبر pipx إلى مسار بحث النظام.

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

* أعد تشغيل النظام لتصبح التغييرات سارية المفعول.


<!-- @os:end -->
<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### العتاد

يتطلب هذا الدليل الإرشادي وحدتي Ryzen AI Halo ومحوّل شبكة إيثرنت واحد، متصلين في طوبولوجيا نجمية مع توصيل كل وحدة مباشرة بالمحوّل.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | عقد الحوسبة التي تشكّل العنقود (cluster) |
| محوّل إيثرنت بسرعة 10 جيجابت في الثانية | 1 | محوّل مركزي للسماح بالتواصل بين عقد Ryzen AI Halo المتعددة (منفذان على الأقل) |
| كابل إيثرنت | 2 | يصل كل وحدة Halo بالمحوّل (يُوصى بفئة Cat 7 أو أعلى) |

> **ملاحظة**: يلزم توفر منفذين في محوّل الإيثرنت لتوصيل وحدتي Ryzen AI Halo. يلزم منفذ ثالث إذا كنت تصل إلى النموذج من جهاز عميل منفصل بدلاً من الوصول من إحدى وحدتي Halo.

### البرامج
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
يرجى تثبيت:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) مع حزمة عمل **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## إعداد العتاد الفعلي

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

وصّل كل وحدة من Ryzen AI Halo بمحوّل الإيثرنت باستخدام كابل من فئة Cat 7 (أو أعلى). يؤدي هذا إلى إنشاء رابط بسرعة 10 جيجابت في الثانية يُستخدم للتواصل عالي السرعة بين العقد.
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

تأكد من أن الرابط نشط ويعمل بأقصى سرعة عن طريق فحص سرعة واجهتك:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **ملاحظة**: استبدل `<IFNAME>` باسم واجهة الإخراج من [1. تحديد واجهات الشبكة](#1-determine-network-interfaces)

يجب أن ترى سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحوّل مضبوط على 10 جيجابت في الثانية. تتطلب بعض المحوّلات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحوّل الخاص بك.

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

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحوّل مضبوط على 10 جيجابت في الثانية. تتطلب بعض المحوّلات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحوّل الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات مبنية مسبقًا، إعداد أسرع
- [الخيار 2: البناء اليدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في خيارات البناء

### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK إصدارات ليلية من llama.cpp بتسريع AMD ROCm 7، تستهدف وحدات معالجة رسومية مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وبنى Radeon الحديثة الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك ووحدة معالجة الرسومات المستهدفة:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث يمثل `xxxx` رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية

قم بفك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مبنية لدعم ROCm من `llama-cli.exe` و `llama-server.exe` و `rpc-server.exe`، تم تجميعها مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات

```bash
.\llama-cli.exe --list-devices
```

المخرجات المتوقعة:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك ووحدة معالجة الرسومات المستهدفة:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث يمثل `xxxx` رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية وتجهيزها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مبنية لدعم ROCm من `llama-cli` و `llama-server` و `rpc-server`، تم تجميعها مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات

```bash
./llama-cli --list-devices
```

المخرجات المتوقعة:

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

أضف HIP إلى المسار الخاص بك وقم بالبناء مع دعم ROCm و RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يمكّن مكدس برمجيات ROCm/HIP |
| `-DGGML_RPC=ON` | يمكّن RPC للاستدلال الموزع |
| `-DGPU_TARGETS=gfx1151` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (‏Radeon 8060s) |
| `-G Ninja` | يستخدم نظام بناء Ninja |

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

المخرجات المتوقعة:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### الخطوة 3: إضافة HIP إلى مسار المستخدم الخاص بك

قامت خطوة البناء أعلاه بتعيين `%HIP_PATH%\bin` للجلسة الحالية فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في x64 Native Tools Command Prompt)، أضفها إلى `PATH` الخاص بمستخدمك بشكل دائم:

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

قم بالبناء مع دعم ROCm و RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يمكّن مكدس برمجيات ROCm |
| `-DGGML_RPC=ON` | يمكّن RPC للاستدلال الموزع |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | يمكّن rocWMMA لتحسين Flash Attention على وحدات معالجة الرسومات من AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (‏Radeon 8060s) |

للمزيد من خيارات البناء، راجع [وثائق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات

```bash
cd rocm/bin
./llama-cli --list-devices
```

المخرجات المتوقعة:

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

يستخدم هذا الدليل [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)، وهو نموذج بحجم 358 مليار معامل بتنسيق التكميم `Q4_K_XL` من [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). بهذا التكميم، يتطلب النموذج ما يقارب 205 جيجابايت من مساحة التخزين ويتناسب مع الذاكرة المجمعة لوحدتي معالجة الرسومات في عقدتي Ryzen AI Halo.

قم بتنزيل ملفات GGUF باستخدام واجهة سطر الأوامر الخاصة بـ Hugging Face:
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

## تشغيل النموذج على العنقود (Cluster)

يتيح محرك llama.cpp RPC (استدعاء الإجراء عن بُعد) لمثيل واحد من llama.cpp نقل طبقات النموذج إلى عمال بعيدين عبر الشبكة. يعمل جهاز واحد كـ **وحدة تحكم** (الجهاز 1)، حيث يتولى الترميز والجدولة والتنسيق. ويشغّل الجهاز الآخر **خادم RPC** خفيف الوزن (الجهاز 2) يعرض ذاكرة وحدة معالجة الرسومات الخاصة به وقدراته الحاسوبية لوحدة التحكم.

عند وقت التحميل، يقوم llama.cpp بتقسيم النموذج عبر كلا العقدتين. بمجرد التحميل، يستمر الاستدلال كما لو كان يعمل على مسرّع واحد. يتعامل RPC مع نقل الموترات (tensors) والمزامنة في الخلفية.

### الخطوة 1: تشغيل خادم RPC (الجهاز 2)

على الجهاز 2، قم بتشغيل خادم RPC لعرض موارد وحدة معالجة الرسومات الخاصة به لوحدة التحكم:
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

| العلامة | الغرض |
|------|---------|
| `-p` | المنفذ الذي يُبث عليه خادم RPC |
| `-c` | يمكّن ذاكرة تخزين مؤقت محلية للموترات الكبيرة، مما يتجنب عمليات النقل المتكررة عبر الشبكة أثناء تحميل النموذج |
| `--host` | عنوان IP الذي يُربط به خادم RPC (`0.0.0.0` لجميع الواجهات) |

للمزيد من الخيارات، راجع [وثائق RPC الخاصة بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خادم RPC على الجهاز 2، قم بتشغيل الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.

#### llama-cli

يوفر `llama-cli` واجهة قائمة على الطرفية للتفاعل المباشر مع النموذج. وهو مثالي للقياس المرجعي (benchmarking) والتصحيح والتجريب منخفض المستوى.

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

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، قم بتشغيل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: قم بتشغيل هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، قم بتشغيل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) للعثور على عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، يعرض `llama-cli` تقدم تحميل النموذج ويدخل إلى موجه أوامر تفاعلي حيث يمكنك الدردشة مباشرة مع النموذج:

![تشغيل llama-cli لنموذج GLM 4.7 عبر عقدتين](assets/llama-cli-example.png)
#### llama-server

يعرض `llama-server` نفس محرك الاستدلال من خلال عملية خادم دائمة مزودة بواجهة ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. هذه هي الواجهة المفضلة للنشر طويل الأمد، والوصول متعدد المستخدمين، والتكامل مع الأدوات الخارجية.

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في الطرفية (Powershell).

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد التشغيل، افتح `http://<HOST_IP>:8081` في المتصفح للوصول إلى واجهة الويب المدمجة. توفر هذه الواجهة واجهة دردشة قائمة على المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server تشغّل GLM 4.7 عبر عقدتين](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00005`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | يفعّل rocWMMA Flash Attention لتحسين الأداء على وحدات معالجة الرسومات AMD |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسومات (GPU) |
| `--no-mmap` | يعطّل التخطيط الذاكري (memory-mapping)، مما يقلل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام (RAM) لكنه يتناسب مع ذاكرة الفيديو (VRAM) |
| `--host` | عنوان IP لربط `llama-server` به (`llama-server` فقط) |
| `--port` | المنفذ لتقديم واجهة برمجة تطبيقات HTTP عليه (`llama-server` فقط) |
| `--rpc` | قائمة بنقاط نهاية عامل RPC مفصولة بفواصل (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، راجع [توثيق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[توثيق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: يعرض `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API عنصر نائب (مثل `none`) للاتصال بمجموعتك (cluster)
- **استكشاف نماذج أخرى**: تصفح ملفات GGUF المكمّمة على [Hugging Face](https://huggingface.co/models?search=gguf) لإيجاد النماذج التي تتناسب مع إجمالي ذاكرة وحدة معالجة الرسومات لمجموعتك
- **التوسع إلى أربع عقد**: أضف نظامي Ryzen AI Halo إضافيين كعمال RPC إضافيين للوصول إلى نماذج بحجم تريليون معامل (parameter). مرر نقاط النهاية الإضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)