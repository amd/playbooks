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

# تجميع أربعة أنظمة Ryzen™ AI Halo عبر RPC

## نظرة عامة

نظام Ryzen™ AI Halo الخاص بك قادر بالفعل على تشغيل نماذج اللغة الكبيرة محليًا. يأخذ التجميع (Clustering) هذه القدرة إلى مستوى أبعد من خلال دمج ذاكرة GPU الخاصة بعدة أنظمة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر بقدرات استدلال أقوى، وتوليد أكواد أفضل، وفهم لغوي متعدد أعمق، كل ذلك بالكامل على أجهزتك الخاصة.

يعلّمك هذا الدليل كيفية تجميع أربعة أنظمة Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp وتشغيل Kimi K2.6، وهو نموذج مزيج خبراء (mixture-of-experts) كبير، عبر الأنظمة الأربعة جميعها بتسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm وRPC
- تهيئة عمّال RPC (RPC workers) وتشغيل الاستدلال الموزّع عبر أربع عقد
- تشغيل نموذج بمليار تريليون (1T) معلمة عبر أربعة أنظمة Ryzen AI Halo مرتبطة عبر الشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على الأجهزة الأربعة كافةً (الجهاز 1 حتى الجهاز 4).

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (ذاكرة VRAM الخاصة بـ iGPU).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 GB**. يرجى إعادة تشغيل النظام لتفعيل التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، يستخدم ROCm مجمع ذاكرة نظام مشترك، وهذا المجمع مهيأ افتراضيًا ليكون نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحة مدير جدول الترجمة (Translation Table Manager - TTM) الخاص بالنواة (kernel)، وذلك باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 GB).

* ثبّت أداة pipx وأضف مسار العجلات (wheels) المثبّتة بواسطة pipx إلى مسار بحث النظام.

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

يتطلب هذا الدليل أربع وحدات Ryzen AI Halo ومحول إيثرنت واحد، متصلة في طوبولوجيا نجمية بحيث تكون كل وحدة موصولة مباشرة بالمحول.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | عقد الحوسبة التي تشكّل المجموعة (cluster) |
| محول إيثرنت بسرعة 10 جيجابت | 1 | محول مركزي للسماح باتصال متعدد العقد بين وحدات Ryzen AI Halo (4 منافذ على الأقل) |
| كابل إيثرنت | 4 | يربط كل وحدة Halo بالمحول (يُفضّل استخدام كابل من فئة Cat 7 أو أعلى) |

> **ملاحظة**: يلزم توفير أربعة منافذ في محول الإيثرنت لتوصيل وحدات Ryzen AI Halo الأربع. يلزم منفذ خامس إذا كنت تصل إلى النموذج من جهاز عميل منفصل بدلًا من أحد وحدات Halo.

### البرامج
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

## إعداد الأجهزة الفعلي

> **ملاحظة**: أكمل هذه الخطوة على الأجهزة الأربعة كافةً (الجهاز 1 حتى الجهاز 4).

وصّل كل وحدة Ryzen AI Halo بمحول الإيثرنت باستخدام كابل من فئة Cat 7 (أو أعلى). يؤدي ذلك إلى إنشاء رابط بسرعة 10 جيجابت يُستخدم للاتصال عالي السرعة بين العقد.
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

