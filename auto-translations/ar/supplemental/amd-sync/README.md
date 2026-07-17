<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# التطوير عن بُعد باستخدام AMD Sync

## نظرة عامة

يحوّل **AMD Sync** جهاز الكمبيوتر المحمول الخاص بك إلى لوحة تحكم عن بُعد لجهاز AMD Ryzen™ AI Halo. تخطَّ الإعداد اليدوي لـ SSH والمفاتيح وبيئة التطوير — ثبّت AMD Sync واحصل على وصول بنقرة واحدة إلى طرفية عن بُعد، و VS Code، و JupyterLab، ولوحة مراقبة مباشرة لـ GPU/CPU/الذاكرة على جهاز Ryzen AI Halo.

يبقى جهازك المحلي مألوفاً؛ كل أمر ودفتر ملاحظات ونموذج يُنفَّذ على جهاز Ryzen AI Halo.

> **تلميح**: ستحتوي هذه الصفحة على أي تحديثات جديدة لـ AMDSync.

## ما ستتعلمه

- تفعيل SSH على جهاز Ryzen AI Halo والاتصال به من AMD Sync
- تشغيل VS Code والطرفية و JupyterLab والمقاييس المباشرة على جهاز Ryzen AI Halo بنقرة واحدة
- تنظيم العمل عن بُعد باستخدام مجلدات المشاريع المُدارة في AMD Sync

---

## المفاهيم الأساسية

يتكون AMD Sync من جانبين: **عميل** (جهازك المحمول الذي يشغّل تطبيق AMD Sync) و**خادم** (جهاز Ryzen AI Halo الذي يشغّل خادم SSH الذي يتصل به AMD Sync عبر نفق). كل ما تشغّله من AMD Sync — VS Code أو طرفية أو دفتر ملاحظات — يُفتح محلياً لكنه يُنفَّذ على جهاز Ryzen AI Halo.

> **الأنظمة المدعومة للعميل:** Windows 11 وLinux. نظام macOS غير مدعوم.

---

## الخطوة 1 — تفعيل SSH على جهاز Ryzen AI Halo


> **ملاحظة:** على Windows، يأتي جهاز Ryzen AI Halo مع خادم SSH *مُعطَّلاً بشكل افتراضي*. على Linux، يأتي مع خادم SSH *مُفعَّلاً بشكل افتراضي*.

1. على جهاز Ryzen AI Halo، افتح **AMD Ryzen™ AI Developer Center**.
2. انتقل إلى تبويب **Remote**.
3. فعّل **SSH Server**.
4. لاحظ **عنوان IP** و**المنفذ** و**اسم المستخدم** المعروضة تحت **Server Information** — ستحتاج إلى لصقها في AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **ملاحظة:** هذا هو AMD Developer Center لنظام Windows. قد يختلف مظهر نسخة Linux، لكنها تتضمن وظائف مشابهة للعمل عن بُعد.

> **تلميح:** يطلب AMD Sync **كلمة مرور تسجيل الدخول إلى نظام التشغيل** لذلك المستخدم، وليس كلمة مرور من Developer Center.

---

## الخطوة 2 — تثبيت AMD Sync على جهاز العميل

يعمل AMD Sync على Windows 11 وLinux. نزّل المثبّت المناسب لنظام تشغيلك، ثم اتبع الخطوات أدناه. بعد التثبيت، انقر على **Accept & Install** في شاشة **Get Started** — يُشغَّل AMD Sync تلقائياً عند الانتهاء.

### Windows

