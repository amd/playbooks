<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Beim Ryzen AI Halo beträgt der dedizierte GPU-Speicher standardmäßig 64 GB, was für die meisten Workloads ausreichend ist. Bei größeren Modellen oder längeren Kontexten kann eine Erhöhung auf 96 GB hilfreich sein. Öffnen Sie zur Anpassung **AMD Software: Adrenalin Edition™** und navigieren Sie zu **Performance → Tuning → AMD Variable Graphics Memory**. Starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Um den dedizierten GPU-Speicherwert zu ändern, öffnen Sie **AMD Software: Adrenalin Edition™** und navigieren Sie zu **Performance → Tuning → AMD Variable Graphics Memory**. Starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Unter Linux erhöhen Sie den für die GPU verfügbaren **Shared Memory**-Pool, um größere Modelle auszuführen. Dies kann erfordern, den dedizierten GPU-Speicher im BIOS auf den Minimalwert zu setzen, damit der Shared Memory-Pool maximiert werden kann.

<!-- @device:halo_box -->

Beim AMD Ryzen™ AI Halo beträgt der Standardwert 96 GB Shared Memory. Um diesen zu ändern, öffnen Sie das **AMD Ryzen™ AI Developer Center** und wechseln Sie zur Registerkarte **Settings**. Erhöhen Sie unter **Graphics Performance Settings** den Regler **Shared Video Memory**, klicken Sie dann auf **Apply Changes** und starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Erhöhen Sie den Shared Memory-Pool, indem Sie die TTM-Seiteneinstellung (Translation Table Manager) des Kernels ändern. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS (0,5 GB) festzulegen, damit der maximale Speicheranteil als Shared Memory verfügbar ist.

1. Installieren Sie das Dienstprogramm `pipx` und fügen Sie den Pfad für von pipx installierte Wheels zum Systemsuchpfad hinzu:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installieren Sie das `amd-debug-tools`-Wheel von PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Fragen Sie die aktuellen Shared Memory-Einstellungen ab:

   ```bash
   amd-ttm
   ```

4. Erhöhen Sie die Shared Memory-Zuweisung (Einheit in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Starten Sie das System neu, damit die Änderungen wirksam werden.

<!-- @device:end -->

<!-- @os:end -->