يجب أن تظهر لك سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يظهر الرابط، تحقق من توصيل الكابل وتأكد من ضبط منفذ المحول على 10 جيجابت. تتطلب بعض المحولات تعطيل التفاوض التلقائي (auto-negotiation) وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

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

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يظهر الرابط، تحقق من توصيل الكابل وتأكد من ضبط منفذ المحول على 10 جيجابت. تتطلب بعض المحولات تعطيل التفاوض التلقائي (auto-negotiation) وضبط سرعة الرابط يدويًا؛ راجع وثائق المحول الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على الأجهزة الأربعة كافةً (الجهاز 1 حتى الجهاز 4).

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات (binaries) جاهزة مسبقًا، أسرع إعداد
- [الخيار 2: بناء يدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في خيارات البناء

### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK إصدارات ليلية (nightly builds) من llama.cpp مع تسريع AMD ROCm 7، تستهدف وحدات معالجة رسومية (GPUs) مثل gfx1151 (‏Strix Halo / Ryzen AI Max+ 395) وبنيات Radeon الأحدث الأخرى.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية المُجهّزة مسبقًا

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك والوحدة الرسومية المستهدفة:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية

فك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مبنية بدعم ROCm من `llama-cli.exe` و`llama-server.exe` و`ggml-rpc-server.exe`، تم تجميعها مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف الوحدة الرسومية

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
#### الخطوة 1: تنزيل الملفات الثنائية المُجهّزة مسبقًا

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك والوحدة الرسومية المستهدفة:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث `xxxx` هو رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية وتجهيزها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مبنية بدعم ROCm من `llama-cli` و`llama-server` و`rpc-server`، تم تجميعها مسبقًا لنظام Ryzen AI Halo الخاص بك.

#### الخطوة 3: التحقق من اكتشاف الوحدة الرسومية

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

أضف HIP إلى مسارك (path) وابنِ المشروع بدعم ROCm وRPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | تفعيل حزمة برمجيات ROCm/HIP |
| `-DGGML_RPC=ON` | تفعيل RPC للاستدلال الموزّع |
| `-DGPU_TARGETS=gfx1151` | استهداف وحدة معالجة رسومية Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | استخدام نظام بناء Ninja |

#### الخطوة 2: التحقق من اكتشاف الوحدة الرسومية

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

#### الخطوة 3: إضافة HIP إلى مسار المستخدم

قامت خطوة البناء أعلاه بتعيين `%HIP_PATH%\bin` لهذه الجلسة فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في x64 Native Tools Command Prompt)، أضفها بشكل دائم إلى متغير `PATH` الخاص بالمستخدم:

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

ابنِ المشروع بدعم ROCm وRPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| علامة البناء | الغرض |
|-----------|---------|
| `-DGGML_HIP=ON` | تفعيل حزمة برمجيات ROCm |
| `-DGGML_RPC=ON` | تفعيل RPC للاستدلال الموزّع |
| `-DAMDGPU_TARGETS="gfx1151"` | استهداف وحدة معالجة رسومية Ryzen AI Halo (Radeon 8060s) |

للمزيد من خيارات البناء، راجع [توثيق بناء llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### الخطوة 2: التحقق من اكتشاف الوحدة الرسومية

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

يستخدم هذا الدليل [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) بنمط الترميز الكمي (quantization) `UD-Q2_K_XL` من [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). يتناسب هذا الترميز الكمي مع إجمالي ذاكرة الوحدة الرسومية المجمّعة لأربع عقد Ryzen AI Halo.

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

> **ملاحظة**: يجب إكمال تنزيل النموذج على الجهاز رقم 1 (وحدة التحكم). لا تحتاج عقد عمّال RPC (الأجهزة رقم 2 و3 و4) إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يتيح محرك RPC (استدعاء الإجراء عن بُعد) الخاص بـ llama.cpp لمثيل واحد من llama.cpp تفريغ طبقات النموذج إلى عمّال بعيدين عبر الشبكة. يعمل جهاز واحد بمثابة **وحدة التحكم** (الجهاز رقم 1)، حيث يتولى مهام الترميز اللفظي (tokenization) والجدولة والتنسيق. بينما يشغّل كل من الأجهزة الثلاثة الأخرى **خادم RPC** خفيف الوزن (الأجهزة رقم 2 و3 و4) يعرض ذاكرة وحدته الرسومية وقدرته الحسابية لوحدة التحكم.

عند وقت التحميل، يقوم llama.cpp بتقسيم النموذج عبر جميع العقد الأربع. وبمجرد التحميل، يسير الاستدلال كما لو كان يعمل على مسرّع واحد. يتولى RPC عمليات نقل الموترات (tensors) والمزامنة خلف الكواليس.

### الخطوة 1: بدء تشغيل خوادم RPC (الأجهزة رقم 2 و3 و4)

على كل من الأجهزة رقم 2 و3 و4، ابدأ تشغيل خادم RPC لعرض موارد وحدته الرسومية لوحدة التحكم:
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
| `-c` | تفعيل ذاكرة تخزين مؤقت محلية للموترات الكبيرة، لتجنّب عمليات النقل الشبكي المتكررة أثناء تحميل النموذج |
| `--host` | عنوان IP لربط خادم RPC به (`0.0.0.0` لجميع الواجهات) |

للمزيد من الخيارات، راجع [توثيق RPC الخاص بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز رقم 1)

مع تشغيل خوادم RPC على الأجهزة رقم 2 و3 و4، ابدأ الاستدلال من الجهاز رقم 1 باستخدام إما `llama-cli` أو `llama-server`.
#### llama-cli

توفر أداة `llama-cli` واجهة تعتمد على الطرفية (terminal) للتفاعل المباشر مع النموذج. وهي مثالية لأغراض قياس الأداء والتصحيح والتجريب على المستوى المنخفض.

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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: في كل من الجهاز 2 والجهاز 3 والجهاز 4، نفّذ الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: في كل من الجهاز 2 والجهاز 3 والجهاز 4، نفّذ الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، تعرض `llama-cli` تقدّم تحميل النموذج وتدخل في موجّه تفاعلي يمكنك من خلاله الدردشة مباشرة مع النموذج:

![llama-cli يشغّل Kimi K2.6 عبر أربع عقد](assets/llama-cli-example.png)

#### llama-server

تعرض `llama-server` نفس محرك الاستدلال عبر عملية خادم دائمة مزوّدة بواجهة مستخدم ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. وهذه هي الواجهة المفضّلة للنشر على المدى الطويل، والوصول من عدة مستخدمين، والتكامل مع الأدوات الخارجية.

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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: في كل من الجهاز 2 والجهاز 3 والجهاز 4، نفّذ الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
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

> **إيجاد `<RPC_WORKER_2_IP>`، `<RPC_WORKER_3_IP>`، `<RPC_WORKER_4_IP>`**: في كل من الجهاز 2 والجهاز 3 والجهاز 4، نفّذ الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد بدء التشغيل، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة الويب المدمجة. توفّر هذه الواجهة تجربة دردشة قائمة على المتصفح للتفاعل مع النموذج:

![واجهة ويب llama-server تشغّل Kimi K2.6 عبر أربع عقد](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، نفّذ الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، نفّذ الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الجزء الأول، `00001-of-00008`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستهلك ذاكرة أكثر |
| `-fa on` | يفعّل rocWMMA Flash Attention لتحسين الأداء على وحدات معالجة الرسومات (GPU) من AMD |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسومات (GPU) |
| `-lm none` | يضبط وضع تحميل النموذج على `none`، مما يعطّل التخطيط الذاكري (memory-mapping) لتقليل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة النظام (RAM) المتاحة لكنه يتّسع ضمن ذاكرة الفيديو (VRAM) |
| `-b` | حجم الدفعة المنطقية (logical batch size) بالرموز. ضبط القيمة على 4096 يوازن بين الإنتاجية واستهلاك الذاكرة عبر العقد |
| `-ub` | حجم الدفعة الفعلية (الدقيقة) لمعالجة المُوجّه (prompt). مطابقة هذه القيمة مع `-b` تتجنب النفقات غير الضرورية للتجزئة |
| `--host` | عنوان IP الذي تُربط به `llama-server` (خاص بـ `llama-server` فقط) |
| `--port` | المنفذ الذي يتم عليه تقديم واجهة برمجة التطبيقات HTTP (خاص بـ `llama-server` فقط) |
| `--rpc` | قائمة مفصولة بفواصل لنقاط نهاية عمال RPC (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، راجع [توثيق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[توثيق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: تعرض `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API نائب (مثل `none`) للاتصال بمجموعتك (cluster)
- **استكشاف نماذج أخرى**: تصفّح ملفات GGUF المكمَّمة (quantized) على [Hugging Face](https://huggingface.co/models?search=gguf) للعثور على نماذج تتناسب مع ذاكرة GPU الإجمالية لمجموعتك
- **التوسّع إلى ما بعد أربع عقد**: أضف أنظمة Ryzen AI Halo إضافية كعمال RPC إضافيين للوصول إلى نماذج تتجاوز مقياس التريليون معامل (1 trillion parameter). مرّر نقاط نهاية إضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)