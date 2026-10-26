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

# تجميع اثنين من Ryzen™ AI Halo باستخدام RPC

## نظرة عامة

جهاز Ryzen™ AI Halo الخاص بك قادر بالفعل على تشغيل نماذج اللغة الكبيرة محليًا. يذهب التجميع (Clustering) بهذا إلى أبعد من ذلك من خلال الجمع بين ذاكرة GPU لأنظمة متعددة عبر شبكة محلية، مما يتيح لك الوصول إلى نماذج أكبر حجمًا ذات قدرة استدلال أقوى، وتوليد أكواد أفضل، وفهم متعدد اللغات أعمق، كل ذلك بالكامل على الأجهزة الخاصة بك.

يعلّمك هذا الدليل كيفية تجميع نظامين من Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp وتشغيل نموذج GLM 4.7، وهو نموذج بـ 358 مليار معامل، عبر كلا الجهازين باستخدام تسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm وRPC
- تهيئة عامل RPC وإطلاق الاستدلال الموزّع عبر عقدتين
- تشغيل نموذج بـ 358 مليار معامل عبر نظامين من Ryzen AI Halo متصلين عبر الشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **تشغيل النماذج القريبة من أو التي تتجاوز 128 جيجابايت:** على أنظمة AMD Ryzen™ AI Max 400 Series (Gorgon Halo) التي تعمل بنظام Windows، تتطلب النماذج التي تقترب من أو تتجاوز 128 جيجابايت من الذاكرة تهيئة إضافية للعمل دون أخطاء. اتبع [إرشادات نظام تشغيل Windows لسلسلة AMD Ryzen AI Max PRO 400](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) قبل تحميل النموذج.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (ذاكرة iGPU VRAM).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 جيجابايت**. يرجى إعادة تشغيل النظام ليتم تطبيق التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، يستخدم ROCm مجمع ذاكرة نظام مشترك، ويتم تهيئة هذا المجمع افتراضيًا على نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحات مدير جدول الترجمة (TTM) الخاص بالنواة، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 جيجابايت).

* قم بتثبيت أداة pipx وأضف المسار الخاص بالحزم المثبتة عبر pipx إلى مسار البحث في النظام.

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

* أعد تهيئة إعدادات الذاكرة المشتركة إلى **120 جيجابايت**:
  ```bash
  amd-ttm --set 120
  ```

* أعد تشغيل النظام ليتم تطبيق التغييرات.


<!-- @os:end -->
<!-- @device:halo_box -->
## تحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->
## المتطلبات الأساسية

### الأجهزة

يتطلب هذا الدليل وحدتين من Ryzen AI Halo ومحول شبكة إيثرنت واحد، متصلين في طوبولوجيا نجمية مع توصيل كل وحدة مباشرة بالمحول.

| المكون | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | عقد الحوسبة التي تشكّل المجموعة |
| محول إيثرنت بسرعة 10 جيجابت | 1 | محول مركزي للسماح بالاتصال متعدد العقد بين وحدات Ryzen AI Halo (منفذان على الأقل) |
| كابل إيثرنت | 2 | يصل كل وحدة Halo بالمحول (يُوصى باستخدام Cat 7 أو أعلى) |

> **ملاحظة**: يلزم وجود منفذين على محول الشبكة لتوصيل وحدتي Ryzen AI Halo. يلزم منفذ ثالث إذا كنت تصل إلى النموذج من جهاز عميل منفصل بدلاً من الوصول من إحدى وحدات Halo.

### البرامج
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
يرجى تثبيت:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) مع حزمة **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## إعداد الأجهزة الفعلي

> **ملاحظة**: أكمل هذه الخطوة على كل من الجهاز 1 والجهاز 2.

قم بتوصيل كل وحدة Ryzen AI Halo بمحول الشبكة باستخدام كابل Cat 7 (أو أعلى). يُنشئ هذا رابط 10 جيجابت المستخدم في الاتصال عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

على كل جهاز، ابحث عن اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه بـ `IFNAME`). قم بتشغيل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

يُطبع هذا اسم الواجهة مباشرة، على سبيل المثال:

```bash
enp191s0
```

### 2. التحقق من سرعات روابط الشبكة

تأكد من أن الرابط نشط ويعمل بالسرعة الكاملة من خلال فحص سرعة واجهتك:

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

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات مبنية مسبقًا، الإعداد الأسرع
- [الخيار 2: بناء يدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في خيارات البناء
### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK إصدارات ليلية من llama.cpp مع تسريع AMD ROCm 7، تستهدف وحدات معالجة رسومية مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وغيرها من معماريات Radeon الحديثة.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية المبنية مسبقًا

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات لديك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم الإصدار).

#### الخطوة 2: استخراج الملفات الثنائية

قم بفك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مُفعّلة بـ ROCm من `llama-cli.exe` و`llama-server.exe` و`rpc-server.exe`، مُجمّعة مسبقًا لنظام Ryzen AI Halo لديك.

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
#### الخطوة 1: تنزيل الملفات الثنائية المبنية مسبقًا

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات لديك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم الإصدار).

