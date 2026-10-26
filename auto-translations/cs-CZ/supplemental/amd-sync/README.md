<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vzdálený vývoj pomocí AMD Sync

## Přehled

**AMD Sync** promění váš notebook ve vzdálený kokpit pro AMD Ryzen™ AI Halo. Vynechte ruční nastavení SSH, klíčů a IDE — nainstalujte AMD Sync a získejte přístup jedním kliknutím ke vzdálenému terminálu, VS Code, JupyterLab a živému dashboardu GPU/CPU/paměti na Ryzen AI Halo.

Váš lokální počítač zůstává stejný; každý příkaz, notebook a model běží na Ryzen AI Halo.

> **Tip**: Tato stránka bude obsahovat jakékoli nové aktualizace AMDSync. 

## Co se naučíte

- Jak povolit SSH na Ryzen AI Halo a připojit se k němu z AMD Sync
- Jak jedním kliknutím spustit VS Code, Terminal, JupyterLab a Live Metrics proti Ryzen AI Halo
- Jak organizovat vzdálenou práci pomocí spravovaných složek projektů v AMD Sync

---

## Základní koncepty

AMD Sync má dvě strany: **klienta** (váš notebook se spuštěnou aplikací AMD Sync) a **server** (Ryzen AI Halo se spuštěným SSH serverem, do kterého se AMD Sync tuneluje). Vše, co spustíte z AMD Sync — VS Code, terminál, notebook — se otevře lokálně, ale provádí se na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS není podporován.

---

## Krok 1 — Povolení SSH na Ryzen AI Halo


> **Poznámka:** Na Windows je u Ryzen AI Halo SSH server *ve výchozím nastavení vypnutý*. Na Linuxu je SSH server *ve výchozím nastavení zapnutý*.

1. Na Ryzen AI Halo otevřete **AMD Ryzen™ AI Developer Center**.
2. Přejděte na kartu **Remote**.
3. Zapněte přepínač **SSH Server**.
4. Poznamenejte si **IP Address**, **Port** a **Username** uvedené v sekci **Server Information** — tyto údaje vložíte do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pro Windows. Linuxová verze může mít jiné uživatelské rozhraní, ale podobnou funkcionalitu pro vzdálený přístup.

> **Tip:** AMD Sync požaduje **heslo pro přihlášení do OS** daného uživatele, nikoli heslo z Developer Center.

---

## Krok 2 — Instalace AMD Sync na klientovi

AMD Sync běží na Windows 11 a Linuxu. Stáhněte si instalátor pro svůj operační systém a postupujte podle níže uvedených kroků. Po instalaci klikněte na obrazovce **Get Started** na tlačítko **Accept & Install** — AMD Sync se po dokončení automaticky spustí.

### Windows

