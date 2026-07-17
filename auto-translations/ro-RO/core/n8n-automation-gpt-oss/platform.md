<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Cerințe preliminare

### Windows

| Componentă | Versiune | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-instalat și disponibil în PATH pe AMD Ryzen™ AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |
| **Lemonade Server** | latest | Rulează pe `http://localhost:13305/api/v1` |

### Linux

| Componentă | Versiune | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-instalat și disponibil în PATH pe AMD Ryzen™ AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |
| **Lemonade Server** | latest | Rulează pe `http://localhost:13305/api/v1` |


## Lemonade LLM

Serverul Lemonade ar trebui să ruleze cu modelul corespunzător dispozitivului încărcat (consultați README pentru comanda `lemonade run` specifică dispozitivului dvs.):

| Dispozitiv | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |