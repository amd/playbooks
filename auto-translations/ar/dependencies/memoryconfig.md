<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

بالنسبة لـ Ryzen AI Halo، تكون ذاكرة GPU المخصصة افتراضيًا 64 جيجابايت، وهي كافية لمعظم أحمال العمل. بالنسبة للنماذج الأكبر أو السياقات الأطول، قد تساعد زيادة هذه القيمة. للتعديل، افتح **AMD Software: Adrenalin Edition™** وانتقل إلى **Performance → Tuning → AMD Variable Graphics Memory**. أعد التشغيل لتفعيل التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

لتغيير قيمة ذاكرة GPU المخصصة، افتح **AMD Software: Adrenalin Edition™** وانتقل إلى **Performance → Tuning → AMD Variable Graphics Memory**. أعد التشغيل لتفعيل التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

على Linux، لتشغيل نماذج أكبر، قم بزيادة مجمع **الذاكرة المشتركة** المتاح لـ GPU. قد يتطلب هذا ضبط ذاكرة GPU المخصصة في BIOS إلى الحد الأدنى، بحيث يمكن زيادة مجمع الذاكرة المشتركة إلى أقصى حد.

<!-- @device:halo_box -->

بالنسبة لـ AMD Ryzen™ AI Halo، لتعديل الإعداد الافتراضي، افتح **AMD Ryzen™ AI Developer Center** وانتقل إلى علامة التبويب **Settings**. ضمن **Graphics Performance Settings**، قم بزيادة شريط **Shared Video Memory**، ثم انقر فوق **Apply Changes** وأعد التشغيل لتفعيل التغييرات.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

قم بزيادة مجمع الذاكرة المشتركة عن طريق تغيير إعداد صفحة مدير جدول الترجمة (TTM) الخاص بالنواة. توصي AMD بضبط الحد الأدنى لذاكرة VRAM المخصصة في BIOS (0.5 جيجابايت) حتى يتوفر أقصى قدر ممكن كذاكرة مشتركة.

1. قم بتثبيت الأداة المساعدة `pipx` وأضف المسار الخاص بالحزم المثبتة عبر pipx إلى مسار البحث الخاص بالنظام:

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

4. قم بزيادة تخصيص الذاكرة المشتركة (الوحدات بالجيجابايت):

   ```bash
   amd-ttm --set <NUM>
   ```

5. أعد التشغيل لتفعيل التغييرات.

<!-- @device:end -->

<!-- @os:end -->