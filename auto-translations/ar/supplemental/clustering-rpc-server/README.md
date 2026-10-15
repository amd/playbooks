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

# تجميع نظامي Ryzen™ AI Halo في عنقود باستخدام RPC

## نظرة عامة

جهاز Ryzen™ AI Halo الخاص بك قادر بالفعل على تشغيل نماذج اللغة الكبيرة محليًا. يأخذ التجميع (Clustering) هذه القدرة إلى مستوى أبعد من خلال دمج ذاكرة GPU لأنظمة متعددة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر حجمًا بقدرات استدلال أقوى، وتوليد أكواد أفضل، وفهم متعدد اللغات أعمق، وكل ذلك على أجهزتك الخاصة بالكامل.

يعلمك هذا الدليل كيفية تجميع نظامي Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp وتشغيل نموذج GLM 4.7، وهو نموذج بمعامل 358 مليار، عبر كلا الجهازين بتسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm و RPC
- تكوين عامل RPC وإطلاق الاستدلال الموزع عبر عقدتين
- تشغيل نموذج بمعامل 358 مليار عبر نظامي Ryzen AI Halo متصلين بالشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص ذاكرة الرسومات المتغيرة من AMD (iGPU VRAM).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 GB**. يرجى إعادة تشغيل النظام حتى تصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، يستخدم ROCm مجمعًا مشتركًا لذاكرة النظام، وهذا المجمع مُهيّأ افتراضيًا ليكون نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحات مدير جدول الترجمة (TTM) الخاص بالنواة، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من VRAM المخصص في BIOS (0.5 GB).

* قم بتثبيت أداة pipx وأضف مسار عجلات (wheels) pipx المثبتة إلى مسار البحث الخاص بالنظام.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* قم بتثبيت عجلة amd-debug-tools من PyPI.
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

* أعد تشغيل النظام حتى تصبح التغييرات سارية المفعول.


<!-- @os:end -->
<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### العتاد (Hardware)

يتطلب هذا الدليل وحدتي Ryzen AI Halo ومحول شبكة إيثرنت واحد، متصلين في طوبولوجيا نجمية مع توصيل كل وحدة مباشرة بالمحول.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | عقد الحوسبة التي تشكّل العنقود |
| محول إيثرنت بسرعة 10 جيجابت | 1 | محول مركزي للسماح بتواصل عدة عقد Ryzen AI Halo (منفذان على الأقل) |
| كابل إيثرنت | 2 | يربط كل وحدة Halo بالمحول (يُفضّل Cat 7 أو أعلى) |

> **ملاحظة**: يلزم منفذان في محول الإيثرنت لتوصيل وحدتي Ryzen AI Halo. يلزم منفذ ثالث إذا كنت ستصل إلى النموذج من جهاز عميل منفصل بدلًا من إحدى وحدتي Halo.

### البرمجيات
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
يرجى تثبيت:
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

قم بتوصيل كل وحدة Ryzen AI Halo بمحول الإيثرنت باستخدام كابل Cat 7 (أو أعلى). يُنشئ هذا رابط 10 جيجابت المستخدم للتواصل عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

على كل جهاز، اعثر على اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه بـ `IFNAME`). قم بتشغيل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

يطبع هذا اسم الواجهة مباشرة، على سبيل المثال:

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

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحول مضبوط على 10 جيجابت. تتطلب بعض المحولات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

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

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحول مضبوط على 10 جيجابت. تتطلب بعض المحولات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات مبنية مسبقًا، إعداد أسرع
- [الخيار 2: بناء يدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في أعلام البناء

### الخيار 1: Lemonade SDK (موصى به)

توفر Lemonade SDK إصدارات ليلية (nightly) من llama.cpp بتسريع AMD ROCm 7، تستهدف وحدات GPU مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وبنى Radeon الحديثة الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية المُجهّزة مسبقًا

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) لديك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية

فك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات ROCm-enabled من `llama-cli.exe` و`llama-server.exe` و`rpc-server.exe`، مُترجمة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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
#### الخطوة 1: تنزيل الملفات الثنائية المُجهّزة مسبقًا

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) لديك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية وتجهيزها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات ROCm-enabled من `llama-cli` و`llama-server` و`rpc-server`، مُترجمة مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

أضف HIP إلى مسارك وقم بالبناء مع دعم ROCm وRPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُفعّل مجموعة برمجيات ROCm/HIP |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزّع |
| `-DGPU_TARGETS=gfx1151` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | يستخدم نظام البناء Ninja |

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

قم بالبناء مع دعم ROCm وRPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | يُفعّل مجموعة برمجيات ROCm |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزّع |
| `-DAMDGPU_TARGETS="gfx1151"` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (Radeon 8060s) |

