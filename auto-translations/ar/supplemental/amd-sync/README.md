<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# التطوير عن بُعد باستخدام AMD Sync

## نظرة عامة

يحوّل **AMD Sync** جهازك المحمول إلى قمرة قيادة عن بُعد لـ AMD Ryzen™ AI Halo. تجاوز الإعداد اليدوي لـ SSH والمفاتيح وبيئة التطوير المتكاملة — قم بتثبيت AMD Sync واحصل على وصول بنقرة واحدة إلى طرفية عن بُعد، وVS Code، وJupyterLab، ولوحة معلومات حية للـ GPU/CPU/الذاكرة على Ryzen AI Halo.

يبقى جهازك المحلي مألوفًا كما هو؛ بينما يتم تشغيل كل أمر ودفتر ملاحظات ونموذج على Ryzen AI Halo.

> **تلميح**: ستحتوي هذه الصفحة على أي تحديثات جديدة لـ AMDSync.

## ما ستتعلمه

- تفعيل SSH على Ryzen AI Halo والاتصال به من AMD Sync
- تشغيل VS Code، والطرفية، وJupyterLab، ومقاييس الأداء الحية مقابل Ryzen AI Halo بنقرة واحدة
- تنظيم العمل عن بُعد باستخدام مجلدات المشاريع المُدارة من AMD Sync

---

## المفاهيم الأساسية

يحتوي AMD Sync على جانبين: **عميل** (جهازك المحمول، الذي يشغّل تطبيق AMD Sync) و**خادم** (Ryzen AI Halo، الذي يشغّل خادم SSH يقوم AMD Sync بإنشاء نفق عبره). كل ما تقوم بتشغيله من AMD Sync — VS Code، أو طرفية، أو دفتر ملاحظات — يُفتح محليًا لكنه يُنفَّذ على Ryzen AI Halo.

> **العملاء المدعومون:** Windows 11 وLinux. macOS غير مدعوم.

---

## الخطوة 1 — تفعيل SSH على Ryzen AI Halo


> **ملاحظة:** على Windows، يأتي Ryzen AI Halo مع خادم SSH *مُعطَّلًا افتراضيًا*. أما على Linux، فيأتي مع خادم SSH *مُفعَّلًا افتراضيًا*.

1. على Ryzen AI Halo، افتح **مركز مطوّري AMD Ryzen™ AI**.
2. انتقل إلى علامة التبويب **Remote**.
3. قم بتفعيل **SSH Server**.
4. لاحظ **IP Address**، و**Port**، و**Username** الظاهرة تحت **Server Information** — ستحتاج إلى لصقها في AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **ملاحظة:** هذا هو مركز مطوّري AMD لنظام Windows. قد يختلف واجهة المستخدم في نسخة Linux، لكن الوظائف عن بُعد متشابهة.

> **تلميح:** يطلب AMD Sync **كلمة مرور تسجيل الدخول لنظام التشغيل** لهذا المستخدم، وليس كلمة مرور من مركز المطوّرين.

---

## الخطوة 2 — تثبيت AMD Sync على جهازك

يعمل AMD Sync على Windows 11 وLinux. قم بتنزيل المُثبِّت الخاص بنظام التشغيل لديك، ثم اتبع الخطوات أدناه. بعد التثبيت، انقر فوق **Accept & Install** في شاشة **Get Started** — سيتم تشغيل AMD Sync تلقائيًا عند الانتهاء.

### Windows

[تنزيل AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. انقر نقرًا مزدوجًا فوق `AMDSyncInstaller.exe`.
2. انقر فوق **Accept & Install**.

> إذا طلب منك جدار حماية Windows إذنًا، فاسمح لـ AMD Sync بالوصول إلى الشبكة حتى يتمكن من الوصول إلى Ryzen AI Halo عبر SSH.

### Linux

انقر فوق الرابط لتنزيل الصيغة المفضّلة لديك:

| الصيغة | التنزيل | أمر التثبيت |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **ملاحظة:** قد يقوم مركز تطبيقات Ubuntu بوضع علامة على ملف `.deb` تم فتحه محليًا بأنه *"غير آمن على الأرجح"*. هذا هو التحذير القياسي لأي مُثبِّت محلي من طرف ثالث. إذا فشل النقر المزدوج على ملف `.deb`، فاستخدم أمر الطرفية أعلاه.

---

## الخطوة 3 — الاتصال بـ Ryzen AI Halo الخاص بك

عند التشغيل الأول، يعرض AMD Sync نموذج **Add a Remote Device**. قم بملئه باستخدام القيم الموجودة في علامة التبويب **Remote** بمركز المطوّرين.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| الحقل | ملاحظات |
|-------|-------|
| **Device Name** *(اختياري)* | تسمية مألوفة مثل `Ryzen AI Halo`. القيمة الافتراضية هي `Device 1`، `Device 2`، … |
| **Hostname or IP** | من علامة تبويب Remote |
| **SSH Port** | من علامة تبويب Remote (أرقام فقط) |
| **Username** | اسم حسابك على نظام التشغيل في Ryzen AI Halo |
| **Password** | كلمة مرور تسجيل الدخول لنظام التشغيل — تظهر مُخفاة أثناء الكتابة |

انقر فوق **Add Device**. بعد شاشة تحميل قصيرة، سترى **"Connection Successful"** وتنتقل إلى الصفحة الرئيسية، والتي تعيش في شريط النظام لديك. انقر خارج النافذة لإغلاقها؛ يستمر AMD Sync في العمل وهو على بُعد نقرة واحدة.

> **إذا فشل الاتصال،** يعود AMD Sync إلى النموذج مع الاحتفاظ بالقيم التي أدخلتها. الأسباب الشائعة هي تعطيل SSH على Ryzen AI Halo، أو كلمة المرور غير الصحيحة، أو وجود الجهازين على شبكتين مختلفتين.

---

## الخطوة 4 — تشغيل أول أداة عن بُعد

توفر لك الصفحة الرئيسية خمسة مكونات بنقرة واحدة — وكلها متاحة بغض النظر عن نظام التشغيل الذي يعمل عليه العميل وRyzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| المكوّن | ماذا يفعل |
|-----------|--------------|
| **Directory** | يختار المجلد على Ryzen AI Halo الذي سيتم فتح VS Code والطرفية وJupyterLab فيه. القيمة الافتراضية هي مساحة عمل مُدارة `Documents/AMD_Sync`. |
| **VS Code** | يفتح VS Code محليًا مع نفق SSH داخل المجلد المحدد. |
| **Terminal** | يفتح طرفية محلية متصلة عبر SSH بـ Ryzen AI Halo، في المجلد المحدد. |
| **JupyterLab** | يشغّل مشروع دفتر ملاحظات متصل عبر SSH بـ Ryzen AI Halo، محصورًا في المجلد المحدد. |
| **Live Metrics** | عرض حي لاستخدام GPU والذاكرة وCPU على Ryzen AI Halo. |

### جرّب VS Code

للتشغيل الأول، جرّب **VS Code**.

1. اترك **Directory** على القيمة الافتراضية `~/Documents/AMD_Sync`.
2. انقر فوق **VS Code**.
3. ينشئ AMD Sync المجلد `Documents/AMD_Sync/Project_1` على Ryzen AI Halo ويفتح VS Code محليًا، عبر نفق متصل به.

أنت الآن تقوم بتحرير ملفات موجودة على Ryzen AI Halo باستخدام إعداد VS Code المحلي لديك. أنشئ ملف `helloworld.py`، أضف `print("hello world")`، افتح الطرفية المدمجة (`` Ctrl + ` ``)، وقم بتشغيله:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

يعرض شريط الحالة **SSH: Linux** — كدليل على أن الكود الخاص بك يعمل على Ryzen AI Halo، وليس على جهازك المحمول.
### جرّب Terminal

انقر على **Terminal** للدخول إلى نفس المجلد عبر SSH دون الحاجة إلى ترك لوحة المفاتيح.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

على Windows، الطرفية الافتراضية هي **PowerShell** — بدّل إلى **Windows Command Prompt** من قائمة الإعدادات إذا كنت تفضل ذلك. على Linux، تستخدم AMD Sync الطرفية الافتراضية لنظامك.

---

## كيف تعمل الدليل (Directory)

القائمة المنسدلة **Directory** هي أهم عنصر تحكم واحد في AMD Sync — فهي التي تحدد أين تُنزَّل كل أداة تُطلقها على Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (الافتراضي)** — إطلاق VS Code أو JupyterLab من هنا ينشئ تلقائيًا مجلد مشروع جديد (`Project_1`، `Project_2`، … لـ VS Code؛ و`Notebook_Project_1`، `Notebook_Project_2`، … لـ JupyterLab).
- **مجلدات المشاريع الموجودة** — يظهر في القائمة المنسدلة أي مجلد فرعي مباشر ضمن `AMD_Sync` (بما في ذلك المجلدات التي تنشئها يدويًا على Ryzen AI Halo). يصبح آخر مجلد استخدمته هو الافتراضي في المرة التالية.
- **المسارات المخصصة** — اكتب أي مسار مطلق لفتح مجلد في مكان آخر على Ryzen AI Halo. تقوم AMD Sync فقط *بفتحه* — فهي لن تُنشئ مجلدات خارج `AMD_Sync`، ولا تُحفظ المسارات المخصصة بين الجلسات.

إذا لم يعمل مسار مخصص، تُخبرك AMD Sync بالسبب: صياغة غير صالحة، أو المجلد غير موجود، أو المسار يشير إلى ملف.

---

## المقاييس الحيّة وJupyterLab

- **Live Metrics** — لوحة معلومات حيّة لاستخدام GPU والذاكرة وCPU. إنها أسرع طريقة للتأكد من أن تشغيل تدريب عن بُعد يصل فعليًا إلى العتاد.
- **JupyterLab** — مشروع دفتر ملاحظات كامل متصل عبر SSH بـ Ryzen AI Halo، مع طرفية مدمجة خاصة به لمزج خلايا الدفتر مع أوامر الصدفة دون مغادرة الواجهة.

---

## الإعدادات والأجهزة المتعددة

تحتوي قائمة **Settings** على ثلاثة تبويبات:

| التبويب | ما يشمله |
|-----|----------------|
| **Devices** | يسرد كل جهاز Ryzen AI Halo اتصلت به بنجاح. أعد الاتصال، أو عدّل بيانات الاعتماد، أو أضف جهازًا جديدًا. |
| **Information** | روابط إلى الوثائق ودعم المنتدى. |
| **Customize** | أعد وضع التطبيق على سطح المكتب، وبدّل نوع الطرفية (Windows فقط)، وتحقق من تحديثات AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **نوع الطرفية (Windows)** — اختر بين **PowerShell** (الافتراضي) و**Windows Command Prompt**.
- **نوع الطرفية (Linux)** — لا تتوفر سوى الطرفية الافتراضية للنظام.
- **تحديثات التطبيق** — هذا التبويب هو المكان المناسب للتحقق من إصدارات جديدة من AMD Sync وتثبيتها من داخل الواجهة؛ لا حاجة إلى أداة تحديث منفصلة.

> لا يظهر الجهاز ضمن **Devices** إلا بعد اتصال أول ناجح، لذا فإن المحاولات الفاشلة لن تُثقل القائمة.

---

## استكشاف الأخطاء وإصلاحها

- **يفشل الاتصال فورًا** — تأكد من تمكين خادم SSH على تبويب **Remote** في Ryzen AI Halo ضمن Developer Center.
- **خطأ كلمة مرور خاطئة** — استخدم **كلمة مرور تسجيل الدخول لنظام التشغيل** على Ryzen AI Halo، وليس كلمات المرور المأخوذة من Developer Center.
- **زر VS Code لا يفعل شيئًا** — ثبّت VS Code على جهازك العميل من [code.visualstudio.com](https://code.visualstudio.com).
- **أيقونة AMD Sync في شريط النظام مفقودة (Linux/GNOME)** — ثبّت وفعّل امتداد AppIndicator.
- **ملف `.deb` لا يُفتح من مدير الملفات** — استخدم `sudo apt install ./AMDSyncInstaller.deb` من الطرفية.
- **يظهر إعداد التهيئة عند كل تشغيل (Linux)**: افتح قفل مخزن كلمات مرور تسجيل الدخول، أو شغّل باستخدام `--password-store=gnome-libsecret`، ثم أعد إجراء الإعداد مرة واحدة.

---