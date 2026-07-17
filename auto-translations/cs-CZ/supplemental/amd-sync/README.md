<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vzdálený vývoj s AMD Sync

## Přehled

**AMD Sync** promění váš laptop v dálkové ovládání pro AMD Ryzen™ AI Halo. Zapomeňte na ruční nastavování SSH, klíčů a IDE — nainstalujte AMD Sync a získejte přístup na jedno kliknutí ke vzdálenému terminálu, VS Code, JupyterLab a živému přehledu GPU/CPU/paměti na Ryzen AI Halo.

Váš lokální počítač zůstane tak, jak ho znáte; každý příkaz, notebook i model běží na Ryzen AI Halo.

> **Tip**: Tato stránka bude obsahovat veškeré nové aktualizace AMDSync.

## Co se naučíte

- Povolit SSH na Ryzen AI Halo a připojit se k němu z AMD Sync
- Spustit VS Code, Terminal, JupyterLab a Live Metrics pro Ryzen AI Halo jedním kliknutím
- Organizovat vzdálenou práci pomocí spravovaných projektových složek AMD Sync

---

## Základní koncepty

AMD Sync má dvě strany: **klient** (váš laptop se spuštěnou aplikací AMD Sync) a **server** (Ryzen AI Halo se spuštěným SSH serverem, do kterého AMD Sync vytváří tunel). Vše, co z AMD Sync spustíte — VS Code, terminál, notebook — se otevře lokálně, ale vykonává se na Ryzen AI Halo.

> **Podporovaní klienti:** Windows 11 a Linux. macOS není podporováno.

---

## Krok 1 — Povolení SSH na Ryzen AI Halo


> **Poznámka:** Na Windows je Ryzen AI Halo dodáván se SSH serverem *ve výchozím stavu vypnutým*. Na Linuxu je SSH server *ve výchozím stavu zapnutý*.

1. Na Ryzen AI Halo otevřete **AMD Ryzen™ AI Developer Center**.
2. Přejděte na záložku **Remote**.
3. Přepněte **SSH Server** do polohy zapnuto.
4. Poznamenejte si **IP adresu**, **Port** a **Uživatelské jméno** zobrazené v části **Server Information** — tyto hodnoty vložíte do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Poznámka:** Toto je AMD Developer Center pro Windows. Verze pro Linux může mít odlišné uživatelské rozhraní, ale podobnou funkci vzdáleného přístupu.

> **Tip:** AMD Sync vyžaduje **přihlašovací heslo operačního systému** daného uživatele, nikoli heslo z Developer Center.

---

## Krok 2 — Instalace AMD Sync na vašem klientovi

AMD Sync běží na Windows 11 a Linuxu. Stáhněte instalátor pro váš operační systém a postupujte podle níže uvedených kroků. Po instalaci klikněte na **Accept & Install** na obrazovce **Get Started** — AMD Sync se po dokončení spustí automaticky.

### Windows

[Stáhnout AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dvakrát klikněte na `AMDSyncInstaller.exe`.
2. Klikněte na **Accept & Install**.

> Pokud vás Windows Firewall vyzve k potvrzení, povolte AMD Sync přístup k síti, aby se mohl připojit k Ryzen AI Halo přes SSH.

### Linux

Kliknutím na odkaz stáhněte preferovaný formát:

| Formát | Stažení | Příkaz pro instalaci |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Poznámka:** Ubuntu App Center může označit lokálně otevřený soubor `.deb` jako *„Potenciálně nebezpečný."* Jedná se o standardní upozornění pro jakýkoli místní instalátor třetí strany. Pokud otevření souboru `.deb` dvojitým kliknutím selže, použijte výše uvedený příkaz v terminálu.

---

## Krok 3 — Připojení k Ryzen AI Halo

Při prvním spuštění zobrazí AMD Sync formulář **Add a Remote Device**. Vyplňte ho hodnotami ze záložky **Remote** v Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Poznámky |
|-------|-------|
| **Device Name** *(volitelné)* | Přátelský název, například `Ryzen AI Halo`. Výchozí hodnota je `Device 1`, `Device 2`, … |
| **Hostname or IP** | Ze záložky Remote |
| **SSH Port** | Ze záložky Remote (pouze čísla) |
| **Username** | Název vašeho účtu OS na Ryzen AI Halo |
| **Password** | Vaše přihlašovací heslo OS — při psaní je maskováno |

Klikněte na **Add Device**. Po krátké načítací obrazovce uvidíte **„Connection Successful"** a přejdete na domovské zobrazení, které se nachází v systémové liště. Kliknutím mimo okno ho zavřete; AMD Sync zůstane spuštěný a je dostupný jedním kliknutím.

> **Pokud se připojení nezdaří,** AMD Sync se vrátí na formulář s vašimi zachovanými hodnotami. Obvyklými příčinami jsou vypnuté SSH na Ryzen AI Halo, nesprávné heslo nebo to, že jsou obě zařízení v různých sítích.

---

## Krok 4 — Spuštění prvního vzdáleného nástroje

Domovské zobrazení nabízí pět komponent dostupných jedním kliknutím — všechny jsou k dispozici bez ohledu na to, jaký OS běží na klientovi a Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponenta | Co dělá |
|-----------|--------------|
| **Directory** | Vybere složku na Ryzen AI Halo, ve které se VS Code, Terminal a JupyterLab otevřou. Výchozí je spravovaný pracovní prostor `Documents/AMD_Sync`. |
| **VS Code** | Otevře VS Code lokálně s SSH tunelem do vybrané složky. |
| **Terminal** | Otevře lokální terminál připojený přes SSH k Ryzen AI Halo ve vybrané složce. |
| **JupyterLab** | Spustí projekt s notebooky připojený přes SSH k Ryzen AI Halo, omezený na vybranou složku. |
| **Live Metrics** | Živý přehled využití GPU, paměti a CPU na Ryzen AI Halo. |

### Vyzkoušejte VS Code

Pro první spuštění zkuste **VS Code**.

1. Ponechte **Directory** na výchozím `~/Documents/AMD_Sync`.
2. Klikněte na **VS Code**.
3. AMD Sync vytvoří `Documents/AMD_Sync/Project_1` na Ryzen AI Halo a otevře VS Code lokálně s tunelem do této složky.

Nyní upravujete soubory uložené na Ryzen AI Halo pomocí vašeho lokálního VS Code. Vytvořte `helloworld.py`, přidejte `print("hello world")`, otevřete integrovaný terminál (`` Ctrl + ` ``) a spusťte ho:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Stavový řádek zobrazuje **SSH: Linux** — důkaz, že váš kód běží na Ryzen AI Halo, nikoli na vašem laptopu.

### Vyzkoušejte Terminal

Klikněte na **Terminal** a přejděte do stejné složky přes SSH bez nutnosti opustit klávesnici.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Na Windows je výchozím terminálem **PowerShell** — v nabídce Nastavení přepněte na **Windows Command Prompt**, pokud preferujete. Na Linuxu AMD Sync používá váš výchozí systémový terminál.

---

## Jak funguje Directory

Rozbalovací nabídka **Directory** je nejdůležitějším ovládacím prvkem v AMD Sync — určuje, kde na Ryzen AI Halo se každý spuštěný nástroj otevře.

- **`~/Documents/AMD_Sync` (výchozí)** — Spuštění VS Code nebo JupyterLab odtud automaticky vytvoří novou projektovou složku (`Project_1`, `Project_2`, … pro VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pro JupyterLab).
- **Existující projektové složky** — Každá přímá podsložka `AMD_Sync` (včetně složek, které ručně vytvoříte na Ryzen AI Halo) se zobrazí v rozbalovací nabídce. Poslední použitá složka se stane výchozí při příštím spuštění.
- **Vlastní cesty** — Zadejte libovolnou absolutní cestu pro otevření složky kdekoli na Ryzen AI Halo. AMD Sync ji pouze *otevře* — nevytváří složky mimo `AMD_Sync` a vlastní cesty se mezi relacemi neukládají.

Pokud vlastní cesta nefunguje, AMD Sync vám sdělí proč: neplatná syntaxe, složka neexistuje nebo cesta ukazuje na soubor.

---

## Live Metrics a JupyterLab

- **Live Metrics** — Živý přehled využití GPU, paměti a CPU. Nejrychlejší způsob, jak ověřit, že vzdálený tréninkový běh skutečně využívá hardware.
- **JupyterLab** — Plnohodnotný projekt s notebooky připojený přes SSH k Ryzen AI Halo s vlastním integrovaným terminálem pro kombinování buněk notebooku a příkazů shellu bez opuštění uživatelského rozhraní.

---

## Nastavení a více zařízení

Nabídka **Settings** má tři záložky:

| Záložka | Co pokrývá |
|-----|----------------|
| **Devices** | Zobrazuje seznam všech Ryzen AI Halo, ke kterým jste se úspěšně připojili. Znovu se připojte, upravte přihlašovací údaje nebo přidejte nové zařízení. |
| **Information** | Odkazy na dokumentaci a podporu na fóru. |
| **Customize** | Přemístěte aplikaci na ploše, přepněte typ terminálu (pouze Windows) a zkontrolujte aktualizace AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminálu (Windows)** — Vyberte mezi **PowerShell** (výchozí) a **Windows Command Prompt**.
- **Typ terminálu (Linux)** — K dispozici je pouze výchozí systémový terminál.
- **Aktualizace aplikace** — Tato záložka je správné místo pro kontrolu a instalaci nových verzí AMD Sync přímo v uživatelském rozhraní; není potřeba žádný samostatný aktualizátor.

> Zařízení se zobrazí v části **Devices** až po úspěšném prvním připojení, takže neúspěšné pokusy seznam nezaplní.

---

## Řešení problémů

- **Připojení okamžitě selže** — Ověřte, že je SSH server povolen na záložce **Remote** v Developer Center na Ryzen AI Halo.
- **Chyba nesprávného hesla** — Použijte své **přihlašovací heslo OS** na Ryzen AI Halo, nikoli hesla z Developer Center.
- **Tlačítko VS Code nereaguje** — Nainstalujte VS Code na svůj klientský počítač z [code.visualstudio.com](https://code.visualstudio.com).
- **Ikona AMD Sync v systémové liště chybí (Linux/GNOME)** — Nainstalujte a povolte rozšíření AppIndicator.
- **Soubor `.deb` nelze otevřít ze správce souborů** — Použijte `sudo apt install ./AMDSyncInstaller.deb` z terminálu.

---