لمزيد من خيارات البناء، راجع [وثائق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### الخطوة 2: التحقق من اكتشاف وحدة معالجة الرسومات (GPU)

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

يستخدم هذا الدليل [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)، وهو نموذج بمعامِلات 358B بترميز `Q4_K_XL` من [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). عند هذا الترميز، يتطلب النموذج ما يقارب 205 جيجابايت من التخزين ويتناسب مع الذاكرة المجمعة لوحدتي معالجة الرسومات (GPU) في عقدتي Ryzen AI Halo.

قم بتنزيل ملفات GGUF باستخدام واجهة سطر الأوامر Hugging Face:
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

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز 1 (وحدة التحكم). لا تحتاج عقد عمّال RPC إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يتيح محرك llama.cpp RPC (استدعاء الإجراء عن بُعد) لنسخة واحدة من llama.cpp تفريغ طبقات النموذج إلى عمّال عن بُعد عبر الشبكة. يعمل جهاز واحد بوصفه **وحدة التحكم** (الجهاز 1)، حيث يتولى الترميز والجدولة والتنسيق. ويشغّل الجهاز الآخر **خادم RPC** خفيف الوزن (الجهاز 2) يعرض ذاكرة وحدة معالجة الرسومات (GPU) وقدرته الحسابية لوحدة التحكم.

عند وقت التحميل، يقسّم llama.cpp النموذج عبر كلتا العقدتين. وبمجرد التحميل، يتم تنفيذ الاستدلال كما لو كان يعمل على مسرّع واحد. يتولى RPC عمليات نقل الموترات (tensors) والمزامنة خلف الكواليس.

### الخطوة 1: بدء تشغيل خادم RPC (الجهاز 2)

على الجهاز 2، ابدأ تشغيل خادم RPC لعرض موارد وحدة معالجة الرسومات (GPU) الخاصة به لوحدة التحكم:
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
| `-c` | يُفعّل ذاكرة تخزين مؤقتة محلية للموترات (tensors) الكبيرة، مما يتجنب عمليات النقل الشبكي المتكررة أثناء تحميل النموذج |
| `--host` | عنوان IP لربط خادم RPC به (`0.0.0.0` لجميع الواجهات) |

لمزيد من الخيارات، راجع [وثائق llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خادم RPC على الجهاز 2، شغّل الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.

#### llama-cli

توفر `llama-cli` واجهة قائمة على الطرفية للتفاعل مباشرة مع النموذج. وهي مثالية للقياس المرجعي وتصحيح الأخطاء والتجريب على مستوى منخفض.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) للعثور على عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، تعرض `llama-cli` تقدم تحميل النموذج وتدخل في محث تفاعلي حيث يمكنك الدردشة مباشرة مع النموذج:

![تشغيل llama-cli لنموذج GLM 4.7 عبر عقدتين](assets/llama-cli-example.png)
#### llama-server

يقوم `llama-server` بكشف محرك الاستدلال نفسه من خلال عملية خادم مستمرة مع واجهة ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. هذه هي الواجهة المفضلة للنشر طويل الأمد، والوصول متعدد المستخدمين، والتكامل مع الأدوات الخارجية.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **العثور على `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد التشغيل، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة الويب المدمجة. توفر هذه الواجهة واجهة دردشة تعمل عبر المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server تشغّل GLM 4.7 عبر عقدتين](assets/llama-server-example.png)

<!-- @os:linux -->
> **العثور على `<HOST_IP>`**: على الجهاز 1، شغّل `hostname -I | awk '{print $1}'` للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **العثور على `<HOST_IP>`**: على الجهاز 1، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) للعثور على عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00005`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | يفعّل rocWMMA Flash Attention لتحسين الأداء على وحدات معالجة الرسومات (GPU) الخاصة بـ AMD |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسومات (GPU) |
| `-lm none` | يضبط وضع تحميل النموذج على `none`، مما يعطّل التخطيط الذاكري (memory-mapping) لتقليل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام (RAM) لكنه يتسع في ذاكرة الفيديو (VRAM) |
| `--host` | عنوان IP لربط `llama-server` به (`llama-server` فقط) |
| `--port` | المنفذ الذي يتم من خلاله تقديم واجهة برمجة تطبيقات HTTP (`llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل من نقاط نهاية عاملي RPC (بصيغة `IP:port`) |

للحصول على شرح كامل لاستخدام المعاملات، راجع [وثائق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[وثائق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: يكشف `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API وهمي (مثل `none`) للاتصال بمجموعتك (cluster)
- **استكشاف نماذج أخرى**: تصفّح ملفات GGUF المكمّمة على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تتناسب مع ذاكرة وحدة معالجة الرسومات (GPU) المجمعة لمجموعتك
- **التوسع إلى أربع عقد**: أضف نظامي Ryzen AI Halo إضافيين كعاملي RPC إضافيين للوصول إلى نماذج بحجم تريليون معامل. مرّر نقاط نهاية إضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)