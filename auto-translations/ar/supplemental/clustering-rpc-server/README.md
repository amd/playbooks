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

# تجميع نظامَي Ryzen™ AI Halo باستخدام RPC

## نظرة عامة

يتمتع نظام Ryzen™ AI Halo لديك بالفعل بالقدرة على تشغيل نماذج اللغة الكبيرة محليًا. يأخذ التجميع (Clustering) هذه القدرة إلى مستوى أبعد من خلال دمج ذاكرة GPU لعدة أنظمة عبر شبكة محلية، مما يمنحك إمكانية الوصول إلى نماذج أكبر بكثير مع قدرات استدلال أقوى، وتوليد أكواد برمجية أفضل، وفهم متعدد اللغات أعمق، وكل ذلك بالكامل على أجهزتك الخاصة.

يعلّمك هذا الدليل كيفية تجميع نظامَي Ryzen AI Halo باستخدام محرك RPC الخاص بـ llama.cpp، وتشغيل نموذج GLM 4.7، وهو نموذج بمعامل 358 مليار، عبر الجهازين باستخدام تسريع AMD ROCm™.

## ما ستتعلمه

- كيفية توسيع تخصيص VRAM على أنظمة Ryzen AI Halo
- تثبيت llama.cpp مع دعم ROCm و RPC
- تكوين عامل RPC (RPC worker) وتشغيل الاستدلال الموزع عبر عقدتين
- تشغيل نموذج بمعامل 358 مليار عبر نظامَي Ryzen AI Halo متصلين بشبكة

## ضبط إعدادات الذاكرة

> **ملاحظة**: أكمل هذه الخطوة على كلٍّ من الجهاز 1 والجهاز 2.

<!-- @os:windows -->
على نظام Windows، لتشغيل نماذج أكبر تتطلب ذاكرة أعلى، نحتاج إلى استخدام تخصيص AMD Variable Graphics Memory (ذاكرة VRAM لـ iGPU).

يمكن القيام بذلك عن طريق فتح لوحة تحكم AMD Software: Adrenalin Edition والانتقال إلى: `Performance > Tuning > AMD Variable Graphics Memory`. اضبط القيمة على **96 GB**. يُرجى إعادة تشغيل النظام لتفعيل التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
على نظام Linux، يستخدم ROCm مجمعًا مشتركًا من ذاكرة النظام، ويكون هذا المجمع مُكوَّنًا افتراضيًا على نصف ذاكرة النظام.

يمكن زيادة هذه الكمية عن طريق تغيير إعداد صفحات مدير جدول الترجمة (Translation Table Manager - TTM) الخاص بالنواة (kernel)، باتباع التعليمات التالية. توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 GB).

* ثبّت أداة pipx وأضف مسار الحزم المثبتة بواسطة pipx إلى مسار بحث النظام.

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

* أعد تكوين إعدادات الذاكرة المشتركة إلى **120 GB**:
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

يتطلب هذا الدليل وحدتَي Ryzen AI Halo ومحوّل شبكة إيثرنت واحد، متصلَين في طوبولوجيا نجمية بحيث تكون كل وحدة موصولة مباشرة بالمحوّل.

| المكوّن | الكمية | الوصف |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | عقد الحوسبة التي تشكّل المجموعة |
| محوّل شبكة إيثرنت بسرعة 10 جيجابت | 1 | محوّل مركزي للسماح باتصال متعدد العقد بين وحدات Ryzen AI Halo (منفذان على الأقل) |
| كابل إيثرنت | 2 | يربط كل وحدة Halo بالمحوّل (يُفضّل Cat 7 أو أعلى) |

> **ملاحظة**: يلزم منفذان على محوّل الشبكة لربط وحدتَي Ryzen AI Halo. يلزم منفذ ثالث إذا كنت ستصل إلى النموذج من جهاز عميل منفصل بدلاً من الوصول من إحدى وحدتَي Halo.

