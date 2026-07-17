<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan tämän playbook-kokonaisuuden suorittamiseen tarvittava alustan konfigurointi.

## Vaaditut sovellukset / kehykset

| Komponentti     | Odotettu konfigurointi               | Huomiot                                                                      |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python `venv`-tuella               | Käytetään `kernel-env`-ympäristön luomiseen ja aktivointiin                  |
| ROCm Python SDK | ROCm 7.13 -pakettiperhe              | Asennetaan playbook-riippuvuusvirran kautta                                  |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vaaditaan `torch.cuda`-toimintoa, HIP-ajonaikaista ympäristöä, JIT-kääntämistä ja `CUDAExtension`-laajennusta varten |
| GPU-ajuri       | AMD GPU -ajuri ROCm/HIP-tuella       | Vaaditaan ennen kuin PyTorch voi havaita AMD GPU:n                           |

> Huomio: Jos käytät AMD Ryzen™ AI Halo Developer Platform -alustaa, AMD ROCm™ -ohjelmisto ja PyTorch ovat valmiiksi asennettuna.

## Linux-edellytykset

Seuraavat järjestelmäpaketit vaaditaan:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` vaaditaan `kernel-env`-ympäristön luomiseen.
* `build-essential`, `gcc` ja `g++` vaaditaan C++-laajennusten läpikäyntiä varten.
* `amd-smi` käytetään Linux GPU:n näkyvyyden ja käyttöasteen tarkistuksiin.

C++-laajennusesimerkit rakentavat natiiveja `.so`-moduuleja `.cu`-tiedostoista käyttäen PyTorchin `CUDAExtension`-polkua.

## Windows-edellytykset

Windows-suoritusympäristöt vaativat:

* Pythonin saatavuuden `python`-komennon kautta
* Asenna uusin versio: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) tai [uudempi](https://visualstudio.microsoft.com/vs/community/) **Desktop development with C++** -työkuormalla

Visual Studio C++ -ympäristön on tarjottava:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK:n sisällytys- ja kirjastopolut

C++-laajennusesimerkit rakentavat natiiveja `.pyd`-moduuleja `.cu`-tiedostoista käyttäen PyTorchin `CUDAExtension`-polkua.