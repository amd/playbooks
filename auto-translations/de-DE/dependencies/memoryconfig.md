<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Für den Ryzen AI Halo beträgt der dedizierte GPU-Speicher standardmäßig 64 GB, was für die meisten Workloads ausreichend ist. Bei größeren Modellen oder längeren Kontexten kann eine Erhöhung auf 96 GB hilfreich sein. Öffnen Sie zum Anpassen **AMD Software: Adrenalin Edition™** und navigieren Sie zu **Performance → Tuning → AMD Variable Graphics Memory**. Starten Sie den Computer neu, damit die Änderungen wirksam werden.

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

Um unter Linux größere Modelle auszuführen, vergrößern Sie den **Shared-Memory**-Pool, der der GPU zur Verfügung steht. Dies kann erfordern, den dedizierten GPU-Speicher im BIOS auf das Minimum zu setzen, damit der Shared-Memory-Pool maximiert werden kann.

<!-- @device:halo_box -->

Für den AMD Ryzen™ AI Halo beträgt der Standardwert 96 GB Shared Memory. Um dies zu ändern, öffnen Sie das **AMD Ryzen™ AI Developer Center** und wechseln Sie zur Registerkarte **Settings**. Erhöhen Sie unter **Graphics Performance Settings** den Schieberegler **Shared Video Memory**, klicken Sie dann auf **Apply Changes**, und starten Sie den Computer neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Vergrößern Sie den Shared-Memory-Pool, indem Sie die Seiteneinstellung des Translation Table Manager (TTM) des Kernels ändern. AMD empfiehlt, im BIOS den minimalen dedizierten VRAM (0,5 GB) einzustellen, damit die maximale Menge als Shared Memory zur Verfügung steht.

1. Installieren Sie das Dienstprogramm `pipx` und fügen Sie den Pfad für mit pipx installierte Wheels dem System-Suchpfad hinzu:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installieren Sie das Wheel `amd-debug-tools` von PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Fragen Sie die aktuellen Shared-Memory-Einstellungen ab:

   ```bash
   amd-ttm
   ```

4. Erhöhen Sie die Shared-Memory-Zuweisung (Einheiten in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Starten Sie den Computer neu, damit die Änderungen wirksam werden.

<!-- @device:end -->

<!-- @os:end -->