[تنزيل AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. انقر نقراً مزدوجاً على `AMDSyncInstaller.exe`.
2. انقر على **Accept & Install**.

> إذا طالبك جدار حماية Windows، اسمح لـ AMD Sync بالوصول إلى الشبكة حتى يتمكن من الوصول إلى جهاز Ryzen AI Halo عبر SSH.

### Linux

انقر على الرابط لتنزيل الصيغة التي تفضّلها:

| الصيغة | التنزيل | أمر التثبيت |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **ملاحظة:** قد يُصنّف Ubuntu App Center ملف `.deb` المفتوح محلياً على أنه *"غير آمن محتملاً."* هذا هو التحذير المعتاد لأي مثبّت محلي من طرف ثالث. إذا فشل النقر المزدوج على ملف `.deb`، استخدم أمر الطرفية أعلاه.

---

## الخطوة 3 — الاتصال بجهاز Ryzen AI Halo

عند التشغيل الأول، يعرض AMD Sync نموذج **Add a Remote Device**. أدخل القيم من تبويب **Remote** في Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| الحقل | ملاحظات |
|-------|-------|
| **Device Name** *(اختياري)* | تسمية ودية مثل `Ryzen AI Halo`. الافتراضي هو `Device 1`، `Device 2`، … |
| **Hostname or IP** | من تبويب Remote |
| **SSH Port** | من تبويب Remote (أرقام فقط) |
| **Username** | اسم حساب نظام التشغيل على جهاز Ryzen AI Halo |
| **Password** | كلمة مرور تسجيل الدخول إلى نظام التشغيل — مخفية أثناء الكتابة |

انقر على **Add Device**. بعد شاشة تحميل قصيرة، ستظهر رسالة **"Connection Successful"** وستنتقل إلى العرض الرئيسي الموجود في علبة النظام. انقر خارج النافذة لإغلاقها؛ يبقى AMD Sync يعمل ويمكن الوصول إليه بنقرة واحدة.

> **إذا فشل الاتصال،** يعود AMD Sync إلى النموذج مع الاحتفاظ بقيمك. الأسباب الشائعة هي تعطيل SSH على جهاز Ryzen AI Halo، أو كلمة مرور خاطئة، أو وجود الجهازين على شبكات مختلفة.

---

## الخطوة 4 — تشغيل أول أداة عن بُعد

يمنحك العرض الرئيسي خمسة مكوّنات بنقرة واحدة — جميعها متاحة بغض النظر عن نظام التشغيل الذي يعمل عليه العميل وجهاز Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| المكوّن | ما يفعله |
|-----------|--------------|
| **Directory** | يختار المجلد على جهاز Ryzen AI Halo الذي سيُفتح فيه VS Code والطرفية و JupyterLab. الافتراضي هو مساحة عمل `Documents/AMD_Sync` المُدارة. |
| **VS Code** | يفتح VS Code محلياً مع نفق SSH إلى المجلد المحدد. |
| **Terminal** | يفتح طرفية محلية متصلة بـ SSH بجهاز Ryzen AI Halo، في المجلد المحدد. |
| **JupyterLab** | يشغّل مشروع دفتر ملاحظات متصلاً بـ SSH بجهاز Ryzen AI Halo، محدوداً بالمجلد المحدد. |
| **Live Metrics** | عرض في الوقت الفعلي لاستخدام GPU والذاكرة و CPU على جهاز Ryzen AI Halo. |

### جرّب VS Code

للتشغيل الأول، جرّب **VS Code**.

1. اترك **Directory** على الافتراضي `~/Documents/AMD_Sync`.
2. انقر على **VS Code**.
3. ينشئ AMD Sync مجلد `Documents/AMD_Sync/Project_1` على جهاز Ryzen AI Halo ويفتح VS Code محلياً متصلاً به عبر نفق.

أنت الآن تحرّر ملفات موجودة على جهاز Ryzen AI Halo باستخدام إعداد VS Code المحلي الخاص بك. أنشئ ملف `helloworld.py`، أضف `print("hello world")`، افتح الطرفية المدمجة (`` Ctrl + ` ``)، وشغّله:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

يعرض شريط الحالة **SSH: Linux** — دليل على أن كودك يعمل على جهاز Ryzen AI Halo وليس على جهازك المحمول.

### جرّب الطرفية

انقر على **Terminal** للانتقال مباشرة إلى نفس المجلد عبر SSH دون مغادرة لوحة المفاتيح.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

على Windows، الطرفية الافتراضية هي **PowerShell** — يمكنك التبديل إلى **Windows Command Prompt** من قائمة الإعدادات إذا كنت تفضّل ذلك. على Linux، يستخدم AMD Sync طرفية النظام الافتراضية.

---

## كيفية عمل Directory

القائمة المنسدلة **Directory** هي أهم عنصر تحكم في AMD Sync — فهي تحدد المكان الذي تُفتح فيه كل أداة تشغّلها على جهاز Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (الافتراضي)** — يؤدي تشغيل VS Code أو JupyterLab من هنا إلى إنشاء مجلد مشروع جديد تلقائياً (`Project_1`، `Project_2`، … لـ VS Code؛ `Notebook_Project_1`، `Notebook_Project_2`، … لـ JupyterLab).
- **مجلدات المشاريع الموجودة** — يظهر أي مجلد فرعي مباشر من `AMD_Sync` (بما في ذلك المجلدات التي تنشئها يدوياً على جهاز Ryzen AI Halo) في القائمة المنسدلة. يصبح آخر مجلد استخدمته هو الافتراضي في المرة القادمة.
- **المسارات المخصصة** — اكتب أي مسار مطلق لفتح مجلد في مكان آخر على جهاز Ryzen AI Halo. يقتصر AMD Sync على *فتحه* فقط — لن ينشئ مجلدات خارج `AMD_Sync`، ولا تُحفظ المسارات المخصصة بين الجلسات.

إذا لم يعمل مسار مخصص، يخبرك AMD Sync بالسبب: صياغة غير صحيحة، أو المجلد غير موجود، أو المسار يشير إلى ملف.

---

## المقاييس المباشرة و JupyterLab

- **Live Metrics** — لوحة مراقبة مباشرة لاستخدام GPU والذاكرة و CPU. أسرع طريقة للتأكد من أن عملية تدريب عن بُعد تستخدم الأجهزة فعلاً.
- **JupyterLab** — مشروع دفتر ملاحظات كامل متصل بـ SSH بجهاز Ryzen AI Halo، مع طرفية مدمجة خاصة به للجمع بين خلايا دفتر الملاحظات وأوامر الصدفة دون مغادرة الواجهة.

---

## الإعدادات والأجهزة المتعددة

تحتوي قائمة **Settings** على ثلاثة تبويبات:

| التبويب | ما يغطيه |
|-----|----------------|
| **Devices** | يسرد كل جهاز Ryzen AI Halo اتصلت به بنجاح. أعد الاتصال أو عدّل بيانات الاعتماد أو أضف جهازاً جديداً. |
| **Information** | روابط إلى الوثائق ودعم المنتدى. |
| **Customize** | أعد تحديد موضع التطبيق على سطح المكتب، وبدّل نوع الطرفية (Windows فقط)، وتحقق من تحديثات AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **نوع الطرفية (Windows)** — اختر بين **PowerShell** (الافتراضي) و**Windows Command Prompt**.
- **نوع الطرفية (Linux)** — طرفية النظام الافتراضية فقط متاحة.
- **تحديثات التطبيق** — هذا التبويب هو المكان المناسب للتحقق من إصدارات AMD Sync الجديدة وتثبيتها من داخل الواجهة؛ لا حاجة إلى أداة تحديث منفصلة.

> يظهر الجهاز تحت **Devices** فقط بعد نجاح الاتصال الأول، لذا لن تُزحم القائمة بالمحاولات الفاشلة.

---

## استكشاف الأخطاء وإصلاحها

- **فشل الاتصال فوراً** — تأكد من تفعيل خادم SSH في تبويب **Remote** في Developer Center على جهاز Ryzen AI Halo.
- **خطأ كلمة مرور خاطئة** — استخدم **كلمة مرور تسجيل الدخول إلى نظام التشغيل** على جهاز Ryzen AI Halo، وليس كلمات المرور المأخوذة من Developer Center.
- **زر VS Code لا يستجيب** — ثبّت VS Code على جهاز العميل من [code.visualstudio.com](https://code.visualstudio.com).
- **أيقونة علبة النظام لـ AMD Sync مفقودة (Linux/GNOME)** — ثبّت امتداد AppIndicator وفعّله.
- **ملف `.deb` لا يُفتح من مدير الملفات** — استخدم `sudo apt install ./AMDSyncInstaller.deb` من الطرفية.

---