<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjekirjan (playbook) suorittamiseen tarvittava alustan määritys.

## Vaaditut sovellukset / kehykset

| Komponentti       | Odotettu määritys               | Huomautukset                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python, jossa `venv`-tuki         | Käytetään `kernel-env`-ympäristön luomiseen ja aktivointiin                                     |
| ROCm Python SDK | ROCm 7.13 -pakettiperhe             | Asennetaan ohjekirjan riippuvuusprosessin kautta                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vaaditaan `torch.cuda`-toimintoa, HIP-ajoaikaa, JIT-kääntämistä ja `CUDAExtension`-toimintoa varten |
| GPU-ajuri      | AMD GPU -ajuri, jossa ROCm/HIP-tuki | Vaaditaan ennen kuin PyTorch voi havaita AMD GPU:n                               |

> Huomautus: Jos käytät AMD Ryzen™ AI Halo Developer Platform -alustaa, AMD ROCm™ -ohjelmisto ja PyTorch on esiasennettu.

## Linux-esivaatimukset

Seuraavat järjestelmäpaketit vaaditaan:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` vaaditaan `kernel-env`-ympäristön luomiseen.
* `build-essential`, `gcc` ja `g++` vaaditaan C++-laajennusten läpikäyntejä varten.
* `amd-smi`-työkalua käytetään Linuxin GPU-näkyvyyden/käyttöasteen tarkistuksiin.

C++-laajennusesimerkit rakentavat natiiveja `.so`-moduuleja `.cu`-tiedostoista käyttäen PyTorchin `CUDAExtension`-polkua.

## Windows-esivaatimukset

Windows-ajoympäristöt vaativat:

* Python käytettävissä `python`-komennolla
* Asenna uusin: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) tai [uudempi](https://visualstudio.microsoft.com/vs/community/), jossa on **Desktop development with C++** -työkuorma

Visual Studion C++-ympäristön on tarjottava:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK:n sisällyspolut ja kirjastopolut

C++-laajennusesimerkit rakentavat natiiveja `.pyd`-moduuleja `.cu`-tiedostoista käyttäen PyTorchin `CUDAExtension`-polkua.