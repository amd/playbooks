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

# Vzdialený vývoj pomocou AMD Sync

## Prehľad

**AMD Sync** premení váš notebook na vzdialený kokpit pre AMD Ryzen™ AI Halo. Preskočte manuálne nastavovanie SSH, kľúčov a IDE — nainštalujte AMD Sync a získajte prístup jedným kliknutím k vzdialenému terminálu, VS Code, JupyterLab a živému dashboardu GPU/CPU/pamäte na Ryzen AI Halo.

Váš lokálny počítač zostáva taký, na aký ste zvyknutí; každý príkaz, notebook a model beží na Ryzen AI Halo.

> **Tip**: Táto stránka bude obsahovať všetky nové aktualizácie AMDSync. 

## Čo sa naučíte

- Povoliť SSH na Ryzen AI Halo a pripojiť sa k nemu z AMD Sync
- Spustiť VS Code, Terminal, JupyterLab a Live Metrics proti Ryzen AI Halo jedným kliknutím
- Organizovať vzdialenú prácu pomocou spravovaných priečinkov projektov AMD Sync

---

## Základné koncepty

AMD Sync má dve strany: **klienta** (váš notebook, na ktorom beží aplikácia AMD Sync) a **server** (Ryzen AI Halo, na ktorom beží SSH server, do ktorého AMD Sync vytvára tunel). Všetko, čo spustíte z AMD Sync — VS Code, terminál, notebook — sa otvorí lokálne, ale vykonáva sa na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS nie je podporovaný.

---

## Krok 1 — Povolenie SSH na Ryzen AI Halo


> **Poznámka:** Na Windows sa Ryzen AI Halo dodáva s SSH serverom *predvolene vypnutým*. Na Linuxe sa dodáva s SSH serverom *predvolene zapnutým*.

1. Na Ryzen AI Halo otvorte **AMD Ryzen™ AI Developer Center**.
2. Prejdite na kartu **Remote**.
3. Zapnite prepínač **SSH Server**.
4. Poznačte si **IP Address**, **Port** a **Username** zobrazené v časti **Server Information** — tieto údaje vložíte do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pre Windows. Verzia pre Linux môže mať odlišné rozhranie, ale podobnú funkcionalitu pre vzdialený prístup.

> **Tip:** AMD Sync vyžaduje **prihlasovacie heslo OS** daného používateľa, nie heslo z Developer Center.

---

## Krok 2 — Inštalácia AMD Sync na vašom klientovi

AMD Sync beží na Windows 11 a Linux. Stiahnite si inštalátor pre váš operačný systém a postupujte podľa nasledujúcich krokov. Po inštalácii kliknite na **Accept & Install** na obrazovke **Get Started** — AMD Sync sa po dokončení automaticky spustí.

### Windows

[Stiahnuť AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvakrát kliknite na `AMDSyncInstaller.exe`.
2. Kliknite na **Accept & Install**.

> Ak sa zobrazí výzva od Windows Firewall, povoľte AMD Sync prístup k sieti, aby sa mohol pripojiť k Ryzen AI Halo cez SSH.

### Linux

Kliknite na odkaz na stiahnutie preferovaného formátu:

| Formát | Stiahnutie | Inštalačný príkaz |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center môže lokálne otvorený súbor `.deb` označiť ako *"Potenciálne nebezpečný."* Ide o štandardné upozornenie pre akýkoľvek lokálny inštalátor od tretej strany. Ak dvojklik na `.deb` zlyhá, použite vyššie uvedený príkaz v termináli.

---

## Krok 3 — Pripojenie k vášmu Ryzen AI Halo

Pri prvom spustení zobrazí AMD Sync formulár **Add a Remote Device**. Vyplňte ho pomocou hodnôt z karty **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(voliteľné)* | Prívetivé označenie ako `Ryzen AI Halo`. Predvolene `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z karty Remote |
| **SSH Port** | Z karty Remote (iba čísla) |
| **Username** | Názov vášho používateľského konta OS na Ryzen AI Halo |
| **Password** | Vaše prihlasovacie heslo OS — počas písania je skryté |

Kliknite na **Add Device**. Po krátkej obrazovke načítavania sa zobrazí **"Connection Successful"** a dostanete sa na domovskú obrazovku, ktorá sa nachádza v systémovej lište. Kliknutím mimo okna ho zatvoríte; AMD Sync zostane spustený a je vzdialený jedno kliknutie.

> **Ak sa pripojenie nepodarí,** AMD Sync sa vráti na formulár so zachovanými hodnotami. Bežnými príčinami sú vypnuté SSH na Ryzen AI Halo, nesprávne heslo, alebo že sa obe zariadenia nachádzajú v odlišných sieťach.

---

## Krok 4 — Spustenie prvého vzdialeného nástroja

Domovská obrazovka ponúka päť komponentov dostupných jedným kliknutím — všetky sú k dispozícii bez ohľadu na to, aký operačný systém používa klient a Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Čo robí |
|-----------|--------------|
| **Directory** | Vyberie priečinok na Ryzen AI Halo, v ktorom sa otvoria VS Code, Terminal a JupyterLab. Predvolene je to spravovaný pracovný priestor `Documents/AMD_Sync`. |
| **VS Code** | Otvorí VS Code lokálne s SSH tunelom do vybraného priečinka. |
| **Terminal** | Otvorí lokálny terminál pripojený cez SSH k Ryzen AI Halo, vo vybranom priečinku. |
| **JupyterLab** | Spustí projekt notebooku pripojený cez SSH k Ryzen AI Halo, obmedzený na vybraný priečinok. |
| **Live Metrics** | Zobrazenie v reálnom čase pre využitie GPU, pamäte a CPU na Ryzen AI Halo. |

### Vyskúšajte VS Code

Pri prvom spustení vyskúšajte **VS Code**. Nasledujúce pokyny sú pre Linux, ale skúsenosť na Windows je podobná.

1. Ponechajte **Directory** na predvolenej hodnote `~/Documents/AMD_Sync`.
2. Kliknite na **VS Code**.
3. AMD Sync vytvorí `Documents/AMD_Sync/Project_1` na Ryzen AI Halo a otvorí VS Code lokálne, s tunelom do tohto priečinka.

Teraz upravujete súbory, ktoré sa nachádzajú na Ryzen AI Halo, pomocou vášho lokálneho nastavenia VS Code. Vytvorte `helloworld.py`, pridajte `print("hello world")`, otvorte integrovaný terminál (`` Ctrl + ` ``) a spustite ho:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový riadok zobrazuje **SSH: Linux** — dôkaz, že váš kód beží na Ryzen AI Halo, nie na vašom notebooku.
### Vyskúšajte terminál

