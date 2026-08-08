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

يحوّل **AMD Sync** حاسوبك المحمول إلى قمرة قيادة عن بُعد لجهاز AMD Ryzen™ AI Halo. تخطَّ الإعداد اليدوي لـ SSH والمفاتيح وبيئة التطوير المتكاملة — قم بتثبيت AMD Sync واحصل بنقرة واحدة على طرفية (terminal) عن بُعد، وVS Code، وJupyterLab، ولوحة معلومات حية لوحدة معالجة الرسومات (GPU) ووحدة المعالجة المركزية (CPU) والذاكرة على Ryzen AI Halo.

يظل جهازك المحلي مألوفًا؛ فكل أمر ودفتر ملاحظات ونموذج يعمل على Ryzen AI Halo.

> **نصيحة**: ستحتوي هذه الصفحة على أي تحديثات جديدة لـ AMDSync.

## ما ستتعلمه

- تفعيل SSH على Ryzen AI Halo والاتصال به من AMD Sync
- تشغيل VS Code والطرفية (Terminal) وJupyterLab والمقاييس الحية (Live Metrics) على Ryzen AI Halo بنقرة واحدة
- تنظيم العمل عن بُعد باستخدام مجلدات المشاريع المُدارة في AMD Sync

---

## المفاهيم الأساسية

يتكوّن AMD Sync من طرفين: **عميل** (client) (حاسوبك المحمول، الذي يشغّل تطبيق AMD Sync) و**خادم** (server) (Ryzen AI Halo، الذي يشغّل خادم SSH يقوم AMD Sync بإنشاء نفق (tunnel) داخله). كل ما تشغّله من AMD Sync — VS Code، أو طرفية، أو دفتر ملاحظات — يُفتح محليًا لكنه يُنفَّذ على Ryzen AI Halo.

> **العملاء المدعومون:** Windows 11 وLinux. نظام macOS غير مدعوم.

---

## الخطوة 1 — تفعيل SSH على Ryzen AI Halo


> **ملاحظة:** على نظام Windows، يأتي جهاز Ryzen AI Halo مع خادم SSH *معطّلًا افتراضيًا*. أما على Linux، فيأتي مع خادم SSH *مفعّلًا افتراضيًا*.

1. على جهاز Ryzen AI Halo، افتح **مركز مطوري AMD Ryzen™ AI** (AMD Ryzen™ AI Developer Center).
2. انتقل إلى علامة التبويب **Remote**.
3. فعّل خيار **SSH Server**.
4. لاحظ **عنوان IP**، و**المنفذ (Port)**، و**اسم المستخدم (Username)** الظاهرة تحت **معلومات الخادم (Server Information)** — ستحتاج إلى لصقها في AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **ملاحظة:** هذا هو مركز مطوري AMD الخاص بنظام Windows. قد يختلف واجهة الإصدار الخاص بـ Linux، لكنه يوفّر وظائف مماثلة للعمل عن بُعد.

> **نصيحة:** يطلب AMD Sync **كلمة مرور تسجيل الدخول لنظام التشغيل (OS login password)** لذلك المستخدم، وليس كلمة مرور من مركز المطورين.

---

## الخطوة 2 — تثبيت AMD Sync على جهاز العميل

يعمل AMD Sync على نظامي Windows 11 وLinux. قم بتنزيل المثبِّت الخاص بنظام التشغيل لديك، ثم اتبع الخطوات أدناه. بعد التثبيت، انقر على **Accept & Install** في شاشة **Get Started** — سيُطلق AMD Sync تلقائيًا عند الانتهاء.

### Windows

[تنزيل AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. انقر نقرًا مزدوجًا على `AMDSyncInstaller.exe`.
2. انقر على **Accept & Install**.

> إذا طلب منك جدار حماية Windows إذنًا، فاسمح لـ AMD Sync بالوصول إلى الشبكة حتى يتمكن من الوصول إلى Ryzen AI Halo عبر SSH.

### Linux

انقر على الرابط لتنزيل التنسيق الذي تفضّله:

| التنسيق | التنزيل | أمر التثبيت |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **ملاحظة:** قد يُصنِّف مركز تطبيقات Ubuntu ملف `.deb` المفتوح محليًا على أنه *"قد يكون غير آمن."* هذا هو التحذير المعتاد لأي مثبِّت محلي من جهة خارجية. إذا فشل النقر المزدوج على ملف `.deb`، فاستخدم أمر الطرفية أعلاه.

---

## الخطوة 3 — الاتصال بجهاز Ryzen AI Halo الخاص بك

عند التشغيل لأول مرة، يعرض AMD Sync نموذج **Add a Remote Device**. قم بملئه باستخدام القيم من علامة التبويب **Remote** في مركز المطورين.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| الحقل | ملاحظات |
|-------|-------|
| **اسم الجهاز** *(اختياري)* | تسمية مألوفة مثل `Ryzen AI Halo`. الإعداد الافتراضي هو `Device 1`، `Device 2`، … |
| **Hostname or IP** | من علامة التبويب Remote |
| **SSH Port** | من علامة التبويب Remote (أرقام فقط) |
| **Username** | اسم حساب نظام التشغيل الخاص بك على Ryzen AI Halo |
| **Password** | كلمة مرور تسجيل الدخول لنظام التشغيل الخاصة بك — تظهر مموّهة أثناء الكتابة |

انقر على **Add Device**. بعد شاشة تحميل قصيرة، سترى رسالة **"Connection Successful"** وستنتقل إلى الشاشة الرئيسية، التي تقيم في شريط النظام (system tray). انقر خارج النافذة لإغلاقها؛ يبقى AMD Sync يعمل ويكون متاحًا بنقرة واحدة.

> **إذا فشل الاتصال،** يعود AMD Sync إلى النموذج مع الاحتفاظ بالقيم التي أدخلتها. الأسباب الشائعة هي تعطيل SSH على Ryzen AI Halo، أو كلمة المرور الخاطئة، أو وجود الجهازين على شبكتين مختلفتين.

---

## الخطوة 4 — تشغيل أول أداة عن بُعد

توفّر لك الشاشة الرئيسية خمسة مكوّنات بنقرة واحدة — وكلها متاحة بغض النظر عن نظام التشغيل الذي يعمل عليه العميل وRyzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| المكوّن | ما الذي يقوم به |
|-----------|--------------|
| **Directory** | يحدد المجلد على Ryzen AI Halo الذي سيُفتح فيه VS Code والطرفية وJupyterLab. الإعداد الافتراضي هو مساحة عمل مُدارة `Documents/AMD_Sync`. |
| **VS Code** | يفتح VS Code محليًا مع نفق SSH إلى المجلد المحدد. |
| **Terminal** | يفتح طرفية محلية متصلة عبر SSH بـ Ryzen AI Halo، في المجلد المحدد. |
| **JupyterLab** | يُطلق مشروع دفتر ملاحظات متصل عبر SSH بـ Ryzen AI Halo، ومحصور في المجلد المحدد. |
| **Live Metrics** | عرض في الوقت الفعلي لاستخدام GPU والذاكرة وCPU على Ryzen AI Halo. |

### جرّب VS Code

في أول عملية تشغيل لك، جرّب **VS Code**.

1. اترك **Directory** على الإعداد الافتراضي `~/Documents/AMD_Sync`.
2. انقر على **VS Code**.
3. ينشئ AMD Sync المجلد `Documents/AMD_Sync/Project_1` على Ryzen AI Halo ويفتح VS Code محليًا، متصلًا بنفق إليه.

أنت الآن تحرّر ملفات موجودة على Ryzen AI Halo باستخدام إعداد VS Code المحلي الخاص بك. أنشئ ملف `helloworld.py`، وأضف `print("hello world")`، ثم افتح الطرفية المدمجة (`` Ctrl + ` ``)، وشغّله:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

يعرض شريط الحالة **SSH: Linux** — دليل على أن الكود الخاص بك يعمل على Ryzen AI Halo، وليس على حاسوبك المحمول.
### جرّب Terminal

انقر على **Terminal** للدخول إلى نفس المجلد عبر SSH دون ترك لوحة المفاتيح.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

في نظام Windows، الطرفية الافتراضية هي **PowerShell** — يمكنك التبديل إلى **Windows Command Prompt** من قائمة الإعدادات إذا كنت تفضل ذلك. في نظام Linux، يستخدم AMD Sync الطرفية الافتراضية لنظامك.

---

## كيف يعمل الدليل (Directory)

القائمة المنسدلة **Directory** هي أهم عنصر تحكم منفرد في AMD Sync — فهي تحدد أين يهبط كل أداة تُطلقها على Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (الافتراضي)** — يؤدي تشغيل VS Code أو JupyterLab من هنا إلى إنشاء مجلد مشروع جديد تلقائيًا (`Project_1`، `Project_2`، … لـ VS Code؛ و`Notebook_Project_1`، `Notebook_Project_2`، … لـ JupyterLab).
- **مجلدات المشاريع الموجودة** — يظهر في القائمة المنسدلة أي مجلد فرعي مباشر تابع لـ `AMD_Sync` (بما في ذلك المجلدات التي تنشئها يدويًا على Ryzen AI Halo). يصبح آخر مجلد استخدمته هو الافتراضي في المرة القادمة.
- **المسارات المخصصة** — اكتب أي مسار مطلق لفتح مجلد في مكان آخر على Ryzen AI Halo. يقوم AMD Sync فقط *بفتح* المجلد — لن ينشئ مجلدات خارج `AMD_Sync`، ولا يتم حفظ المسارات المخصصة بين الجلسات.

إذا لم يعمل مسار مخصص، يخبرك AMD Sync بالسبب: بنية غير صالحة، أو المجلد غير موجود، أو المسار يشير إلى ملف.

---

## Live Metrics و JupyterLab

- **Live Metrics** — لوحة معلومات مباشرة لاستخدام الـ GPU والذاكرة والـ CPU. إنها أسرع طريقة للتأكد من أن عملية تدريب عن بُعد تستخدم العتاد فعليًا.
- **JupyterLab** — مشروع دفتر ملاحظات كامل متصل عبر SSH بـ Ryzen AI Halo، مزود بطرفية مدمجة خاصة به لمزج خلايا الدفتر مع أوامر الصدفة دون مغادرة الواجهة.

---

## الإعدادات وأجهزة متعددة

تحتوي قائمة **Settings** على ثلاثة تبويبات:

| التبويب | ما يشمله |
|-----|----------------|
| **Devices** | يسرد كل جهاز Ryzen AI Halo اتصلت به بنجاح. أعد الاتصال، أو عدّل بيانات الاعتماد، أو أضف جهازًا جديدًا. |
| **Information** | روابط إلى الوثائق ودعم المنتدى. |
| **Customize** | أعد تموضع التطبيق على سطح مكتبك، وبدّل نوع الطرفية (Windows فقط)، وتحقق من تحديثات AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **نوع الطرفية (Windows)** — اختر بين **PowerShell** (الافتراضي) و**Windows Command Prompt**.
- **نوع الطرفية (Linux)** — تتوفر فقط الطرفية الافتراضية للنظام.
- **تحديثات التطبيق** — هذا التبويب هو المكان المناسب للتحقق من إصدارات جديدة من AMD Sync وتثبيتها من داخل الواجهة؛ لا حاجة إلى أداة تحديث منفصلة.

> لا يظهر الجهاز ضمن **Devices** إلا بعد نجاح أول اتصال، لذا لن تزدحم القائمة بالمحاولات الفاشلة.

---

## استكشاف الأخطاء وإصلاحها

- **فشل الاتصال فورًا** — تأكد من تفعيل خادم SSH على تبويب **Remote** في Developer Center الخاص بجهاز Ryzen AI Halo.
- **خطأ كلمة المرور خاطئة** — استخدم **كلمة مرور تسجيل الدخول لنظام التشغيل** الخاصة بجهاز Ryzen AI Halo، وليس كلمات المرور المأخوذة من Developer Center.
- **زر VS Code لا يفعل شيئًا** — ثبّت VS Code على جهازك العميل من [code.visualstudio.com](https://code.visualstudio.com).
- **أيقونة AMD Sync في شريط النظام مفقودة (Linux/GNOME)** — ثبّت وفعّل امتداد AppIndicator.
- **ملف `.deb` لا يفتح من مدير الملفات** — استخدم `sudo apt install ./AMDSyncInstaller.deb` من الطرفية.

---