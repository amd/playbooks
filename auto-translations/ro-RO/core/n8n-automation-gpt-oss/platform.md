<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din engleză și nu a fost revizuită de o persoană. Poate conține erori, iar unii pași, comenzi, descărcări sau disponibilitatea produselor pot diferi în funcție de limba sau regiunea dumneavoastră. Dacă ceva pare incorect, considerați playbook-ul original în limba engleză drept sursă de referință.
<!-- auto-translated-disclaimer:end -->

# Configurarea platformei

Acest document descrie configurațiile de platformă preconizate pentru rularea acestui playbook.

## Cerințe preliminare

### Windows

| Componentă | Versiune | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalat și disponibil în PATH pe AMD Ryzen™ AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |
| **Lemonade Server** | cea mai recentă | Rulează pe `http://localhost:13305/api/v1` |

### Linux

| Componentă | Versiune | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalat și disponibil în PATH pe AMD Ryzen™ AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |
| **Lemonade Server** | cea mai recentă | Rulează pe `http://localhost:13305/api/v1` |


## Lemonade LLM

Serverul Lemonade trebuie să ruleze cu modelul adecvat dispozitivului încărcat (consultați README pentru comanda `lemonade run` corespunzătoare dispozitivului dvs.):

| Dispozitiv | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |