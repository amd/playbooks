<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### تثبيت Lemonade

<!-- @os:windows -->
قم بتنزيل أحدث برنامج تثبيت من [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) وشغّل ملف `.msi`. 

بعد التثبيت:
- تتم إضافة أداة سطر الأوامر `lemonade` إلى مسار PATH الخاص بنظامك تلقائيًا
- من المتوقع أن يعمل خادم Lemonade في الخلفية تلقائيًا

يمكنك أيضًا التثبيت بصمت من سطر الأوامر:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

للتوزيعات الأخرى أو للتثبيت من المصدر، راجع [خيارات التثبيت الكاملة](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### التحقق من تثبيت Lemonade

افتح موجه الأوامر (terminal) وشغّل:
```bash
lemonade --version
```

يجب أن ترى ناتجًا مشابهًا لما يلي:
```
lemonade version x.y.z
```

إذا رأيت رقم إصدار، فهذا يعني أن Lemonade مثبّت بشكل صحيح وجاهز للاستخدام.

للرجوع السريع، إليك أوامر سطر الأوامر الشائعة لـ Lemonade:

| الأمر | ما الذي يفعله |
| --- | --- |
| `lemonade --help` | يعرض جميع الأوامر والخيارات المتاحة. |
| `lemonade --version` | يطبع إصدار Lemonade المثبّت. |
| `lemonade status` | يتحقق مما إذا كان خادم Lemonade يعمل ويمكن الوصول إليه. عنوان URL الأساسي الافتراضي لواجهة برمجة التطبيقات المتوافقة مع OpenAI هو `http://localhost:13305/api/v1`. |
| `lemonade list` | يسرد النماذج المتاحة في إعداد Lemonade الخاص بك. |
| `lemonade pull <MODEL_NAME>` | يقوم بتنزيل نموذج دون تشغيله. |
| `lemonade run <MODEL_NAME>` | يقوم بتنزيل النموذج إذا لزم الأمر، ثم يبدأ تشغيله للاستدلال/المحادثة. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | يبدأ تشغيل نموذج llama.cpp باستخدام خلفية ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | يبدأ تشغيل نموذج llama.cpp باستخدام خلفية Vulkan. |
| `lemonade config` | يعرض قيم إعدادات Lemonade الحالية. |
| `lemonade config set llamacpp.backend=rocm` | يضبط خلفية llama.cpp الافتراضية على ROCm. |

للحصول على أحدث خيارات خادم Lemonade أو استكشاف الأخطاء وإصلاحها، يُرجى الرجوع إلى [الوثائق الرسمية لـ Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).