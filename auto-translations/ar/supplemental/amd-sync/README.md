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

يحوّل **AMD Sync** جهازك المحمول إلى قمرة قيادة عن بُعد لجهاز AMD Ryzen™ AI Halo. تخطَّ الإعداد اليدوي لـ SSH والمفاتيح وبيئة التطوير — قم بتثبيت AMD Sync واحصل على وصول بنقرة واحدة إلى طرفية (terminal) عن بُعد، وVS Code، وJupyterLab، ولوحة معلومات حية لوحدة معالجة الرسومات/المعالج/الذاكرة على جهاز Ryzen AI Halo.

يبقى جهازك المحلي مألوفًا كما هو؛ بينما يتم تشغيل كل أمر ودفتر ملاحظات ونموذج على جهاز Ryzen AI Halo.

> **تلميح**: ستحتوي هذه الصفحة على أي تحديثات جديدة لـ AMDSync. 

## ما ستتعلمه

- تفعيل SSH على جهاز Ryzen AI Halo والاتصال به من خلال AMD Sync
- تشغيل VS Code، والطرفية، وJupyterLab، والمقاييس الحية (Live Metrics) على جهاز Ryzen AI Halo بنقرة واحدة
- تنظيم العمل عن بُعد باستخدام مجلدات المشاريع المُدارة في AMD Sync

---

## المفاهيم الأساسية

يتكوّن AMD Sync من طرفين: **عميل** (client) (جهازك المحمول، حيث يعمل تطبيق AMD Sync) و**خادم** (server) (جهاز Ryzen AI Halo، حيث يعمل خادم SSH الذي يتصل به AMD Sync عبر نفق). كل ما تقوم بتشغيله من AMD Sync — سواء كان VS Code، أو طرفية، أو دفتر ملاحظات — يُفتح محليًا لكنه يُنفَّذ على جهاز Ryzen AI Halo.

> **العملاء المدعومون:** Windows 11 وLinux. أنظمة macOS غير مدعومة.

---

## الخطوة 1 — تفعيل SSH على جهاز Ryzen AI Halo


> **ملاحظة:** على نظام Windows، يأتي جهاز Ryzen AI Halo مع خادم SSH *مُعطّلًا افتراضيًا*. أما على نظام Linux، فيأتي مع خادم SSH *مُفعّلًا افتراضيًا*.

1. على جهاز Ryzen AI Halo، افتح **AMD Ryzen™ AI Developer Center**.
2. انتقل إلى علامة التبويب **Remote**.
3. قم بتفعيل **SSH Server**.
4. لاحظ **IP Address** و**Port** و**Username** الظاهرة تحت **Server Information** — ستحتاج إلى لصقها في AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **ملاحظة:** هذا هو AMD Developer Center لنظام Windows. قد يختلف واجهة المستخدم في نظام Linux، لكن الوظائف عن بُعد مشابهة.

> **تلميح:** يطلب AMD Sync **كلمة مرور تسجيل الدخول لنظام التشغيل** لذلك المستخدم، وليست كلمة مرور من Developer Center.

---

## الخطوة 2 — تثبيت AMD Sync على جهاز العميل

يعمل AMD Sync على نظامي Windows 11 وLinux. قم بتنزيل برنامج التثبيت الخاص بنظام التشغيل لديك، ثم اتبع الخطوات أدناه. بعد التثبيت، انقر على **Accept & Install** في شاشة **Get Started** — يُشغَّل AMD Sync تلقائيًا عند الانتهاء.

### Windows

