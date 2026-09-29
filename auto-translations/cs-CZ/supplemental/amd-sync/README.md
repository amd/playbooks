<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vzdálený vývoj s AMD Sync

## Přehled

**AMD Sync** promění váš notebook ve vzdálený kokpit pro AMD Ryzen™ AI Halo. Přeskočte ruční nastavování SSH, klíčů a IDE — nainstalujte AMD Sync a získejte přístup jedním kliknutím ke vzdálenému terminálu, VS Code, JupyterLab a živému dashboardu GPU/CPU/paměti na Ryzen AI Halo.

Váš lokální počítač zůstává známým prostředím; každý příkaz, notebook a model běží na Ryzen AI Halo.

> **Tip**: Tato stránka bude obsahovat veškeré nové aktualizace AMDSync.

## Co se naučíte

- Povolit SSH na Ryzen AI Halo a připojit se k němu z AMD Sync
- Spustit VS Code, Terminal, JupyterLab a Live Metrics vůči Ryzen AI Halo jedním kliknutím
- Organizovat vzdálenou práci pomocí spravovaných projektových složek AMD Sync

---

## Základní pojmy

AMD Sync má dvě strany: **klienta** (váš notebook, se spuštěnou aplikací AMD Sync) a **server** (Ryzen AI Halo, se spuštěným SSH serverem, do kterého se AMD Sync tuneluje). Vše, co spustíte z AMD Sync — VS Code, terminál, notebook — se otevře lokálně, ale spouští se na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS není podporován.

---

## Krok 1 — Povolení SSH na Ryzen AI Halo


> **Poznámka:** Ve Windows je Ryzen AI Halo dodáván s SSH serverem *ve výchozím stavu vypnutým*. Na Linuxu je dodáván se SSH serverem *ve výchozím stavu zapnutým*.

1. Na Ryzen AI Halo otevřete **AMD Ryzen™ AI Developer Center**.
2. Přejděte na kartu **Remote**.
3. Přepněte **SSH Server** do polohy zapnuto.
4. Poznamenejte si **IP Address**, **Port** a **Username** zobrazené pod **Server Information** — vložíte je do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pro Windows. Verze pro Linux může mít odlišné uživatelské rozhraní, ale podobnou funkčnost pro vzdálený přístup.

> **Tip:** AMD Sync se dotazuje na **heslo pro přihlášení do OS** daného uživatele, nikoli na heslo z Developer Center.

---

## Krok 2 — Instalace AMD Sync na klientovi

AMD Sync běží na Windows 11 a Linuxu. Stáhněte instalátor pro váš operační systém a postupujte podle níže uvedených kroků. Po instalaci klikněte na **Accept & Install** na obrazovce **Get Started** — AMD Sync se po dokončení spustí automaticky.

### Windows

[Stáhnout AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Poklikejte na `AMDSyncInstaller.exe`.
2. Klikněte na **Accept & Install**.

> Pokud se zobrazí výzva brány Windows Firewall, povolte AMD Sync síťový přístup, aby se mohla připojit k Ryzen AI Halo přes SSH.

### Linux

Klikněte na odkaz a stáhněte preferovaný formát:

| Formát | Stažení | Instalační příkaz |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center může lokálně otevřený soubor `.deb` označit jako *„Potenciálně nebezpečný."* Jde o standardní varování pro jakýkoli lokální instalátor třetí strany. Pokud poklikání na `.deb` selže, použijte výše uvedený terminálový příkaz.

---

## Krok 3 — Připojení k vašemu Ryzen AI Halo

Při prvním spuštění zobrazí AMD Sync formulář **Add a Remote Device**. Vyplňte jej pomocí hodnot z karty **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(volitelné)* | Přátelský název, například `Ryzen AI Halo`. Výchozí hodnota je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z karty Remote |
| **SSH Port** | Z karty Remote (pouze čísla) |
| **Username** | Název vašeho OS účtu na Ryzen AI Halo |
| **Password** | Heslo pro přihlášení do OS — během psaní je maskováno |

Klikněte na **Add Device**. Po krátké obrazovce načítání se zobrazí zpráva **„Connection Successful"** a otevře se domovské zobrazení, které se nachází v systémové liště. Kliknutím mimo okno jej skryjete; AMD Sync zůstává spuštěná a je vzdálená jen jedno kliknutí.

> **Pokud připojení selže,** AMD Sync se vrátí do formuláře se zachovanými hodnotami. Obvyklými příčinami jsou vypnuté SSH na Ryzen AI Halo, nesprávné heslo nebo skutečnost, že se obě zařízení nacházejí v odlišných sítích.

---

## Krok 4 — Spuštění vašeho prvního vzdáleného nástroje

Domovské zobrazení nabízí pět komponent spustitelných jedním kliknutím — všechny jsou dostupné bez ohledu na to, jaký operační systém běží na klientovi a na Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Co dělá |
|-----------|--------------|
| **Directory** | Vybere složku na Ryzen AI Halo, ve které se otevřou VS Code, Terminal a JupyterLab. Výchozí hodnota je spravovaný pracovní prostor `Documents/AMD_Sync`. |
| **VS Code** | Otevře VS Code lokálně s SSH tunelem do vybrané složky. |
| **Terminal** | Otevře lokální terminál připojený přes SSH k Ryzen AI Halo, ve vybrané složce. |
| **JupyterLab** | Spustí projekt notebooku připojený přes SSH k Ryzen AI Halo, omezený na vybranou složku. |
| **Live Metrics** | Zobrazení využití GPU, paměti a CPU na Ryzen AI Halo v reálném čase. |

### Vyzkoušejte VS Code

Pro první spuštění vyzkoušejte **VS Code**.

1. Ponechte **Directory** na výchozí hodnotě `~/Documents/AMD_Sync`.
2. Klikněte na **VS Code**.
3. AMD Sync vytvoří `Documents/AMD_Sync/Project_1` na Ryzen AI Halo a otevře VS Code lokálně, tunelovaně do této složky.

Nyní upravujete soubory, které se nacházejí na Ryzen AI Halo, pomocí vašeho lokálního nastavení VS Code. Vytvořte soubor `helloworld.py`, přidejte `print("hello world")`, otevřete integrovaný terminál (`` Ctrl + ` ``) a spusťte jej:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový řádek zobrazuje **SSH: Linux** — důkaz, že váš kód běží na Ryzen AI Halo, nikoli na vašem notebooku.
### Vyzkoušejte Terminál

Klikněte na **Terminal** a přes SSH se dostanete do stejné složky bez nutnosti opustit klávesnici.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Ve Windows je výchozím terminálem **PowerShell** — pokud preferujete jiný, přepněte na **Windows Command Prompt** v nabídce Settings. V Linuxu AMD Sync používá váš výchozí systémový terminál.

---

## Jak funguje adresář

Rozbalovací nabídka **Directory** je nejdůležitější ovládací prvek v AMD Sync — určuje, kam se na Ryzen AI Halo umístí každý nástroj, který spustíte.

- **`~/Documents/AMD_Sync` (výchozí)** — Spuštění VS Code nebo JupyterLab odsud automaticky vytvoří novou projektovou složku (`Project_1`, `Project_2`, … pro VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pro JupyterLab).
- **Existující projektové složky** — V rozbalovací nabídce se zobrazí každá přímá podsložka `AMD_Sync` (včetně složek, které ručně vytvoříte na Ryzen AI Halo). Naposledy použitá složka se příště stane výchozí.
- **Vlastní cesty** — Zadejte libovolnou absolutní cestu pro otevření složky kdekoli jinde na Ryzen AI Halo. AMD Sync ji pouze *otevře* — nevytváří složky mimo `AMD_Sync` a vlastní cesty se mezi relacemi neukládají.

Pokud vlastní cesta nefunguje, AMD Sync vám sdělí důvod: neplatná syntaxe, složka neexistuje, nebo cesta odkazuje na soubor.

---

## Live Metrics a JupyterLab

- **Live Metrics** — Živý přehled využití GPU, paměti a CPU. Nejrychlejší způsob, jak ověřit, že vzdálený trénovací běh skutečně zatěžuje hardware.
- **JupyterLab** — Kompletní notebookový projekt připojený přes SSH k Ryzen AI Halo, s vlastním integrovaným terminálem pro kombinování buněk notebooku a shellových příkazů bez nutnosti opustit uživatelské rozhraní.

---

## Nastavení a více zařízení

Nabídka **Settings** má tři karty:

| Karta | Co obsahuje |
|-----|----------------|
| **Devices** | Seznam všech Ryzen AI Halo zařízení, ke kterým jste se úspěšně připojili. Znovu se připojte, upravte přihlašovací údaje nebo přidejte nové zařízení. |
| **Information** | Odkazy na dokumentaci a podporu na fóru. |
| **Customize** | Změna umístění aplikace na ploše, přepnutí typu terminálu (pouze Windows) a kontrola aktualizací AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte mezi **PowerShell** (výchozí) a **Windows Command Prompt**.
- **Typ terminálu (Linux)** — K dispozici je pouze výchozí systémový terminál.
- **Aktualizace aplikace** — Tato karta je správným místem pro kontrolu a instalaci nových verzí AMD Sync přímo z uživatelského rozhraní; není potřeba žádný samostatný aktualizátor.

> Zařízení se v sekci **Devices** zobrazí až po úspěšném prvním připojení, takže neúspěšné pokusy seznam nezaplní.

---

## Řešení problémů

- **Připojení okamžitě selže** — Ověřte, že je na kartě **Remote** v Developer Center na Ryzen AI Halo povolen SSH server.
- **Chyba nesprávného hesla** — Použijte **přihlašovací heslo k operačnímu systému** na Ryzen AI Halo, ne hesla z Developer Center.
- **Tlačítko VS Code nic nedělá** — Nainstalujte VS Code na svém klientském počítači z [code.visualstudio.com](https://code.visualstudio.com).
- **Chybí ikona AMD Sync v panelu (Linux/GNOME)** — Nainstalujte a povolte rozšíření AppIndicator.
- **Soubor `.deb` se neotevře ze správce souborů** — Použijte `sudo apt install ./AMDSyncInstaller.deb` v terminálu.
- **Nastavení se znovu objevuje při každém spuštění (Linux)**: odemkněte svou přihlašovací klíčenku, nebo spusťte s parametrem `--password-store=gnome-libsecret`, poté ještě jednou proveďte nastavení.

---