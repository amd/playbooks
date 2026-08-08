<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
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