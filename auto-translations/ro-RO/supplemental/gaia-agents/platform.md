<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din engleză și nu a fost revizuită de o persoană. Poate conține erori, iar unii pași, comenzi, descărcări sau disponibilitatea produselor pot diferi în funcție de limba sau regiunea dumneavoastră. Dacă ceva pare incorect, considerați playbook-ul original în limba engleză drept sursă de referință.
<!-- auto-translated-disclaimer:end -->

# Configurarea platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestei cărți de rețete (playbook).

## Aplicații/Framework-uri necesare

### Windows/Linux

GAIA ar trebui să fie preinstalat urmând instrucțiunile furnizate în [Ghidul de instalare GAIA](../../dependencies/gaia.md).

Lemonade Server ar trebui să fie preinstalat urmând instrucțiunile furnizate în [Ghidul de instalare Lemonade](../../dependencies/lemonade.md).

## Modele necesare

### Windows/Linux

Agentul Hardware Advisor utilizează **Qwen3-Coder-30B** pentru raționamentul agentului. Acest model este descărcat automat în timpul comenzii `gaia init`. Nu este necesară descărcarea manuală a niciunui model.