Kliknite na **Terminál**, aby ste sa ocitli v rovnakom priečinku cez SSH bez toho, aby ste museli opustiť klávesnicu.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Vo Windows je predvoleným terminálom **PowerShell** — ak preferujete iný, prepnite na **Windows Command Prompt** v ponuke Nastavenia. V systéme Linux aplikácia AMD Sync používa predvolený systémový terminál.

---

## Ako funguje Adresár

Rozbaľovacia ponuka **Adresár** je najdôležitejší ovládací prvok v AMD Sync — určuje, kam sa na Ryzen AI Halo umiestni každý spustený nástroj.

- **`~/Documents/AMD_Sync` (predvolené)** — Spustenie VS Code alebo JupyterLab z tohto miesta automaticky vytvorí nový priečinok projektu (`Project_1`, `Project_2`, … pre VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pre JupyterLab).
- **Existujúce priečinky projektov** — V rozbaľovacej ponuke sa zobrazí každý priamy podpriečinok `AMD_Sync` (vrátane priečinkov, ktoré manuálne vytvoríte na Ryzen AI Halo). Posledný použitý priečinok sa stane predvoleným pri ďalšom použití.
- **Vlastné cesty** — Zadajte ľubovoľnú absolútnu cestu na otvorenie priečinka inde na Ryzen AI Halo. AMD Sync ho iba *otvorí* — nevytvára priečinky mimo `AMD_Sync` a vlastné cesty sa medzi reláciami neukladajú.

Ak vlastná cesta nefunguje, AMD Sync vám povie prečo: neplatná syntax, priečinok neexistuje, alebo cesta smeruje na súbor.

---

## Živé metriky a JupyterLab

- **Živé metriky** — Živý prehľad využitia GPU, pamäte a CPU. Najrýchlejší spôsob, ako potvrdiť, že vzdialené trénovanie skutočne zaťažuje hardvér.
- **JupyterLab** — Plnohodnotný projekt zápisníka pripojený cez SSH k Ryzen AI Halo, s vlastným integrovaným terminálom na kombinovanie buniek zápisníka a príkazov shellu bez opustenia používateľského rozhrania.

---

## Nastavenia a viacero zariadení

Ponuka **Nastavenia** má tri karty:

| Karta | Čo pokrýva |
|-----|----------------|
| **Zariadenia** | Zoznam každého Ryzen AI Halo, s ktorým ste sa úspešne pripojili. Znova sa pripojte, upravte prihlasovacie údaje alebo pridajte nové zariadenie. |
| **Informácie** | Odkazy na dokumentáciu a podporu na fóre. |
| **Prispôsobiť** | Premiestnite aplikáciu na pracovnej ploche, prepnite typ terminálu (iba Windows) a skontrolujte aktualizácie AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte medzi **PowerShell** (predvolené) a **Windows Command Prompt**.
- **Typ terminálu (Linux)** — K dispozícii je iba predvolený systémový terminál.
- **Aktualizácie aplikácie** — Táto karta je správnym miestom na kontrolu a inštaláciu nových verzií AMD Sync priamo z používateľského rozhrania; samostatný aktualizačný nástroj nie je potrebný.

> Zariadenie sa v sekcii **Zariadenia** zobrazí až po úspešnom prvom pripojení, takže neúspešné pokusy nezaplnia zoznam.

---

## Riešenie problémov

- **Pripojenie okamžite zlyhá** — Skontrolujte, či je na karte **Remote** v Developer Center na Ryzen AI Halo povolený SSH server.
- **Chyba nesprávneho hesla** — Použite svoje **prihlasovacie heslo OS** na Ryzen AI Halo, nie heslá prevzaté z Developer Center.
- **Tlačidlo VS Code nereaguje** — Nainštalujte VS Code na vašom klientskom zariadení z [code.visualstudio.com](https://code.visualstudio.com).
- **Chýbajúca ikona AMD Sync v systémovej lište (Linux/GNOME)** — Nainštalujte a povoľte rozšírenie AppIndicator.
- **Súbor `.deb` sa neotvorí zo správcu súborov** — Použite príkaz `sudo apt install ./AMDSyncInstaller.deb` v termináli.
- **Nastavenie sa objavuje pri každom spustení (Linux)**: odomknite svoj prihlasovací kľúčenku (keyring), alebo spustite s `--password-store=gnome-libsecret`, a potom nastavenie znova vykonajte raz.

---