<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform-konfigurációkat írja le.

## Előfeltételek

### Windows

| Összetevő | Verzió | Megjegyzések |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Előre telepítve és elérhető a PATH-ban az AMD Ryzen™ AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |
| **Lemonade Server** | legújabb | A következő címen fut: `http://localhost:13305/api/v1` |

### Linux

| Összetevő | Verzió | Megjegyzések |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Előre telepítve és elérhető a PATH-ban az AMD Ryzen™ AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |
| **Lemonade Server** | legújabb | A következő címen fut: `http://localhost:13305/api/v1` |


## Lemonade LLM

A Lemonade szervernek futnia kell az eszközhöz megfelelő betöltött modellel (lásd a README-t a `lemonade run` parancshoz az adott eszközön):

| Eszköz | Végpont | Modell |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |