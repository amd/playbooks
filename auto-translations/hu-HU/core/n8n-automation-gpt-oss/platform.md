<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformkonfiguráció

Ez a dokumentum ismerteti a jelen forgatókönyv futtatásához szükséges platformkonfigurációkat.

## Előfeltételek

### Windows

| Komponens | Verzió | Megjegyzések |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Az AMD Ryzen™ AI Halo Developer Platform eszközön előre telepítve és a PATH-ban elérhető; minden más eszközön manuálisan kell telepíteni |
| **Lemonade Server** | legfrissebb | A `http://localhost:13305/api/v1` címen fut |

### Linux

| Komponens | Verzió | Megjegyzések |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Az AMD Ryzen™ AI Halo Developer Platform eszközön előre telepítve és a PATH-ban elérhető; minden más eszközön manuálisan kell telepíteni |
| **Lemonade Server** | legfrissebb | A `http://localhost:13305/api/v1` címen fut |


## Lemonade LLM

A Lemonade szervernek futnia kell a megfelelő, az adott eszközhöz illő betöltött modellel (lásd az README fájlt az eszközéhez tartozó `lemonade run` parancshoz):

| Eszköz | Végpont | Modell |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |