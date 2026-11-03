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

# التطوير عن بُعد باستخدام AMD Sync

## نظرة عامة

يحوّل **AMD Sync** جهازك المحمول إلى قمرة قيادة عن بُعد لجهاز AMD Ryzen™ AI Halo. تخطَّ الإعداد اليدوي لـ SSH والمفاتيح وبيئة التطوير — قم بتثبيت AMD Sync واحصل على وصول بنقرة واحدة إلى طرفية عن بُعد، وVS Code، وJupyterLab، ولوحة معلومات مباشرة لـ GPU/CPU/الذاكرة على جهاز Ryzen AI Halo.

يبقى جهازك المحلي مألوفًا؛ إذ يتم تنفيذ كل أمر ودفتر ملاحظات ونموذج على جهاز Ryzen AI Halo.

> **تلميح**: ستحتوي هذه الصفحة على أي تحديثات جديدة لـ AMDSync.

## ما الذي ستتعلمه

- تفعيل SSH على جهاز Ryzen AI Halo والاتصال به من AMD Sync
- تشغيل VS Code والطرفية وJupyterLab ومقاييس الأداء المباشرة على جهاز Ryzen AI Halo بنقرة واحدة
- تنظيم العمل عن بُعد باستخدام مجلدات المشاريع المُدارة في AMD Sync

---

## المفاهيم الأساسية

يتكون AMD Sync من جانبين: **عميل** (جهازك المحمول، الذي يشغّل تطبيق AMD Sync) و**خادم** (جهاز Ryzen AI Halo، الذي يشغّل خادم SSH يقوم AMD Sync بإنشاء نفق إليه). كل ما تطلقه من AMD Sync — VS Code، أو طرفية، أو دفتر ملاحظات — يُفتح محليًا لكنه يُنفَّذ على جهاز Ryzen AI Halo.

> **العملاء المدعومون:** Windows 11 وLinux. لا يتم دعم macOS.

---

## الخطوة 1 — تفعيل SSH على جهاز Ryzen AI Halo


> **ملاحظة:** على Windows، يأتي جهاز Ryzen AI Halo مع خادم SSH *مُعطّلًا افتراضيًا*. أما على Linux، فيأتي مع خادم SSH *مُفعّلًا افتراضيًا*.

1. على جهاز Ryzen AI Halo، افتح **مركز مطوري AMD Ryzen™ AI**.
2. انتقل إلى علامة التبويب **Remote**.
3. قم بتفعيل **SSH Server**.
4. لاحظ **عنوان IP**، و**المنفذ (Port)**، و**اسم المستخدم (Username)** الظاهرة تحت **Server Information** — ستقوم بلصقها في AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **ملاحظة:** هذا هو مركز مطوري AMD لنظام Windows. قد يختلف الواجهة الخاصة بـ Linux، لكنها توفر وظائف عن بُعد مشابهة.

> **تلميح:** يطلب AMD Sync **كلمة مرور تسجيل الدخول لنظام التشغيل** لذلك المستخدم، وليست كلمة مرور من مركز المطورين.

---

## الخطوة 2 — تثبيت AMD Sync على جهاز العميل

يعمل AMD Sync على Windows 11 وLinux. قم بتنزيل برنامج التثبيت الخاص بنظام التشغيل لديك، ثم اتبع الخطوات أدناه. بعد التثبيت، انقر على **Accept & Install** في شاشة **Get Started** — سيتم تشغيل AMD Sync تلقائيًا عند الانتهاء.

### Windows