[تنزيل AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. انقر نقرًا مزدوجًا على `AMDSyncInstaller.exe`.
2. انقر على **Accept & Install**.

> إذا ظهرت لك رسالة من جدار حماية Windows، اسمح لـ AMD Sync بالوصول إلى الشبكة حتى يتمكن من الوصول إلى جهاز Ryzen AI Halo عبر SSH.

### Linux

انقر على الرابط لتنزيل الصيغة التي تفضلها:

| الصيغة | التنزيل | أمر التثبيت |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **ملاحظة:** قد يُصنّف مركز تطبيقات Ubuntu ملف `.deb` المفتوح محليًا على أنه *"غير آمن على الأرجح"*. هذا هو التحذير القياسي لأي برنامج تثبيت محلي من جهة خارجية. إذا فشل النقر المزدوج على ملف `.deb`، استخدم أمر الطرفية أعلاه.

---

## الخطوة 3 — الاتصال بجهاز Ryzen AI Halo الخاص بك

عند التشغيل الأول، يعرض AMD Sync نموذج **Add a Remote Device**. قم بتعبئته باستخدام القيم من علامة التبويب **Remote** في Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| الحقل | ملاحظات |
|-------|-------|
| **Device Name** *(اختياري)* | تسمية مألوفة مثل `Ryzen AI Halo`. القيمة الافتراضية هي `Device 1`، `Device 2`، … |
| **Hostname or IP** | من علامة التبويب Remote |
| **SSH Port** | من علامة التبويب Remote (أرقام فقط) |
| **Username** | اسم حساب نظام التشغيل الخاص بك على جهاز Ryzen AI Halo |
| **Password** | كلمة مرور تسجيل الدخول لنظام التشغيل الخاص بك — تظهر مُقنَّعة أثناء الكتابة |

انقر على **Add Device**. بعد شاشة تحميل قصيرة، ستشاهد **"Connection Successful"** وستنتقل إلى الشاشة الرئيسية، التي تقيم في شريط نظام التشغيل (system tray). انقر خارج النافذة لإغلاقها؛ يبقى AMD Sync يعمل وهو على بُعد نقرة واحدة منك.

> **في حال فشل الاتصال،** يعود AMD Sync إلى النموذج مع الاحتفاظ بالقيم التي أدخلتها. الأسباب الشائعة هي تعطيل SSH على جهاز Ryzen AI Halo، أو كلمة مرور خاطئة، أو وجود الجهازين على شبكات مختلفة.

---

## الخطوة 4 — تشغيل أول أداة عن بُعد

توفر لك الشاشة الرئيسية خمسة مكونات بنقرة واحدة — وكلها متاحة بغض النظر عن نظام التشغيل الذي يعمل عليه كل من العميل وجهاز Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| المكوّن | ماذا يفعل |
|-----------|--------------|
| **Directory** | يختار المجلد على جهاز Ryzen AI Halo الذي سيُفتح فيه كل من VS Code والطرفية وJupyterLab. القيمة الافتراضية هي مساحة عمل مُدارة باسم `Documents/AMD_Sync`. |
| **VS Code** | يفتح VS Code محليًا مع نفق SSH إلى المجلد المحدد. |
| **Terminal** | يفتح طرفية محلية متصلة عبر SSH بجهاز Ryzen AI Halo، في المجلد المحدد. |
| **JupyterLab** | يُطلق مشروع دفتر ملاحظات متصل عبر SSH بجهاز Ryzen AI Halo، مقتصرًا على المجلد المحدد. |
| **Live Metrics** | عرض لحظي لاستخدام وحدة معالجة الرسومات والذاكرة والمعالج على جهاز Ryzen AI Halo. |

### جرّب VS Code

للتشغيل الأول، جرّب **VS Code**. التعليمات التالية مخصصة لنظام Linux، لكن تجربة Windows مشابهة.

1. اترك **Directory** على القيمة الافتراضية `~/Documents/AMD_Sync`.
2. انقر على **VS Code**.
3. ينشئ AMD Sync المجلد `Documents/AMD_Sync/Project_1` على جهاز Ryzen AI Halo ويفتح VS Code محليًا، متصلًا به عبر نفق.

أنت الآن تقوم بتحرير ملفات موجودة على جهاز Ryzen AI Halo باستخدام إعداد VS Code المحلي الخاص بك. أنشئ الملف `helloworld.py`، وأضف السطر `print("hello world")`، وافتح الطرفية المدمجة (`` Ctrl + ` ``)، وقم بتشغيله:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

يُظهر شريط الحالة **SSH: Linux** — وهو دليل على أن الكود الخاص بك يعمل على جهاز Ryzen AI Halo، وليس على جهازك المحمول.
### جرّب الطرفية

انقر على **Terminal** للدخول مباشرة إلى المجلد نفسه عبر SSH دون مغادرة لوحة المفاتيح.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

في نظام Windows، الطرفية الافتراضية هي **PowerShell** — يمكنك التبديل إلى **Windows Command Prompt** من قائمة الإعدادات إذا كنت تفضل ذلك. في نظام Linux، يستخدم AMD Sync الطرفية الافتراضية لنظامك.

---

## كيف يعمل الدليل (Directory)

تُعدّ قائمة **Directory** المنسدلة أهم عنصر تحكم منفرد في AMD Sync — فهي التي تحدد أين تُفتح كل أداة تُطلقها على Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (الافتراضي)** — عند تشغيل VS Code أو JupyterLab من هنا، يتم إنشاء مجلد مشروع جديد تلقائيًا (`Project_1`، `Project_2`، … لـ VS Code؛ و`Notebook_Project_1`، `Notebook_Project_2`، … لـ JupyterLab).
- **مجلدات المشاريع الموجودة** — يظهر في القائمة المنسدلة أي مجلد فرعي مباشر ضمن `AMD_Sync` (بما في ذلك المجلدات التي تُنشئها يدويًا على Ryzen AI Halo). ويُصبح آخر مجلد استخدمته هو الافتراضي في المرة القادمة.
- **المسارات المخصصة** — اكتب أي مسار مطلق لفتح مجلد في مكان آخر على Ryzen AI Halo. يقوم AMD Sync بـ*فتحه* فقط — ولن يُنشئ مجلدات خارج `AMD_Sync`، كما أن المسارات المخصصة لا تُحفظ بين الجلسات.

إذا لم يعمل مسار مخصص، يُخبرك AMD Sync بالسبب: صيغة غير صالحة، أو المجلد غير موجود، أو المسار يشير إلى ملف.

---

## المقاييس الحيّة وJupyterLab

- **Live Metrics** — لوحة معلومات حيّة لاستخدام GPU والذاكرة وCPU. إنها أسرع طريقة للتأكد من أن عملية تدريب عن بُعد تعمل فعليًا على العتاد.
- **JupyterLab** — مشروع دفتر ملاحظات كامل متصل عبر SSH بـ Ryzen AI Halo، مع طرفية مدمجة خاصة به لمزج خلايا الدفتر وأوامر الصدفة دون مغادرة الواجهة.

---

## الإعدادات وأجهزة متعددة

تحتوي قائمة **Settings** على ثلاثة تبويبات:

| التبويب | ما يشمله |
|-----|----------------|
| **Devices** | يسرد كل جهاز Ryzen AI Halo اتصلت به بنجاح. يمكنك إعادة الاتصال، أو تعديل بيانات الاعتماد، أو إضافة جهاز جديد. |
| **Information** | روابط إلى الوثائق ودعم المنتدى. |
| **Customize** | إعادة تموضع التطبيق على سطح مكتبك، تبديل نوع الطرفية (Windows فقط)، والتحقق من تحديثات AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **نوع الطرفية (Windows)** — اختر بين **PowerShell** (الافتراضي) و**Windows Command Prompt**.
- **نوع الطرفية (Linux)** — تتوفر فقط الطرفية الافتراضية للنظام.
- **تحديثات التطبيق** — هذا التبويب هو المكان المناسب للتحقق من إصدارات AMD Sync الجديدة وتثبيتها من داخل الواجهة؛ دون الحاجة إلى أداة تحديث منفصلة.

> لا يظهر الجهاز ضمن **Devices** إلا بعد نجاح أول اتصال به، لذا فإن المحاولات الفاشلة لن تُزاحم القائمة.

---

## استكشاف الأخطاء وإصلاحها

- **فشل الاتصال فورًا** — تأكد من تفعيل خادم SSH على تبويب **Remote** في Developer Center الخاص بجهاز Ryzen AI Halo.
- **خطأ كلمة مرور خاطئة** — استخدم **كلمة مرور تسجيل الدخول لنظام التشغيل** الخاصة بجهاز Ryzen AI Halo، وليس كلمات المرور المأخوذة من Developer Center.
- **زر VS Code لا يستجيب** — ثبّت VS Code على جهازك العميل من [code.visualstudio.com](https://code.visualstudio.com).
- **أيقونة شريط AMD Sync مفقودة (Linux/GNOME)** — ثبّت وفعّل امتداد AppIndicator.
- **ملف `.deb` لا يُفتح من مدير الملفات** — استخدم `sudo apt install ./AMDSyncInstaller.deb` من الطرفية.
- **يعاود ظهور الإعداد عند كل تشغيل (Linux)**: افتح قفل حلقة مفاتيح تسجيل الدخول (keyring)، أو شغّل التطبيق باستخدام `--password-store=gnome-libsecret`، ثم أعد الإعداد مرة واحدة.

---