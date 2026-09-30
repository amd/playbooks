<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Bei Ryzen AI Halo beträgt der dedizierte GPU-Speicher standardmäßig 64 GB, was für die meisten Workloads ausreichend ist. Bei größeren Modellen oder längeren Kontexten kann eine Erhöhung hilfreich sein. Öffnen Sie zum Anpassen **AMD Software: Adrenalin Edition™** und navigieren Sie zu **Performance → Tuning → AMD Variable Graphics Memory**. Starten Sie den Computer neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Um den Wert für den dedizierten GPU-Speicher zu ändern, öffnen Sie **AMD Software: Adrenalin Edition™** und navigieren Sie zu **Performance → Tuning → AMD Variable Graphics Memory**. Starten Sie den Computer neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Um unter Linux größere Modelle auszuführen, erhöhen Sie den **gemeinsam genutzten Speicherpool (shared memory)**, der der GPU zur Verfügung steht. Dies kann erfordern, den dedizierten GPU-Speicher im BIOS auf das Minimum zu setzen, damit der gemeinsam genutzte Speicherpool maximiert werden kann.

<!-- @device:halo_box -->

Um bei AMD Ryzen™ AI Halo die Standardeinstellung zu ändern, öffnen Sie das **AMD Ryzen™ AI Developer Center** und wechseln Sie zur Registerkarte **Settings**. Erhöhen Sie unter **Graphics Performance Settings** den Schieberegler **Shared Video Memory**, klicken Sie dann auf **Apply Changes** und starten Sie den Computer neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Erhöhen Sie den gemeinsam genutzten Speicherpool, indem Sie die TTM-Seiteneinstellung (Translation Table Manager) des Kernels ändern. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS einzustellen (0,5 GB), damit die maximale Menge als gemeinsam genutzter Speicher zur Verfügung steht.

1. Installieren Sie das `pipx`-Dienstprogramm und fügen Sie den Pfad für mit pipx installierte Wheels dem System-Suchpfad hinzu:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installieren Sie das `amd-debug-tools`-Wheel von PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Fragen Sie die aktuellen Einstellungen für den gemeinsam genutzten Speicher ab:

   ```bash
   amd-ttm
   ```

4. Erhöhen Sie die Zuweisung für den gemeinsam genutzten Speicher (Einheiten in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Starten Sie den Computer neu, damit die Änderungen wirksam werden.

<!-- @device:end -->

<!-- @os:end -->