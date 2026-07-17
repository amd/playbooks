<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vzdialený vývoj s AMD Sync

## Prehľad

**AMD Sync** premení váš laptop na vzdialené ovládacie centrum pre AMD Ryzen™ AI Halo. Zabudnite na manuálne nastavovanie SSH, kľúčov a IDE — nainštalujte AMD Sync a získajte prístup na jedno kliknutie k vzdialenému terminálu, VS Code, JupyterLab a živému dashboardu GPU/CPU/pamäte na Ryzen AI Halo.

Váš lokálny počítač zostáva rovnaký; každý príkaz, notebook a model beží na Ryzen AI Halo.

> **Tip**: Táto stránka bude obsahovať všetky nové aktualizácie AMDSync.

## Čo sa naučíte

- Povoliť SSH na Ryzen AI Halo a pripojiť sa k nemu cez AMD Sync
- Spustiť VS Code, Terminal, JupyterLab a Live Metrics pre Ryzen AI Halo jedným kliknutím
- Organizovať vzdialenú prácu pomocou spravovaných projektových priečinkov AMD Sync

---

## Základné koncepty

AMD Sync má dve strany: **klient** (váš laptop, na ktorom beží aplikácia AMD Sync) a **server** (Ryzen AI Halo, na ktorom beží SSH server, do ktorého AMD Sync tuneluje). Všetko, čo spustíte z AMD Sync — VS Code, terminál, notebook — sa otvorí lokálne, ale vykonáva sa na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS nie je podporovaný.

---

## Krok 1 — Povolenie SSH na Ryzen AI Halo


> **Poznámka:** Na Windows je Ryzen AI Halo dodávaný so SSH serverom *predvolene vypnutým*. Na Linux prichádza so SSH serverom *predvolene zapnutým*.

1. Na Ryzen AI Halo otvorte **AMD Ryzen™ AI Developer Center**.
2. Prejdite na záložku **Remote**.
3. Prepnite **SSH Server** na zapnuté.
4. Poznačte si **IP adresu**, **Port** a **Používateľské meno** zobrazené v časti **Server Information** — vložíte ich do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pre Windows. Verzia pre Linux môže mať odlišné rozhranie, ale podobnú funkciu vzdialeného prístupu.

> **Tip:** AMD Sync vyžaduje **prihlasovacie heslo OS** daného používateľa, nie heslo z Developer Center.

---

## Krok 2 — Inštalácia AMD Sync na vašom klientovi

AMD Sync beží na Windows 11 a Linux. Stiahnite si inštalátor pre váš operačný systém a postupujte podľa krokov nižšie. Po inštalácii kliknite na **Accept & Install** na obrazovke **Get Started** — AMD Sync sa po dokončení spustí automaticky.

### Windows

[Stiahnuť AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvakrát kliknite na `AMDSyncInstaller.exe`.
2. Kliknite na **Accept & Install**.

> Ak vás Windows Firewall vyzve, povoľte AMD Sync prístup k sieti, aby sa mohol pripojiť k Ryzen AI Halo cez SSH.

### Linux

Kliknite na odkaz a stiahnite si preferovaný formát:

| Formát | Stiahnutie | Príkaz na inštaláciu |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center môže označiť lokálne otvorený súbor `.deb` ako *„Potenciálne nebezpečný."* Toto je štandardné upozornenie pre akýkoľvek lokálny inštalátor tretej strany. Ak dvojité kliknutie na `.deb` zlyhá, použite príkaz v termináli uvedený vyššie.

---

## Krok 3 — Pripojenie k vášmu Ryzen AI Halo

Pri prvom spustení AMD Sync zobrazí formulár **Add a Remote Device**. Vyplňte ho hodnotami zo záložky **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(voliteľné)* | Priateľský názov, napríklad `Ryzen AI Halo`. Predvolene `Device 1`, `Device 2`, … |
| **Hostname or IP** | Zo záložky Remote |
| **SSH Port** | Zo záložky Remote (iba čísla) |
| **Username** | Názov vášho OS účtu na Ryzen AI Halo |
| **Password** | Vaše prihlasovacie heslo OS — pri písaní je maskované |

Kliknite na **Add Device**. Po krátkom načítavaní uvidíte **„Connection Successful"** a ocitnete sa na domovskom zobrazení, ktoré sa nachádza v systémovej lište. Kliknutím mimo okna ho zatvoríte; AMD Sync zostáva spustený a je dostupný jedným kliknutím.

> **Ak sa pripojenie nepodarí,** AMD Sync sa vráti na formulár so zachovanými hodnotami. Bežné príčiny sú: SSH je vypnuté na Ryzen AI Halo, nesprávne heslo alebo oba zariadenia sú v rôznych sieťach.

---

## Krok 4 — Spustenie prvého vzdialeného nástroja

Domovské zobrazenie vám ponúka päť komponentov na jedno kliknutie — všetky sú dostupné bez ohľadu na to, aký OS beží na klientovi a Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Čo robí |
|-----------|--------------|
| **Directory** | Vyberie priečinok na Ryzen AI Halo, v ktorom sa VS Code, Terminal a JupyterLab otvoria. Predvolene spravovaný pracovný priestor `Documents/AMD_Sync`. |
| **VS Code** | Otvorí VS Code lokálne s SSH tunelom do vybraného priečinka. |
| **Terminal** | Otvorí lokálny terminál pripojený cez SSH k Ryzen AI Halo, vo vybranom priečinku. |
| **JupyterLab** | Spustí notebookový projekt pripojený cez SSH k Ryzen AI Halo, obmedzený na vybraný priečinok. |
| **Live Metrics** | Zobrazenie GPU, pamäte a využitia CPU na Ryzen AI Halo v reálnom čase. |

### Vyskúšajte VS Code

Pri prvom spustení vyskúšajte **VS Code**.

1. Nechajte **Directory** na predvolenom `~/Documents/AMD_Sync`.
2. Kliknite na **VS Code**.
3. AMD Sync vytvorí `Documents/AMD_Sync/Project_1` na Ryzen AI Halo a otvorí VS Code lokálne, s tunelom do tohto priečinka.

Teraz upravujete súbory, ktoré sa nachádzajú na Ryzen AI Halo, pomocou vášho lokálneho nastavenia VS Code. Vytvorte `helloworld.py`, pridajte `print("hello world")`, otvorte integrovaný terminál (`` Ctrl + ` ``) a spustite ho:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový riadok zobrazuje **SSH: Linux** — dôkaz, že váš kód beží na Ryzen AI Halo, nie na vašom laptope.

### Vyskúšajte terminál

Kliknite na **Terminal** a prejdite do rovnakého priečinka cez SSH bez toho, aby ste opustili klávesnicu.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Na Windows je predvolený terminál **PowerShell** — v ponuke Nastavenia prepnite na **Windows Command Prompt**, ak preferujete. Na Linux AMD Sync používa váš predvolený systémový terminál.

---

## Ako funguje Directory

Rozbaľovací zoznam **Directory** je najdôležitejší ovládací prvok v AMD Sync — určuje, kde na Ryzen AI Halo sa každý spustený nástroj otvorí.

- **`~/Documents/AMD_Sync` (predvolené)** — Spustenie VS Code alebo JupyterLab odtiaľto automaticky vytvorí nový projektový priečinok (`Project_1`, `Project_2`, … pre VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pre JupyterLab).
- **Existujúce projektové priečinky** — Každý priamy podpriečinok `AMD_Sync` (vrátane priečinkov, ktoré ručne vytvoríte na Ryzen AI Halo) sa zobrazí v rozbaľovacom zozname. Posledný použitý priečinok sa stane predvoleným pri ďalšom spustení.
- **Vlastné cesty** — Zadajte ľubovoľnú absolútnu cestu na otvorenie priečinka kdekoľvek na Ryzen AI Halo. AMD Sync ho iba *otvorí* — nevytvorí priečinky mimo `AMD_Sync` a vlastné cesty sa medzi reláciami neukladajú.

Ak vlastná cesta nefunguje, AMD Sync vám povie prečo: neplatná syntax, priečinok neexistuje alebo cesta ukazuje na súbor.

---

## Live Metrics a JupyterLab

- **Live Metrics** — Živý dashboard využitia GPU, pamäte a CPU. Najrýchlejší spôsob, ako potvrdiť, že vzdialený tréning skutočne zaťažuje hardvér.
- **JupyterLab** — Kompletný notebookový projekt pripojený cez SSH k Ryzen AI Halo s vlastným integrovaným terminálom na kombinovanie buniek notebooku a príkazov shellu bez opustenia rozhrania.

---

## Nastavenia a viacero zariadení

Ponuka **Settings** má tri záložky:

| Záložka | Čo pokrýva |
|-----|----------------|
| **Devices** | Zobrazuje každý Ryzen AI Halo, ku ktorému ste sa úspešne pripojili. Znovu sa pripojiť, upraviť prihlasovacie údaje alebo pridať nové zariadenie. |
| **Information** | Odkazy na dokumentáciu a podporu na fóre. |
| **Customize** | Premiestnenie aplikácie na pracovnej ploche, prepnutie typu terminálu (iba Windows) a kontrola aktualizácií AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte medzi **PowerShell** (predvolené) a **Windows Command Prompt**.
- **Typ terminálu (Linux)** — K dispozícii je iba predvolený systémový terminál.
- **Aktualizácie aplikácie** — Táto záložka je správne miesto na kontrolu a inštaláciu nových verzií AMD Sync priamo z rozhrania; nie je potrebný žiadny samostatný aktualizátor.

> Zariadenie sa zobrazí v časti **Devices** až po úspešnom prvom pripojení, takže neúspešné pokusy nezaplnia zoznam.

---

## Riešenie problémov

- **Pripojenie okamžite zlyhá** — Overte, či je SSH server povolený na záložke **Remote** v Developer Center na Ryzen AI Halo.
- **Chyba nesprávneho hesla** — Použite svoje **prihlasovacie heslo OS** na Ryzen AI Halo, nie heslá z Developer Center.
- **Tlačidlo VS Code nereaguje** — Nainštalujte VS Code na váš klientský počítač z [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync v lište chýba (Linux/GNOME)** — Nainštalujte a povoľte rozšírenie AppIndicator.
- **`.deb` sa nedá otvoriť zo správcu súborov** — Použite `sudo apt install ./AMDSyncInstaller.deb` z terminálu.

---