[Stáhnout AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvakrát klikněte na `AMDSyncInstaller.exe`.
2. Klikněte na **Accept & Install**.

> Pokud se zobrazí výzva Windows Firewall, povolte AMD Sync síťový přístup, aby se mohl dostat k Ryzen AI Halo přes SSH.

### Linux

Klikněte na odkaz a stáhněte si preferovaný formát:

| Formát | Stažení | Instalační příkaz |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center může lokálně otevřený soubor `.deb` označit jako *„Potenciálně nebezpečný."* Jde o standardní varování pro jakýkoli instalátor třetí strany spuštěný lokálně. Pokud dvojklik na `.deb` selže, použijte výše uvedený příkaz v terminálu.

---

## Krok 3 — Připojení k vašemu Ryzen AI Halo

Při prvním spuštění zobrazí AMD Sync formulář **Add a Remote Device**. Vyplňte jej pomocí hodnot z karty **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(volitelné)* | Popisný název, například `Ryzen AI Halo`. Výchozí hodnota je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z karty Remote |
| **SSH Port** | Z karty Remote (pouze čísla) |
| **Username** | Název vašeho uživatelského účtu OS na Ryzen AI Halo |
| **Password** | Vaše heslo pro přihlášení do OS — při psaní je skryté |

Klikněte na **Add Device**. Po krátkém načítání se zobrazí hláška **„Connection Successful"** a objevíte se na domovské obrazovce, která žije ve vaší systémové liště. Kliknutím mimo okno jej zavřete; AMD Sync zůstává spuštěný a je na jedno kliknutí.

> **Pokud se připojení nezdaří,** AMD Sync se vrátí na formulář se zachovanými zadanými hodnotami. Obvyklými příčinami jsou vypnuté SSH na Ryzen AI Halo, špatné heslo nebo to, že obě zařízení jsou na odlišných sítích.

---

## Krok 4 — Spuštění vašeho prvního vzdáleného nástroje

Domovská obrazovka vám nabízí pět komponent spustitelných jedním kliknutím — všechny dostupné bez ohledu na to, jaký operační systém běží na klientovi a Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Co dělá |
|-----------|--------------|
| **Directory** | Vybere složku na Ryzen AI Halo, ve které se otevřou VS Code, Terminal a JupyterLab. Výchozí hodnota je spravovaný pracovní prostor `Documents/AMD_Sync`. |
| **VS Code** | Otevře VS Code lokálně s SSH tunelem do vybrané složky. |
| **Terminal** | Otevře lokální terminál připojený přes SSH k Ryzen AI Halo, ve vybrané složce. |
| **JupyterLab** | Spustí notebookový projekt připojený přes SSH k Ryzen AI Halo, omezený na vybranou složku. |
| **Live Metrics** | Zobrazení vytížení GPU, paměti a CPU na Ryzen AI Halo v reálném čase. |

### Vyzkoušejte VS Code

Pro první spuštění vyzkoušejte **VS Code**. Následující pokyny jsou pro Linux, ale zážitek na Windows je podobný.

1. Ponechte **Directory** na výchozí hodnotě `~/Documents/AMD_Sync`.
2. Klikněte na **VS Code**.
3. AMD Sync vytvoří na Ryzen AI Halo složku `Documents/AMD_Sync/Project_1` a otevře VS Code lokálně, tunelovaně napojené na tuto složku.

Nyní upravujete soubory, které se nacházejí na Ryzen AI Halo, prostřednictvím vašeho lokálního nastavení VS Code. Vytvořte soubor `helloworld.py`, přidejte `print("hello world")`, otevřete integrovaný terminál (`` Ctrl + ` ``) a spusťte jej:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový řádek zobrazuje **SSH: Linux** — důkaz, že váš kód běží na Ryzen AI Halo, nikoli na vašem notebooku.
### Vyzkoušejte terminál

Klikněte na **Terminál** a přes SSH se přesunete do stejné složky, aniž byste museli opustit klávesnici.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Ve Windows je výchozím terminálem **PowerShell** — pokud preferujete jiný, přepněte na **Příkazový řádek systému Windows** v nabídce Nastavení. V Linuxu AMD Sync používá výchozí systémový terminál.

---

## Jak funguje adresář

Rozbalovací nabídka **Adresář** je jediný nejdůležitější ovládací prvek v AMD Sync — určuje, kam se na Ryzen AI Halo umístí každý nástroj, který spustíte.

- **`~/Documents/AMD_Sync` (výchozí)** — Spuštění VS Code nebo JupyterLab odtud automaticky vytvoří novou projektovou složku (`Project_1`, `Project_2`, … pro VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pro JupyterLab).
- **Existující projektové složky** — V rozbalovací nabídce se zobrazí jakýkoli přímý podadresář složky `AMD_Sync` (včetně složek, které si na Ryzen AI Halo vytvoříte ručně). Naposledy použitá složka se příště stane výchozí.
- **Vlastní cesty** — Zadáním libovolné absolutní cesty otevřete složku kdekoli jinde na Ryzen AI Halo. AMD Sync ji pouze *otevře* — nevytváří složky mimo `AMD_Sync` a vlastní cesty se mezi relacemi neukládají.

Pokud vlastní cesta nefunguje, AMD Sync vám sdělí důvod: neplatná syntaxe, složka neexistuje, nebo cesta odkazuje na soubor.

---

## Živé metriky a JupyterLab

- **Živé metriky** — Živý přehled vytížení GPU, paměti a CPU. Nejrychlejší způsob, jak ověřit, že vzdálený trénovací běh skutečně zatěžuje hardware.
- **JupyterLab** — Kompletní notebookový projekt připojený přes SSH k Ryzen AI Halo, s vlastním integrovaným terminálem pro kombinování buněk notebooku a shellových příkazů bez nutnosti opustit uživatelské rozhraní.

---

## Nastavení a více zařízení

Nabídka **Nastavení** obsahuje tři karty:

| Karta | Co obsahuje |
|-----|----------------|
| **Zařízení** | Zobrazuje všechna zařízení Ryzen AI Halo, ke kterým jste se úspěšně připojili. Umožňuje znovu se připojit, upravit přihlašovací údaje nebo přidat nové zařízení. |
| **Informace** | Odkazy na dokumentaci a podporu na fóru. |
| **Přizpůsobit** | Přemístění aplikace na ploše, přepnutí typu terminálu (pouze Windows) a kontrola aktualizací AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte mezi **PowerShell** (výchozí) a **Příkazovým řádkem systému Windows**.
- **Typ terminálu (Linux)** — K dispozici je pouze výchozí systémový terminál.
- **Aktualizace aplikace** — Na této kartě můžete přímo z uživatelského rozhraní zkontrolovat a nainstalovat nové verze AMD Sync; samostatný aktualizační nástroj není potřeba.

> Zařízení se v sekci **Zařízení** zobrazí až po úspěšném prvním připojení, takže neúspěšné pokusy seznam nezaplní.

---

## Řešení problémů

- **Připojení okamžitě selže** — Ověřte, že je na kartě **Remote** v Developer Center na Ryzen AI Halo povolen SSH server.
- **Chyba nesprávného hesla** — Použijte **přihlašovací heslo operačního systému** na Ryzen AI Halo, nikoli hesla převzatá z Developer Center.
- **Tlačítko VS Code nereaguje** — Nainstalujte VS Code na svém klientském počítači z [code.visualstudio.com](https://code.visualstudio.com).
- **Chybí ikona AMD Sync v systémové liště (Linux/GNOME)** — Nainstalujte a povolte rozšíření AppIndicator.
- **Soubor `.deb` se nespustí ze správce souborů** — Použijte v terminálu `sudo apt install ./AMDSyncInstaller.deb`.
- **Nastavení se objevuje při každém spuštění (Linux)**: odemkněte přihlašovací klíčenku, nebo spusťte aplikaci s parametrem `--password-store=gnome-libsecret` a poté znovu proveďte nastavení.

---