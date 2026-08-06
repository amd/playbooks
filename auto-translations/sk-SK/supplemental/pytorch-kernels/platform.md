<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávanú konfiguráciu platformy na spustenie tohto playbooku.

## Požadované aplikácie/frameworky

| Komponent       | Očakávaná konfigurácia               | Poznámky                                                                        |
| --------------- | ------------------------------------ | -------------------------------------------------------------------------------- |
| Python          | Python s podporou `venv`         | Používa sa na vytvorenie a aktiváciu `kernel-env`                                     |
| ROCm Python SDK | Rodina balíkov ROCm 7.13             | Nainštalované prostredníctvom procesu závislostí playbooku                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vyžaduje sa pre `torch.cuda`, HIP runtime, JIT kompiláciu a `CUDAExtension` |
| Ovládač GPU      | Ovládač AMD GPU s podporou ROCm/HIP | Vyžaduje sa pred tým, ako PyTorch dokáže rozpoznať AMD GPU                               |

> Poznámka: Ak používate AMD Ryzen™ AI Halo Developer Platform, softvér AMD ROCm™ a PyTorch sú predinštalované.

## Predpoklady pre Linux

Vyžadujú sa nasledujúce systémové balíky:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je potrebný na vytvorenie `kernel-env`.
* `build-essential`, `gcc` a `g++` sú potrebné pre návody týkajúce sa rozšírení v jazyku C++.
* `amd-smi` sa používa na kontrolu viditeľnosti/vyťaženia GPU v systéme Linux.

Príklady rozšírení v jazyku C++ zostavujú natívne moduly `.so` zo súborov `.cu` pomocou cesty `CUDAExtension` v PyTorch.

## Predpoklady pre Windows

Runnery pre Windows vyžadujú:

* Python dostupný cez `python`
* Nainštalujte najnovšiu verziu: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) alebo [novší](https://visualstudio.microsoft.com/vs/community/) so záťažou **Desktop development with C++**

Prostredie Visual Studio C++ musí poskytovať:
* `vcvars64.bat`
* `cl.exe`
* Cesty k hlavičkovým súborom a knižniciam Windows SDK

Príklady rozšírení v jazyku C++ zostavujú natívne moduly `.pyd` zo súborov `.cu` pomocou cesty `CUDAExtension` v PyTorch.