[تنزيل AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. انقر نقرًا مزدوجًا على `AMDSyncInstaller.exe`.
2. انقر على **Accept & Install**.

> إذا طلب منك جدار حماية Windows الإذن، اسمح لـ AMD Sync بالوصول إلى الشبكة حتى يتمكن من الوصول إلى جهاز Ryzen AI Halo عبر SSH.

### Linux

انقر على الرابط لتنزيل التنسيق المفضل لديك:

| التنسيق | التنزيل | أمر التثبيت |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **ملاحظة:** قد يُصنِّف مركز تطبيقات Ubuntu ملف `.deb` المفتوح محليًا على أنه *"قد يكون غير آمن"*. هذا هو التحذير القياسي لأي برنامج تثبيت محلي من طرف ثالث. إذا فشل النقر المزدوج على ملف `.deb`، استخدم أمر الطرفية أعلاه.

---

## الخطوة 3 — الاتصال بجهاز Ryzen AI Halo الخاص بك

عند التشغيل لأول مرة، يعرض AMD Sync نموذج **Add a Remote Device**. قم بملئه باستخدام القيم من علامة التبويب **Remote** في مركز المطورين.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| الحقل | ملاحظات |
|-------|-------|
| **اسم الجهاز (Device Name)** *(اختياري)* | تسمية سهلة مثل `Ryzen AI Halo`. القيمة الافتراضية هي `Device 1`، `Device 2`، … |
| **Hostname or IP** | من علامة التبويب Remote |
| **SSH Port** | من علامة التبويب Remote (أرقام فقط) |
| **Username** | اسم حسابك على نظام التشغيل الخاص بجهاز Ryzen AI Halo |
| **Password** | كلمة مرور تسجيل الدخول لنظام التشغيل الخاص بك — تظهر مموّهة أثناء الكتابة |

انقر على **Add Device**. بعد شاشة تحميل قصيرة، سترى **"Connection Successful"** وتصل إلى العرض الرئيسي، الذي يظهر في علبة نظام التشغيل (system tray). انقر خارج النافذة لإخفائها؛ سيستمر AMD Sync في العمل ويكون على بُعد نقرة واحدة.

> **إذا فشل الاتصال،** يعود AMD Sync إلى النموذج مع الاحتفاظ بالقيم التي أدخلتها. الأسباب الشائعة هي تعطيل SSH على جهاز Ryzen AI Halo، أو كلمة مرور خاطئة، أو وجود الجهازين على شبكتين مختلفتين.

---

## الخطوة 4 — تشغيل أول أداة عن بُعد

يوفر لك العرض الرئيسي خمسة مكونات بنقرة واحدة — وكلها متاحة بغض النظر عن نظام التشغيل الذي يعمل عليه العميل وجهاز Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| المكوّن | ما الذي يقوم به |
|-----------|--------------|
| **Directory** | يختار المجلد الموجود على جهاز Ryzen AI Halo الذي سيُفتح فيه VS Code والطرفية وJupyterLab. القيمة الافتراضية هي مساحة عمل مُدارة باسم `Documents/AMD_Sync`. |
| **VS Code** | يفتح VS Code محليًا مع نفق SSH إلى المجلد المحدد. |
| **Terminal** | يفتح طرفية محلية متصلة عبر SSH بجهاز Ryzen AI Halo، في المجلد المحدد. |
| **JupyterLab** | يُطلق مشروع دفتر ملاحظات متصل عبر SSH بجهاز Ryzen AI Halo، محصورًا في المجلد المحدد. |
| **Live Metrics** | عرض في الوقت الفعلي لاستخدام GPU والذاكرة وCPU على جهاز Ryzen AI Halo. |

### جرّب VS Code

لأول تشغيل، جرّب **VS Code**.

1. اترك **Directory** على القيمة الافتراضية `~/Documents/AMD_Sync`.
2. انقر على **VS Code**.
3. يُنشئ AMD Sync المجلد `Documents/AMD_Sync/Project_1` على جهاز Ryzen AI Halo ويفتح VS Code محليًا، متصلًا به عبر نفق.

أنت الآن تقوم بتحرير ملفات موجودة على جهاز Ryzen AI Halo باستخدام إعداد VS Code المحلي لديك. أنشئ ملف `helloworld.py`، وأضف `print("hello world")`، وافتح الطرفية المدمجة (`` Ctrl + ` ``)، وشغّله:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

يعرض شريط الحالة **SSH: Linux** — دليل على أن الكود الخاص بك يعمل على جهاز Ryzen AI Halo، وليس على جهازك المحمول.
### جرّب الطرفية (Terminal)

انقر على **Terminal** للدخول إلى المجلد نفسه عبر SSH دون ترك لوحة المفاتيح.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

على نظام Windows، الطرفية الافتراضية هي **PowerShell** — يمكنك التبديل إلى **Windows Command Prompt** من قائمة الإعدادات إذا كنت تفضل ذلك. أما على نظام Linux، فتستخدم AMD Sync الطرفية الافتراضية لنظامك.

---

## كيف يعمل الدليل (Directory)

القائمة المنسدلة **Directory** هي أهم عنصر تحكم في AMD Sync — فهي تحدد أين تنتهي كل أداة تطلقها على Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (الافتراضي)** — يؤدي تشغيل VS Code أو JupyterLab من هنا إلى إنشاء مجلد مشروع جديد تلقائيًا (`Project_1`، `Project_2`، … لـ VS Code؛ و`Notebook_Project_1`، `Notebook_Project_2`، … لـ JupyterLab).
- **مجلدات المشاريع الموجودة** — يظهر أي مجلد فرعي مباشر لـ `AMD_Sync` (بما في ذلك المجلدات التي تنشئها يدويًا على Ryzen AI Halo) في القائمة المنسدلة. يصبح آخر مجلد استخدمته هو الافتراضي في المرة القادمة.
- **المسارات المخصصة** — اكتب أي مسار مطلق لفتح مجلد في مكان آخر على Ryzen AI Halo. تقوم AMD Sync فقط *بفتح* المجلد — ولن تُنشئ مجلدات خارج `AMD_Sync`، كما أن المسارات المخصصة لا تُحفظ بين الجلسات.

إذا لم يعمل مسار مخصص، تخبرك AMD Sync بالسبب: صياغة غير صالحة، أو المجلد غير موجود، أو المسار يشير إلى ملف.

---

## المقاييس الحية (Live Metrics) وJupyterLab

- **Live Metrics** — لوحة معلومات حية لاستخدام GPU والذاكرة وCPU. إنها أسرع طريقة للتأكد من أن عملية تدريب عن بُعد تعمل فعليًا على الجهاز.
- **JupyterLab** — مشروع دفتر ملاحظات كامل متصل عبر SSH بـ Ryzen AI Halo، مع طرفية مدمجة خاصة به لمزج خلايا الدفتر مع أوامر الصدفة دون مغادرة الواجهة.

---

## الإعدادات (Settings) والأجهزة المتعددة

تحتوي قائمة **Settings** على ثلاث علامات تبويب:

| علامة التبويب | ما تغطيه |
|-----|----------------|
| **Devices** | تسرد كل جهاز Ryzen AI Halo اتصلت به بنجاح. أعد الاتصال، أو عدّل بيانات الاعتماد، أو أضف جهازًا جديدًا. |
| **Information** | روابط إلى الوثائق ودعم المنتدى. |
| **Customize** | أعد وضع التطبيق على سطح المكتب، وبدّل نوع الطرفية (على Windows فقط)، وتحقّق من تحديثات AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **نوع الطرفية (Windows)** — اختر بين **PowerShell** (الافتراضي) و**Windows Command Prompt**.
- **نوع الطرفية (Linux)** — تتوفر فقط الطرفية الافتراضية للنظام.
- **تحديثات التطبيق** — علامة التبويب هذه هي المكان المناسب للتحقق من إصدارات AMD Sync الجديدة وتثبيتها من داخل الواجهة؛ فلا حاجة إلى أداة تحديث منفصلة.

> لا يظهر الجهاز ضمن **Devices** إلا بعد نجاح أول اتصال به، لذا لن تؤدي المحاولات الفاشلة إلى ازدحام القائمة.

---

## استكشاف الأخطاء وإصلاحها

- **فشل الاتصال فورًا** — تأكد من تفعيل خادم SSH على علامة تبويب **Remote** في Developer Center على Ryzen AI Halo.
- **خطأ كلمة مرور خاطئة** — استخدم **كلمة مرور تسجيل الدخول لنظام التشغيل** على Ryzen AI Halo، وليس كلمات المرور المأخوذة من Developer Center.
- **زر VS Code لا يفعل شيئًا** — ثبّت VS Code على جهاز العميل الخاص بك من [code.visualstudio.com](https://code.visualstudio.com).
- **أيقونة AMD Sync في شريط النظام مفقودة (Linux/GNOME)** — ثبّت وفعّل امتداد AppIndicator.
- **ملف `.deb` لا يُفتح من مدير الملفات** — استخدم الأمر `sudo apt install ./AMDSyncInstaller.deb` من طرفية.
- **يظهر الإعداد مجددًا في كل مرة تشغيل (Linux)**: افتح قفل سلسلة مفاتيح تسجيل الدخول (login keyring)، أو شغّل باستخدام `--password-store=gnome-libsecret`، ثم أعد الإعداد مرة واحدة.

---