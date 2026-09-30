<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

بالنسبة لـ Ryzen AI Halo، تكون ذاكرة GPU المخصصة افتراضيًا 64 جيجابايت، وهو ما يكفي لمعظم أحمال العمل. بالنسبة للنماذج الأكبر أو السياقات الأطول، قد تساعد زيادة هذه القيمة. لتعديلها، افتح **AMD Software: Adrenalin Edition™** وانتقل إلى **Performance → Tuning → AMD Variable Graphics Memory**. أعد تشغيل الجهاز لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

لتغيير قيمة ذاكرة GPU المخصصة، افتح **AMD Software: Adrenalin Edition™** وانتقل إلى **Performance → Tuning → AMD Variable Graphics Memory**. أعد تشغيل الجهاز لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

على نظام Linux، لتشغيل نماذج أكبر، قم بزيادة **تجمّع الذاكرة المشتركة** المتاح لوحدة معالجة الرسومات (GPU). قد يتطلب ذلك ضبط ذاكرة GPU المخصصة في BIOS على الحد الأدنى، بحيث يمكن زيادة تجمّع الذاكرة المشتركة إلى أقصى حد.

<!-- @device:halo_box -->

بالنسبة لـ AMD Ryzen™ AI Halo، لتعديل الإعداد الافتراضي، افتح **AMD Ryzen™ AI Developer Center** وانتقل إلى علامة التبويب **Settings**. ضمن **Graphics Performance Settings**، قم بزيادة شريط التمرير **Shared Video Memory**، ثم انقر فوق **Apply Changes** وأعد تشغيل الجهاز لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

قم بزيادة تجمّع الذاكرة المشتركة عن طريق تغيير إعداد صفحة مدير جدول الترجمة (TTM) الخاص بالنواة (kernel). توصي AMD بضبط الحد الأدنى من ذاكرة VRAM المخصصة في BIOS (0.5 جيجابايت) بحيث يتوفر أكبر قدر ممكن كذاكرة مشتركة.

1. قم بتثبيت أداة `pipx` وأضف المسار الخاص بالحزم المثبتة عبر pipx إلى مسار البحث الخاص بالنظام:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. قم بتثبيت حزمة `amd-debug-tools` من PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. استعلم عن إعدادات الذاكرة المشتركة الحالية:

   ```bash
   amd-ttm
   ```

4. قم بزيادة تخصيص الذاكرة المشتركة (الوحدة بالجيجابايت):

   ```bash
   amd-ttm --set <NUM>
   ```

5. أعد تشغيل الجهاز لتصبح التغييرات سارية المفعول.

<!-- @device:end -->

<!-- @os:end -->