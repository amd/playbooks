<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vzdialený vývoj s AMD Sync

## Prehľad

**AMD Sync** premení váš notebook na vzdialený riadiaci panel pre AMD Ryzen™ AI Halo. Zabudnite na manuálne nastavovanie SSH, kľúčov a IDE — nainštalujte AMD Sync a jedným kliknutím získate prístup k vzdialenému terminálu, VS Code, JupyterLab a živému dashboardu GPU/CPU/pamäte na zariadení Ryzen AI Halo.

Vaše lokálne zariadenie zostáva pre vás známe; každý príkaz, notebook a model beží na Ryzen AI Halo.

> **Tip**: Táto stránka bude obsahovať všetky nové aktualizácie AMDSync. 

## Čo sa naučíte

- Zapnúť SSH na Ryzen AI Halo a pripojiť sa k nemu z AMD Sync
- Spustiť VS Code, Terminal, JupyterLab a Live Metrics voči Ryzen AI Halo jedným kliknutím
- Organizovať vzdialenú prácu pomocou spravovaných priečinkov projektov v AMD Sync

---

## Základné koncepty

AMD Sync má dve strany: **klienta** (váš notebook, na ktorom beží aplikácia AMD Sync) a **server** (Ryzen AI Halo, na ktorom beží SSH server, do ktorého sa AMD Sync tuneluje). Všetko, čo spustíte z AMD Sync — VS Code, terminál, notebook — sa otvorí lokálne, ale vykonáva sa na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS nie je podporovaný.

---

## Krok 1 — Zapnutie SSH na Ryzen AI Halo


> **Poznámka:** Na Windows je Ryzen AI Halo dodávaný s SSH serverom *predvolene vypnutým*. Na Linuxe prichádza s SSH serverom *predvolene zapnutým*.

1. Na Ryzen AI Halo otvorte **AMD Ryzen™ AI Developer Center**.
2. Prejdite na kartu **Remote**.
3. Zapnite prepínač **SSH Server**.
4. Poznamenajte si **IP Address**, **Port** a **Username** zobrazené v časti **Server Information** — tieto údaje neskôr vložíte do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pre Windows. Linuxová verzia môže mať iné rozhranie, ale podobnú funkcionalitu vzdialeného prístupu.

> **Tip:** AMD Sync vyžaduje **prihlasovacie heslo operačného systému** daného používateľa, nie heslo z Developer Center.

---

## Krok 2 — Inštalácia AMD Sync na vašom klientovi

AMD Sync beží na Windows 11 a Linuxe. Stiahnite si inštalátor pre váš operačný systém a postupujte podľa nižšie uvedených krokov. Po inštalácii kliknite na **Accept & Install** na obrazovke **Get Started** — AMD Sync sa po dokončení automaticky spustí.

### Windows

[Stiahnuť AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvakrát kliknite na `AMDSyncInstaller.exe`.
2. Kliknite na **Accept & Install**.

> Ak sa zobrazí výzva brány Windows Firewall, povoľte AMD Sync prístup k sieti, aby sa mohol pripojiť k Ryzen AI Halo cez SSH.

### Linux

Kliknite na odkaz a stiahnite si preferovaný formát:

| Formát | Stiahnutie | Inštalačný príkaz |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center môže lokálne otvorený `.deb` súbor označiť ako *"Potenciálne nebezpečný."* Ide o štandardné upozornenie pre akýkoľvek lokálny inštalátor tretej strany. Ak dvojklik na `.deb` zlyhá, použite vyššie uvedený terminálový príkaz.

---

## Krok 3 — Pripojenie k vášmu Ryzen AI Halo

Pri prvom spustení AMD Sync zobrazí formulár **Add a Remote Device**. Vyplňte ho hodnotami z karty **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(voliteľné)* | Priateľský názov, napríklad `Ryzen AI Halo`. Predvolene `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z karty Remote |
| **SSH Port** | Z karty Remote (iba čísla) |
| **Username** | Názov vášho používateľského konta operačného systému na Ryzen AI Halo |
| **Password** | Vaše prihlasovacie heslo operačného systému — pri písaní zamaskované |

Kliknite na **Add Device**. Po krátkej obrazovke načítania sa zobrazí **"Connection Successful"** a dostanete sa na domovské zobrazenie, ktoré sídli vo vašej systémovej lište. Kliknutím mimo okna ho zatvoríte; AMD Sync zostáva spustený a je vzdialený jediné kliknutie.

> **Ak sa pripojenie nepodarí,** AMD Sync sa vráti na formulár so zachovanými hodnotami. Bežnými príčinami sú vypnuté SSH na Ryzen AI Halo, nesprávne heslo, alebo skutočnosť, že obe zariadenia sú v odlišných sieťach.

---

## Krok 4 — Spustenie vášho prvého vzdialeného nástroja

Domovské zobrazenie ponúka päť komponentov na jedno kliknutie — všetky dostupné bez ohľadu na to, aký operačný systém beží na klientovi a na Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Čo robí |
|-----------|--------------|
| **Directory** | Vyberá priečinok na Ryzen AI Halo, v ktorom sa otvoria VS Code, Terminal a JupyterLab. Predvolene ide o spravovaný pracovný priestor `Documents/AMD_Sync`. |
| **VS Code** | Otvorí VS Code lokálne s SSH tunelom do vybraného priečinka. |
| **Terminal** | Otvorí lokálny terminál pripojený cez SSH k Ryzen AI Halo, v rámci vybraného priečinka. |
| **JupyterLab** | Spustí notebookový projekt pripojený cez SSH k Ryzen AI Halo, obmedzený na vybraný priečinok. |
| **Live Metrics** | Zobrazenie využitia GPU, pamäte a CPU na Ryzen AI Halo v reálnom čase. |

### Vyskúšajte VS Code

Pri prvom spustení vyskúšajte **VS Code**.

1. Ponechajte **Directory** na predvolenej hodnote `~/Documents/AMD_Sync`.
2. Kliknite na **VS Code**.
3. AMD Sync vytvorí priečinok `Documents/AMD_Sync/Project_1` na Ryzen AI Halo a otvorí VS Code lokálne, tunelované do tohto priečinka.

Teraz upravujete súbory, ktoré sídlia na Ryzen AI Halo, pomocou vášho lokálneho nastavenia VS Code. Vytvorte súbor `helloworld.py`, pridajte `print("hello world")`, otvorte integrovaný terminál (`` Ctrl + ` ``) a spustite ho:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový riadok zobrazuje **SSH: Linux** — dôkaz, že váš kód beží na Ryzen AI Halo, nie na vašom notebooku.
### Vyskúšajte Terminál