### البرامج
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

## إعداد الأجهزة الفعلية

> **ملاحظة**: أكمل هذه الخطوة على كلٍّ من الجهاز 1 والجهاز 2.

صِل كل وحدة من وحدات Ryzen AI Halo بمحوّل شبكة إيثرنت باستخدام كابل Cat 7 (أو أعلى). يُنشئ هذا رابط 10 جيجابت المستخدم للاتصال عالي السرعة بين العقد.
<!-- @os:linux -->
### 1. تحديد واجهات الشبكة

على كل جهاز، ابحث عن اسم واجهة الشبكة الخاصة به ودوّنه (سيُشار إليه أدناه باسم `IFNAME`). شغّل:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

هذا يطبع اسم الواجهة مباشرةً، على سبيل المثال:

```bash
enp191s0
```

### 2. التحقق من سرعات روابط الشبكة

تأكد من أن الرابط نشط ويعمل بأقصى سرعة عن طريق التحقق من سرعة واجهتك:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **ملاحظة**: استبدل `<IFNAME>` باسم واجهة الإخراج من [1. تحديد واجهات الشبكة](#1-determine-network-interfaces)

يجب أن تشاهد سرعة `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **ملاحظة**: إذا كانت السرعة أقل من `10000Mb/s` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحوّل مضبوط على 10 جيجابت. تتطلب بعض المحوّلات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحوّل الخاص بك.

<!-- @os:end -->

<!-- @os:windows -->
### التحقق من سرعة رابط الشبكة

على كل جهاز، تحقق من سرعة رابط واجهات الشبكة الخاصة بك:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

يجب أن تكون واجهة الإيثرنت الخاصة بك في حالة `Up` وتعمل بسرعة `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **ملاحظة**: إذا كانت السرعة أقل من `10 Gbps` أو لم يعمل الرابط، تحقق من توصيل الكابل وتأكد من أن منفذ المحوّل مضبوط على 10 جيجابت. تتطلب بعض المحوّلات تعطيل التفاوض التلقائي وضبط سرعة الرابط يدويًا؛ راجع وثائق المحوّل الخاص بك.

<!-- @os:end -->

## تثبيت llama.cpp

> **ملاحظة**: أكمل هذه الخطوة على كلٍّ من الجهاز 1 والجهاز 2.

يتوفر خياران للتثبيت:

- [الخيار 1: Lemonade SDK (موصى به)](#option-1-lemonade-sdk-recommended) - ثنائيات جاهزة مسبقًا، أسرع إعداد
- [الخيار 2: بناء يدوي من المصدر](#option-2-manual-source-build) - البناء من المصدر مع تحكم كامل في خيارات البناء

### الخيار 1: Lemonade SDK (موصى به)

يوفر Lemonade SDK إصدارات ليلية (nightly builds) من llama.cpp مع تسريع AMD ROCm 7، تستهدف وحدات GPU مثل gfx1151 (Strix Halo / Ryzen AI Max+ 395) وغيرها من معماريات Radeon الحديثة.

<!-- @os:windows -->
#### الخطوة 1: تنزيل الملفات الثنائية الجاهزة

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) الخاصة بك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (حيث تمثل `xxxx` رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية

قم بفك ضغط الأرشيف الذي تم تنزيله:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

يحتوي هذا الدليل الآن على إصدارات مبنية بدعم ROCm من `llama-cli.exe` و`llama-server.exe` و`rpc-server.exe`، مُجمَّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

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

انتقل إلى صفحة أحدث إصدار وقم بتنزيل الأرشيف المطابق لمنصتك وهدف وحدة معالجة الرسومات (GPU) الخاصة بك:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

قم بتنزيل الملف المسمى `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (حيث تمثل `xxxx` رقم البناء).

#### الخطوة 2: استخراج الملفات الثنائية وتجهيزها

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

يحتوي هذا الدليل الآن على إصدارات مبنية بدعم ROCm من `llama-cli` و`llama-server` و`rpc-server`، مُجمَّعة مسبقًا لنظام Ryzen AI Halo الخاص بك.

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

افتح **x64 Native Tools Command Prompt** (المثبت مع Visual Studio Build Tools) وقم باستنساخ المستودع:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

أضف HIP إلى المسار الخاص بك وقم بالبناء بدعم ROCm وRPC:

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

قامت خطوة البناء أعلاه بضبط `%HIP_PATH%\bin` لهذه الجلسة فقط. لجعل مكتبات HIP متاحة في أي طرفية (وليس فقط في x64 Native Tools Command Prompt)، أضفها بشكل دائم إلى `PATH` الخاص بمستخدمك:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

بعد تجهيز llama.cpp على كل عقدة، تابع إلى [تنزيل النموذج](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### الخطوة 1: بناء llama.cpp

قم باستنساخ المستودع:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

قم بالبناء بدعم ROCm وRPC:

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

يستخدم هذا الدليل [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)، وهو نموذج بحجم 358 مليار معلمة بتنسيق التكميم `Q4_K_XL` من [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). عند هذا التكميم، يتطلب النموذج ما يقارب 205 جيجابايت من مساحة التخزين، ويتناسب مع إجمالي ذاكرة وحدتي معالجة الرسومات لعقدتي Ryzen AI Halo مجتمعتين.

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

> **ملاحظة**: يجب إتمام عملية تنزيل النموذج على الجهاز 1 (المتحكم). عقد العمل الخاصة بـ RPC لا تحتاج إلى نسخة محلية من ملفات النموذج.

## تشغيل النموذج على العنقود (Cluster)

يتيح محرك RPC (استدعاء الإجراء عن بُعد) الخاص بـ llama.cpp لنسخة واحدة من llama.cpp تفريغ طبقات النموذج إلى عمال عن بُعد عبر الشبكة. يعمل جهاز واحد بصفته **المتحكم** (الجهاز 1)، حيث يتولى الترميز والجدولة والتنسيق. أما الجهاز الآخر فيُشغّل **خادم RPC** خفيف الوزن (الجهاز 2) يعرض ذاكرة وحدة معالجة الرسومات وقدرته الحسابية للمتحكم.

عند وقت التحميل، يقوم llama.cpp بتوزيع النموذج عبر كلا العقدتين. بمجرد التحميل، يسير الاستدلال كما لو كان يعمل على مسرّع واحد. يتولى RPC عمليات نقل المصفوفات (tensors) والمزامنة خلف الكواليس.

### الخطوة 1: تشغيل خادم RPC (الجهاز 2)

على الجهاز 2، قم بتشغيل خادم RPC لعرض موارد وحدة معالجة الرسومات الخاصة به للمتحكم:
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
| `-c` | يُفعّل ذاكرة تخزين مؤقت محلية للمصفوفات (tensors) الكبيرة، لتجنب عمليات النقل المتكررة عبر الشبكة أثناء تحميل النموذج |
| `--host` | عنوان IP لربط خادم RPC به (`0.0.0.0` لجميع الواجهات) |

لمزيد من الخيارات، راجع [وثائق RPC الخاصة بـ llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### الخطوة 2: تشغيل النموذج (الجهاز 1)

مع تشغيل خادم RPC على الجهاز 2، قم بتشغيل الاستدلال من الجهاز 1 باستخدام إما `llama-cli` أو `llama-server`.

#### llama-cli

توفر `llama-cli` واجهة قائمة على الطرفية للتفاعل المباشر مع النموذج. وهي مثالية لقياس الأداء وتصحيح الأخطاء والتجربة على مستوى منخفض.

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل الأمر `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: قم بتشغيل هذا الأمر في الطرفية (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل الأمر `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.

<!-- @os:end -->

بمجرد التشغيل، تعرض `llama-cli` تقدم تحميل النموذج وتدخل في محث تفاعلي حيث يمكنك الدردشة مباشرة مع النموذج:

![تشغيل llama-cli لنموذج GLM 4.7 عبر عقدتين](assets/llama-cli-example.png)
#### llama-server

يعرض `llama-server` نفس محرك الاستدلال عبر عملية خادم مستمرة مع واجهة مستخدم ويب متكاملة وواجهة برمجة تطبيقات HTTP متوافقة مع OpenAI. تُعد هذه الواجهة المفضلة للنشر طويل الأمد، والوصول متعدد المستخدمين، والتكامل مع الأدوات الخارجية.

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
> **ملاحظة**: شغّل هذا الأمر في الطرفية (Powershell).

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

> **إيجاد `<RPC_WORKER_IP>`**: على الجهاز 2، شغّل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

بمجرد التشغيل، افتح `http://<HOST_IP>:8081` في متصفحك للوصول إلى واجهة المستخدم الويب المدمجة. توفر هذه الواجهة واجهة دردشة تعمل عبر المتصفح للتفاعل مع النموذج:

![واجهة مستخدم ويب llama-server تعمل بنظام GLM 4.7 عبر عقدتين](assets/llama-server-example.png)

<!-- @os:linux -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `hostname -I | awk '{print $1}'` لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

<!-- @os:windows -->
> **إيجاد `<HOST_IP>`**: على الجهاز 1، شغّل `ipconfig | findstr /C:"IPv4"` في الطرفية (Powershell) لإيجاد عنوان IP المحلي الخاص به.
<!-- @os:end -->

#### مرجع المعاملات

| العلامة | الغرض |
|------|---------|
| `-m` | مسار ملف نموذج GGUF (استخدم الشظية الأولى، `00001-of-00005`) |
| `-c` | حجم السياق بالرموز (tokens). القيم الأكبر تستخدم ذاكرة أكثر |
| `-fa on` | يُفعّل rocWMMA Flash Attention لتحسين الأداء على وحدات معالجة الرسوميات AMD |
| `-ngl 999` | ينقل جميع طبقات النموذج إلى وحدة معالجة الرسوميات |
| `-lm none` | يضبط وضع تحميل النموذج على `none`، مما يعطّل التخطيط الذاكري (memory-mapping) لتقليل أوقات التحميل عندما يتجاوز حجم النموذج ذاكرة الوصول العشوائي للنظام لكنه يتناسب مع ذاكرة VRAM |
| `--host` | عنوان IP لربط `llama-server` به (`llama-server` فقط) |
| `--port` | المنفذ لتقديم واجهة برمجة تطبيقات HTTP عليه (`llama-server` فقط) |
| `--rpc` | قائمة نقاط نهاية عمال RPC مفصولة بفواصل (`IP:port`) |

للاطلاع على الاستخدام الكامل للمعاملات، راجع [توثيق llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) و[توثيق llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## الخطوات التالية

- **ربط تطبيقات الطرف الثالث**: يعرض `llama-server` واجهة برمجة تطبيقات متوافقة مع OpenAI. وجّه أي تطبيق متوافق مع OpenAI (مثل Open WebUI) إلى `http://<HOST_IP>:8081` مع أي مفتاح API عنصر نائب (مثل `none`) للاتصال بمجموعتك
- **استكشاف نماذج أخرى**: تصفّح ملفات GGUF المُكمّمة على [Hugging Face](https://huggingface.co/models?search=gguf) لإيجاد نماذج تتناسب مع إجمالي ذاكرة وحدة معالجة الرسوميات لمجموعتك
- **التوسع إلى أربع عقد**: أضف نظامي Ryzen AI Halo إضافيين كعمال RPC إضافيين للوصول إلى نماذج بحجم تريليون معامل. مرّر نقاط نهاية إضافية إلى `--rpc` كقائمة مفصولة بفواصل (مثل `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)