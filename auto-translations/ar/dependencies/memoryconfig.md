<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

بالنسبة لـ Ryzen AI Halo، تبلغ ذاكرة GPU المخصصة الافتراضية 64 جيجابايت، وهي كافية لمعظم أعباء العمل. بالنسبة للنماذج الأكبر أو السياقات الأطول، قد تساعد زيادتها إلى 96 جيجابايت. للضبط، افتح **AMD Software: Adrenalin Edition™** وانتقل إلى **Performance → Tuning → AMD Variable Graphics Memory**. أعد التشغيل لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

لتغيير قيمة ذاكرة GPU المخصصة، افتح **AMD Software: Adrenalin Edition™** وانتقل إلى **Performance → Tuning → AMD Variable Graphics Memory**. أعد التشغيل لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

على Linux، لتشغيل نماذج أكبر، قم بزيادة مجموعة **الذاكرة المشتركة** المتاحة لـ GPU. قد يتضمن ذلك ضبط ذاكرة GPU المخصصة في BIOS على الحد الأدنى، حتى يمكن تعظيم مجموعة الذاكرة المشتركة.

<!-- @device:halo_box -->

بالنسبة لـ AMD Ryzen™ AI Halo، الإعداد الافتراضي هو 96 جيجابايت مشتركة. لتعديل ذلك، افتح **AMD Ryzen™ AI Developer Center** وانتقل إلى علامة التبويب **Settings**. ضمن **Graphics Performance Settings**، قم بزيادة شريط تمرير **Shared Video Memory**، ثم انقر على **Apply Changes** وأعد التشغيل لتصبح التغييرات سارية المفعول.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

قم بزيادة مجموعة الذاكرة المشتركة عن طريق تغيير إعداد صفحة مدير جدول الترجمة (TTM) الخاص بالنواة. توصي AMD بضبط الحد الأدنى من VRAM المخصصة في BIOS (0.5 جيجابايت) حتى يكون الحد الأقصى من الذاكرة متاحاً كذاكرة مشتركة.

1. قم بتثبيت الأداة المساعدة `pipx` وأضف المسار لعجلات المثبتة عبر pipx إلى مسار البحث في النظام:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. قم بتثبيت عجلة `amd-debug-tools` من PyPI:

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

5. أعد التشغيل لتصبح التغييرات سارية المفعول.

<!-- @device:end -->

<!-- @os:end -->