#### الخطوة 2: استخراج وتحضير الملفات الثنائية

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مُفعّلة بـ ROCm من `llama-cli` و`llama-server` و`rpc-server`، مُجمّعة مسبقًا لنظام Ryzen AI Halo لديك.

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
| `-DGGML_HIP=ON` | يُفعّل حزمة برمجيات ROCm/HIP |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزّع |
| `-DGPU_TARGETS=gfx1151` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (Radeon 8060s) |
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

قامت خطوة البناء أعلاه بتعيين `%HIP_PATH%\bin` للجلسة الحالية فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في x64 Native Tools Command Prompt)، أضفها بشكل دائم إلى `PATH` الخاص بمستخدمك:

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
| `-DGGML_HIP=ON` | يُفعّل حزمة برمجيات ROCm |
| `-DGGML_RPC=ON` | يُفعّل RPC للاستدلال الموزّع |
| `-DAMDGPU_TARGETS="gfx1151"` | يستهدف وحدة معالجة الرسومات Ryzen AI Halo (Radeon 8060s) |

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

يستخدم هذا الدليل [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)، وهو نموذج بـ358 مليار معامل بتنسيق التكميم `Q4_K_XL` من [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). عند هذا التكميم، يتطلب النموذج ما يقارب 205 جيجابايت من مساحة التخزين ويتناسب مع إجمالي ذاكرة وحدة معالجة الرسومات المشتركة لعقدتَي Ryzen AI Halo.

قم بتنزيل ملفات GGUF باستخدام Hugging Face CLI:
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

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز 1 (وحدة التحكم). لا تحتاج عقد العامل RPC إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يسمح محرك RPC (Remote Procedure Call) في llama.cpp لمثيل واحد من llama.cpp بتفريغ طبقات النموذج إلى عمال بعيدين عبر الشبكة. يعمل جهاز واحد بصفته **وحدة التحكم** (الجهاز 1)، حيث يتولى عمليات الترميز (tokenization) والجدولة والتنسيق. ويشغّل الجهاز الآخر **خادم RPC** خفيف الوزن (الجهاز 2) يعرض ذاكرة وحدة معالجة الرسومات والقدرة الحاسوبية الخاصة به لوحدة التحكم.

عند وقت التحميل، يقوم llama.cpp بتقسيم النموذج عبر العقدتين. وبمجرد التحميل، يسير الاستدلال كما لو كان يعمل على مُسرّع واحد. يتولى RPC عمليات نقل الموترات (tensors) والمزامنة في الخلفية.

### الخطوة 1: بدء تشغيل خادم RPC (الجهاز 2)

على الجهاز 2، ابدأ تشغيل خادم RPC لعرض موارد وحدة معالجة الرسومات الخاصة به لوحدة التحكم:
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
| `-c` | يُفعّل ذاكرة تخزين مؤقت محلية للموترات الكبيرة، مما يتجنب عمليات النقل الشبكي المتكررة أثناء تحميل النموذج |
| `--host` | عنوان IP الذي يُربط به خادم RPC (`0.0.0.0` لجميع الواجهات) |

لمزيد من الخيارات، راجع [وثائق RPC الخاصة بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خادم RPC على الجهاز 2، قم بتشغيل الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.
#### llama-cli

يوفر `llama-cli` واجهة طرفية (terminal-based) للتفاعل المباشر مع النموذج. وهو مثالي لقياس الأداء، وتصحيح الأخطاء، والتجريب على المستوى المنخفض.

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: شغّل هذا الأمر في Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) لإيجاد عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، يعرض `llama-cli` تقدم تحميل النموذج ويدخل في محث تفاعلي حيث يمكنك الدردشة مباشرةً مع النموذج:

![تشغيل llama-cli لنموذج GLM 4.7 عبر عقدتين](assets/llama-cli-example.png)

#### llama-server

يكشف `llama-server` نفس محرك الاستدلال من خلال عملية خادم دائمة مع واجهة ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. هذه هي الواجهة المفضلة لعمليات النشر طويلة الأمد، والوصول من مستخدمين متعددين، والتكامل مع الأدوات الخارجية.

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد البدء، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة الويب المدمجة. توفر هذه الواجهة واجهة دردشة قائمة على المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server أثناء تشغيل GLM 4.7 عبر عقدتين](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `ipconfig | findstr /C:"IPv4"` في Terminal (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00005`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | يفعّل rocWMMA Flash Attention لتحسين الأداء على وحدات معالجة الرسوميات (GPUs) من AMD |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسوميات (GPU) |
| `-lm none` | يضبط وضع تحميل النموذج على `none`، مما يعطل التخطيط الذاكري (memory-mapping) لتقليل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام RAM لكنه يناسب VRAM |
| `--host` | عنوان IP لربط `llama-server` به (`llama-server` فقط) |
| `--port` | المنفذ الذي يُقدَّم عليه واجهة برمجة التطبيقات HTTP (`llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل من نقاط نهاية عمال RPC (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، راجع [وثائق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[وثائق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: يكشف `llama-server` عن واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API وهمي (مثل، `none`) للاتصال بمجموعتك
- **استكشاف نماذج أخرى**: تصفح ملفات GGUF المُكمَّمة على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تناسب إجمالي ذاكرة GPU لمجموعتك
- **التوسع إلى أربع عقد**: أضف نظامين إضافيين من Ryzen AI Halo كعمال RPC إضافيين للوصول إلى نماذج بحجم تريليون معامل. مرر نقاط نهاية إضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل، `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)