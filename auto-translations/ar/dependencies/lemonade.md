<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### تثبيت Lemonade

<!-- @os:windows -->
قم بتنزيل أحدث مثبّت من [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) وشغّل ملف `.msi`.

بعد التثبيت:
- تتم إضافة واجهة سطر الأوامر `lemonade` إلى متغير PATH الخاص بنظامك تلقائيًا
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

افتح طرفية ونفّذ:
```bash
lemonade --version
```

يجب أن تظهر لك مخرجات مثل:
```
lemonade version x.y.z
```

إذا رأيت رقم إصدار، فهذا يعني أن Lemonade مثبّت بشكل صحيح وجاهز للاستخدام.

للرجوع السريع، إليك أوامر Lemonade CLI الشائعة:

| الأمر | ما يفعله |
| --- | --- |
| `lemonade --help` | يعرض جميع الأوامر والأعلام المتاحة. |
| `lemonade --version` | يطبع إصدار Lemonade المثبّت. |
| `lemonade status` | يؤكد ما إذا كان خادم Lemonade يعمل ويمكن الوصول إليه. عنوان URL الافتراضي لواجهة برمجة التطبيقات المتوافقة مع OpenAI هو `http://localhost:13305/api/v1`. |
| `lemonade list` | يسرد النماذج المتاحة لإعداد Lemonade الخاص بك. |
| `lemonade pull <MODEL_NAME>` | ينزّل نموذجًا دون تشغيله. |
| `lemonade run <MODEL_NAME>` | ينزّل النموذج إذا لزم الأمر، ثم يشغّله للاستدلال/الدردشة. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | يشغّل نموذج llama.cpp مع خلفية ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | يشغّل نموذج llama.cpp مع خلفية Vulkan. |
| `lemonade config` | يعرض قيم تكوين Lemonade الحالية. |
| `lemonade config set llamacpp.backend=rocm` | يضبط خلفية llama.cpp الافتراضية على ROCm. |

للاطلاع على أحدث خيارات خادم Lemonade أو استكشاف الأخطاء وإصلاحها، يرجى الرجوع إلى [وثائق Lemonade الرسمية](https://lemonade-server.ai/docs/lemonade-cli/).