<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguráció — Lemonade Local AI

Ez a dokumentum ismerteti az előre telepített szoftvereket, a modell-elérési utakat, valamint a platformspecifikus előfeltételeket, amelyeket ez a playbook feltételez.

## Előre telepített szoftverek

| Szoftver | Verzió | Cél |
|----------|---------|---------|
| Lemonade Server | Legújabb kiadás | Helyi LLM-kiszolgáló OpenAI-kompatibilis API-val |
| Python | 3.10–3.13 | Az OpenAI Python kliens példához szükséges |

## Alapértelmezett modelltárolás

A Lemonade-en keresztül letöltött modellek a Hugging Face Hub specifikációja szerint kerülnek tárolásra:

| Platform | Alapértelmezett elérési út |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

A tárolási hely módosításához állítsa be a `HF_HOME` környezeti változót.

## Hardverkövetelmények

| Hardvercél | Követelmények |
|----------------|-------------|
| **CPU** | Bármilyen modern x86-64 processzor (AMD vagy Intel) |
| **GPU (Vulkan)** | Bármilyen GPU Vulkan-illesztőprogram-támogatással |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 sorozat vagy Radeon PRO W7000 sorozat; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 sorozatú processzor, Windows 11 |

## Hálózati követelmények

- Internetkapcsolat szükséges a kezdeti modelletöltéshez (1–25 GB a modelltől függően)
- A modellek letöltése után nincs szükség internetkapcsolatra