Kliknite na **Terminál**, aby ste sa cez SSH prepli do rovnakého priečinka bez toho, aby ste museli opustiť klávesnicu.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

V systéme Windows je predvoleným terminálom **PowerShell** — ak preferujete iný, prepnite na **Windows Command Prompt** v ponuke Nastavenia. V systéme Linux používa AMD Sync váš predvolený systémový terminál.

---

## Ako funguje adresár

Rozbaľovací zoznam **Priečinok** je najdôležitejším ovládacím prvkom v AMD Sync — určuje, kam sa umiestni každý nástroj, ktorý spustíte na Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (predvolené)** — Spustenie VS Code alebo JupyterLab odtiaľto automaticky vytvorí nový priečinok projektu (`Project_1`, `Project_2`, … pre VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pre JupyterLab).
- **Existujúce priečinky projektov** — V rozbaľovacom zozname sa zobrazí každý priamy podpriečinok `AMD_Sync` (vrátane priečinkov, ktoré manuálne vytvoríte na Ryzen AI Halo). Naposledy použitý priečinok sa nabudúce stane predvoleným.
- **Vlastné cesty** — Zadaním ľubovoľnej absolútnej cesty otvoríte priečinok kdekoľvek inde na Ryzen AI Halo. AMD Sync ho iba *otvorí* — nevytvára priečinky mimo `AMD_Sync` a vlastné cesty sa medzi reláciami neukladajú.

Ak vlastná cesta nefunguje, AMD Sync vám oznámi prečo: neplatná syntax, priečinok neexistuje, alebo cesta odkazuje na súbor.

---

## Živé metriky a JupyterLab

- **Živé metriky** — Živý prehľad využitia GPU, pamäte a CPU. Najrýchlejší spôsob, ako potvrdiť, že vzdialený tréningový beh skutočne zaťažuje hardvér.
- **JupyterLab** — Kompletný notebookový projekt pripojený cez SSH k Ryzen AI Halo, s vlastným integrovaným terminálom na kombinovanie buniek notebooku a príkazov shellu bez opustenia používateľského rozhrania.

---

## Nastavenia a viacero zariadení

Ponuka **Nastavenia** má tri karty:

| Karta | Čo obsahuje |
|-----|----------------|
| **Zariadenia** | Zobrazuje zoznam všetkých Ryzen AI Halo zariadení, ku ktorým ste sa úspešne pripojili. Znova sa pripojte, upravte prihlasovacie údaje alebo pridajte nové zariadenie. |
| **Informácie** | Odkazy na dokumentáciu a podporu na fóre. |
| **Prispôsobiť** | Zmeňte pozíciu aplikácie na ploche, prepnite typ terminálu (iba Windows) a skontrolujte aktualizácie AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte medzi **PowerShell** (predvolené) a **Windows Command Prompt**.
- **Typ terminálu (Linux)** — K dispozícii je iba predvolený systémový terminál.
- **Aktualizácie aplikácie** — Táto karta je správne miesto na kontrolu a inštaláciu nových verzií AMD Sync priamo z rozhrania; samostatný nástroj na aktualizáciu nie je potrebný.

> Zariadenie sa v sekcii **Zariadenia** zobrazí až po prvom úspešnom pripojení, takže neúspešné pokusy zoznam nezapratávajú.

---

## Riešenie problémov

- **Pripojenie okamžite zlyhá** — Skontrolujte, či je na karte **Vzdialený prístup** (Remote) v Developer Center na Ryzen AI Halo povolený SSH server.
- **Chyba nesprávneho hesla** — Použite svoje **prihlasovacie heslo operačného systému** na Ryzen AI Halo, nie heslá prevzaté z Developer Center.
- **Tlačidlo VS Code nič nespraví** — Nainštalujte si VS Code na svoj klientský počítač z [code.visualstudio.com](https://code.visualstudio.com).
- **Chýba ikona AMD Sync v systémovej lište (Linux/GNOME)** — Nainštalujte a povoľte rozšírenie AppIndicator.
- **Súbor `.deb` sa neotvorí zo správcu súborov** — V termináli použite `sudo apt install ./AMDSyncInstaller.deb`.
- **Nastavenie sa opakuje pri každom spustení (Linux)**: odomknite si prihlasovací kľúčenku (keyring) alebo aplikáciu spustite s parametrom `--password-store=gnome-libsecret` a nastavenie ešte raz dokončite.

---