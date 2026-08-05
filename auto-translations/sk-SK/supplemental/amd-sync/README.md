<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vzdialený vývoj s AMD Sync

## Prehľad

**AMD Sync** premení váš notebook na vzdialenú riadiacu jednotku pre AMD Ryzen™ AI Halo. Preskočte manuálne nastavovanie SSH, kľúčov a IDE — nainštalujte AMD Sync a získajte jedným kliknutím prístup k vzdialenému terminálu, VS Code, JupyterLab a živému prehľadu GPU/CPU/pamäte na Ryzen AI Halo.

Váš lokálny počítač zostáva vám dobre známy; každý príkaz, notebook a model sa spúšťa na Ryzen AI Halo.

> **Tip**: Táto stránka bude obsahovať akékoľvek nové aktualizácie AMDSync.

## Čo sa naučíte

- Povoliť SSH na Ryzen AI Halo a pripojiť sa k nemu z AMD Sync
- Spustiť VS Code, Terminal, JupyterLab a Live Metrics voči Ryzen AI Halo jedným kliknutím
- Organizovať vzdialenú prácu pomocou spravovaných priečinkov projektov v AMD Sync

---

## Základné koncepty

AMD Sync má dve strany: **klienta** (váš notebook, na ktorom beží aplikácia AMD Sync) a **server** (Ryzen AI Halo, na ktorom beží SSH server, do ktorého sa AMD Sync tuneluje). Všetko, čo spustíte z AMD Sync — VS Code, terminál, notebook — sa otvára lokálne, ale vykonáva sa na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS nie je podporovaný.

---

## Krok 1 — Povoľte SSH na Ryzen AI Halo


> **Poznámka:** Na Windows sa Ryzen AI Halo dodáva s SSH serverom *predvolene vypnutým*. Na Linuxe sa dodáva s SSH serverom *predvolene zapnutým*.

1. Na Ryzen AI Halo otvorte **AMD Ryzen™ AI Developer Center**.
2. Prejdite na kartu **Remote**.
3. Zapnite prepínač **SSH Server**.
4. Poznačte si **IP Address**, **Port** a **Username** zobrazené v časti **Server Information** — tieto hodnoty vložíte do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pre Windows. Verzia pre Linux môže mať iné používateľské rozhranie, no podobnú funkcionalitu vzdialeného prístupu.

> **Tip:** AMD Sync sa pýta na **prihlasovacie heslo do OS** daného používateľa, nie na heslo z Developer Center.

---

## Krok 2 — Nainštalujte AMD Sync na svojom klientovi

AMD Sync beží na Windows 11 a Linuxe. Stiahnite si inštalátor pre svoj operačný systém a postupujte podľa nasledujúcich krokov. Po inštalácii kliknite na **Accept & Install** na obrazovke **Get Started** — AMD Sync sa po dokončení spustí automaticky.

### Windows

[Stiahnuť AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvakrát kliknite na `AMDSyncInstaller.exe`.
2. Kliknite na **Accept & Install**.

> Ak vás vyzve Windows Firewall, povoľte AMD Sync prístup k sieti, aby sa mohol pripojiť k Ryzen AI Halo cez SSH.

### Linux

Kliknite na odkaz a stiahnite si preferovaný formát:

| Formát | Stiahnutie | Inštalačný príkaz |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center môže lokálne otvorený súbor `.deb` označiť ako *„Potenciálne nebezpečný."* Ide o štandardné upozornenie pri akomkoľvek lokálne spustenom inštalátore od tretej strany. Ak dvojklik na `.deb` zlyhá, použite vyššie uvedený príkaz v termináli.

---

## Krok 3 — Pripojte sa k svojmu Ryzen AI Halo

Pri prvom spustení zobrazí AMD Sync formulár **Add a Remote Device**. Vyplňte ho pomocou hodnôt z karty **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(voliteľné)* | Vlastný popisný názov, napríklad `Ryzen AI Halo`. Predvolene sa nastaví na `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z karty Remote |
| **SSH Port** | Z karty Remote (iba čísla) |
| **Username** | Názov vášho účtu OS na Ryzen AI Halo |
| **Password** | Vaše prihlasovacie heslo do OS — pri písaní zamaskované |

Kliknite na **Add Device**. Po krátkom načítaní sa zobrazí hlásenie **„Connection Successful"** a prejdete na domovské zobrazenie, ktoré sa nachádza v systémovej lište. Kliknutím mimo okna ho zavriete; AMD Sync zostáva spustený a je vzdialený len jedno kliknutie.

> **Ak sa pripojenie nepodarí,** AMD Sync sa vráti na formulár so zachovanými zadanými hodnotami. Bežnými príčinami sú vypnuté SSH na Ryzen AI Halo, nesprávne heslo alebo skutočnosť, že sa oba zariadenia nachádzajú v odlišných sieťach.

---

## Krok 4 — Spustite svoj prvý vzdialený nástroj

Domovské zobrazenie vám ponúka päť komponentov spustiteľných jedným kliknutím — všetky dostupné bez ohľadu na to, aký operačný systém beží na klientovi a na Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Čo robí |
|-----------|--------------|
| **Directory** | Vyberá priečinok na Ryzen AI Halo, v ktorom sa otvorí VS Code, Terminal a JupyterLab. Predvolene ide o spravovaný pracovný priestor `Documents/AMD_Sync`. |
| **VS Code** | Otvorí VS Code lokálne s SSH tunelom do vybraného priečinka. |
| **Terminal** | Otvorí lokálny terminál pripojený cez SSH k Ryzen AI Halo, vo vybranom priečinku. |
| **JupyterLab** | Spustí projekt s notebookom pripojený cez SSH k Ryzen AI Halo, obmedzený na vybraný priečinok. |
| **Live Metrics** | Zobrazenie využitia GPU, pamäte a CPU na Ryzen AI Halo v reálnom čase. |

### Vyskúšajte VS Code

Pri prvom spustení vyskúšajte **VS Code**.

1. Ponechajte **Directory** na predvolenej hodnote `~/Documents/AMD_Sync`.
2. Kliknite na **VS Code**.
3. AMD Sync vytvorí `Documents/AMD_Sync/Project_1` na Ryzen AI Halo a otvorí VS Code lokálne, tunelovaný do tohto priečinka.

Teraz upravujete súbory, ktoré sa nachádzajú na Ryzen AI Halo, pomocou svojho lokálneho nastavenia VS Code. Vytvorte `helloworld.py`, pridajte `print("hello world")`, otvorte integrovaný terminál (`` Ctrl + ` ``) a spustite ho:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový riadok zobrazuje **SSH: Linux** — dôkaz, že váš kód beží na Ryzen AI Halo, nie na vašom notebooku.
### Vyskúšajte Terminál

Kliknite na tlačidlo **Terminál**, aby ste sa cez SSH dostali do rovnakého priečinka bez toho, aby ste museli opustiť klávesnicu.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Vo Windows je predvoleným terminálom **PowerShell** — ak preferujete iný, prepnite na **Windows Command Prompt** v ponuke Settings. V systéme Linux používa AMD Sync váš predvolený systémový terminál.

---

## Ako funguje priečinok Directory

Rozbaľovacia ponuka **Directory** je jediný najdôležitejší ovládací prvok v aplikácii AMD Sync — určuje, kam sa umiestni každý nástroj, ktorý spustíte na zariadení Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (predvolené)** — Spustenie VS Code alebo JupyterLab odtiaľto automaticky vytvorí nový priečinok projektu (`Project_1`, `Project_2`, … pre VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pre JupyterLab).
- **Existujúce priečinky projektov** — V rozbaľovacej ponuke sa zobrazí každý priamy podpriečinok `AMD_Sync` (vrátane priečinkov, ktoré manuálne vytvoríte na zariadení Ryzen AI Halo). Naposledy použitý priečinok sa nastaví ako predvolený pri ďalšom spustení.
- **Vlastné cesty** — Zadaním ľubovoľnej absolútnej cesty otvoríte priečinok kdekoľvek inde na zariadení Ryzen AI Halo. AMD Sync ho iba *otvorí* — nevytvára priečinky mimo `AMD_Sync` a vlastné cesty sa medzi jednotlivými reláciami neukladajú.

Ak vlastná cesta nefunguje, AMD Sync vám oznámi prečo: neplatná syntax, priečinok neexistuje alebo cesta smeruje na súbor.

---

## Live Metrics a JupyterLab

- **Live Metrics** — Živý prehľad zobrazujúci využitie GPU, pamäte a CPU. Najrýchlejší spôsob, ako potvrdiť, že vzdialený tréningový beh skutočne zaťažuje hardvér.
- **JupyterLab** — Plnohodnotný notebookový projekt pripojený cez SSH k zariadeniu Ryzen AI Halo, s vlastným integrovaným terminálom na kombinovanie buniek notebooku a príkazov shellu bez opustenia používateľského rozhrania.

---

## Nastavenia a viacero zariadení

Ponuka **Settings** má tri karty:

| Karta | Čo pokrýva |
|-----|----------------|
| **Devices** | Zoznam všetkých zariadení Ryzen AI Halo, ku ktorým ste sa úspešne pripojili. Opätovné pripojenie, úprava prihlasovacích údajov alebo pridanie nového zariadenia. |
| **Information** | Odkazy na dokumentáciu a podporu na fóre. |
| **Customize** | Zmena umiestnenia aplikácie na ploche, prepnutie typu terminálu (iba Windows) a kontrola aktualizácií AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte medzi **PowerShell** (predvolené) a **Windows Command Prompt**.
- **Typ terminálu (Linux)** — K dispozícii je iba predvolený systémový terminál.
- **Aktualizácie aplikácie** — Táto karta je správnym miestom na kontrolu a inštaláciu nových verzií AMD Sync priamo z používateľského rozhrania; samostatný aktualizačný nástroj nie je potrebný.

> Zariadenie sa v sekcii **Devices** zobrazí až po úspešnom prvom pripojení, takže neúspešné pokusy zoznam nezaneprazdnia.

---

## Riešenie problémov

- **Pripojenie okamžite zlyhá** — Skontrolujte, či je SSH server povolený na karte **Remote** v Developer Center zariadenia Ryzen AI Halo.
- **Chyba nesprávneho hesla** — Použite svoje **prihlasovacie heslo operačného systému** na zariadení Ryzen AI Halo, nie heslá prevzaté z Developer Center.
- **Tlačidlo VS Code nič nerobí** — Nainštalujte si VS Code na svoj klientský počítač zo stránky [code.visualstudio.com](https://code.visualstudio.com).
- **Chýbajúca ikona AMD Sync v systémovej lište (Linux/GNOME)** — Nainštalujte a povoľte rozšírenie AppIndicator.
- **Súbor `.deb` sa neotvorí zo správcu súborov** — Použite príkaz `sudo apt install ./AMDSyncInstaller.deb` v termináli.

---