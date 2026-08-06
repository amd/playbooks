<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Zdalny rozwój z AMD Sync

## Przegląd

**AMD Sync** zamienia Twój laptop w zdalny kokpit dla AMD Ryzen™ AI Halo. Pomiń ręczną konfigurację SSH, kluczy i IDE — zainstaluj AMD Sync i uzyskaj dostęp jednym kliknięciem do zdalnego terminala, VS Code, JupyterLab oraz pulpitu na żywo z danymi o GPU/CPU/pamięci na Ryzen AI Halo.

Twoja maszyna lokalna pozostaje znajoma; każde polecenie, notatnik i model działają na Ryzen AI Halo.

> **Wskazówka**: Ta strona będzie zawierać wszelkie nowe aktualizacje AMDSync. 

## Czego się nauczysz

- Włączyć SSH na Ryzen AI Halo i połączyć się z nim z poziomu AMD Sync
- Uruchamiać VS Code, Terminal, JupyterLab i Live Metrics na Ryzen AI Halo jednym kliknięciem
- Organizować zdalną pracę za pomocą zarządzanych folderów projektów AMD Sync

---

## Podstawowe pojęcia

AMD Sync ma dwie strony: **klienta** (Twój laptop, na którym działa aplikacja AMD Sync) oraz **serwer** (Ryzen AI Halo, na którym działa serwer SSH, do którego AMD Sync tworzy tunel). Wszystko, co uruchamiasz z poziomu AMD Sync — VS Code, terminal, notatnik — otwiera się lokalnie, ale wykonuje się na Ryzen AI Halo.

> **Obsługiwani klienci:** Windows 11 i Linux. macOS nie jest obsługiwany.

---

## Krok 1 — Włącz SSH na Ryzen AI Halo


> **Uwaga:** W systemie Windows Ryzen AI Halo jest dostarczany z serwerem SSH *domyślnie wyłączonym*. W systemie Linux jest dostarczany z serwerem SSH *domyślnie włączonym*.

1. Na Ryzen AI Halo otwórz **AMD Ryzen™ AI Developer Center**.
2. Przejdź do zakładki **Remote**.
3. Włącz przełącznik **SSH Server**.
4. Zanotuj **IP Address**, **Port** oraz **Username** wyświetlone w sekcji **Server Information** — wkleisz je do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Uwaga:** To jest AMD Developer Center dla systemu Windows. Wersja dla systemu Linux może mieć inny interfejs, ale podobną funkcjonalność zdalną.

> **Wskazówka:** AMD Sync prosi o **hasło logowania do systemu operacyjnego** danego użytkownika, a nie o hasło z Developer Center.

---

## Krok 2 — Zainstaluj AMD Sync na swoim kliencie

AMD Sync działa w systemach Windows 11 i Linux. Pobierz instalator dla swojego systemu operacyjnego, a następnie wykonaj poniższe kroki. Po instalacji kliknij **Accept & Install** na ekranie **Get Started** — AMD Sync uruchomi się automatycznie po zakończeniu.

### Windows

[Pobierz AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kliknij dwukrotnie plik `AMDSyncInstaller.exe`.
2. Kliknij **Accept & Install**.

> Jeśli zapora Windows Firewall wyświetli monit, zezwól AMD Sync na dostęp do sieci, aby mógł łączyć się z Ryzen AI Halo przez SSH.

### Linux

Kliknij link, aby pobrać preferowany format:

| Format | Pobieranie | Polecenie instalacji |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Uwaga:** Ubuntu App Center może oznaczyć lokalnie otwarty plik `.deb` jako *"Potencjalnie niebezpieczny."* To standardowe ostrzeżenie dla każdego instalatora innej firmy uruchamianego lokalnie. Jeśli dwukrotne kliknięcie pliku `.deb` się nie powiedzie, użyj powyższego polecenia w terminalu.

---

## Krok 3 — Połącz się ze swoim Ryzen AI Halo

Przy pierwszym uruchomieniu AMD Sync wyświetla formularz **Add a Remote Device**. Wypełnij go, korzystając z wartości z zakładki **Remote** w Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Uwagi |
|-------|-------|
| **Device Name** *(opcjonalnie)* | Przyjazna nazwa, np. `Ryzen AI Halo`. Domyślnie `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z zakładki Remote |
| **SSH Port** | Z zakładki Remote (tylko cyfry) |
| **Username** | Nazwa Twojego konta systemowego na Ryzen AI Halo |
| **Password** | Hasło logowania do systemu operacyjnego — maskowane podczas wpisywania |

Kliknij **Add Device**. Po krótkim ekranie ładowania zobaczysz komunikat **"Connection Successful"** i przejdziesz do widoku głównego, który znajduje się w zasobniku systemowym. Kliknij poza oknem, aby je zamknąć; AMD Sync pozostaje uruchomiony i jest dostępny jednym kliknięciem.

> **Jeśli połączenie się nie powiedzie,** AMD Sync powróci do formularza z zachowanymi wartościami. Najczęstsze przyczyny to wyłączony SSH na Ryzen AI Halo, błędne hasło lub urządzenia znajdujące się w różnych sieciach.

---

## Krok 4 — Uruchom swoje pierwsze narzędzie zdalne

Widok główny udostępnia pięć komponentów uruchamianych jednym kliknięciem — wszystkie dostępne niezależnie od tego, jaki system operacyjny działa na kliencie i na Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Co robi |
|-----------|--------------|
| **Directory** | Wybiera folder na Ryzen AI Halo, w którym otworzą się VS Code, Terminal i JupyterLab. Domyślnie jest to zarządzany obszar roboczy `Documents/AMD_Sync`. |
| **VS Code** | Otwiera VS Code lokalnie z tunelem SSH do wybranego folderu. |
| **Terminal** | Otwiera lokalny terminal połączony przez SSH z Ryzen AI Halo, w wybranym folderze. |
| **JupyterLab** | Uruchamia projekt notatnika połączony przez SSH z Ryzen AI Halo, ograniczony do wybranego folderu. |
| **Live Metrics** | Widok w czasie rzeczywistym wykorzystania GPU, pamięci i CPU na Ryzen AI Halo. |

### Wypróbuj VS Code

Przy pierwszym uruchomieniu wypróbuj **VS Code**.

1. Pozostaw **Directory** na wartości domyślnej `~/Documents/AMD_Sync`.
2. Kliknij **VS Code**.
3. AMD Sync utworzy folder `Documents/AMD_Sync/Project_1` na Ryzen AI Halo i otworzy VS Code lokalnie, z tunelem do tego folderu.

Teraz edytujesz pliki znajdujące się na Ryzen AI Halo, korzystając z lokalnej konfiguracji VS Code. Utwórz plik `helloworld.py`, dodaj `print("hello world")`, otwórz zintegrowany terminal (`` Ctrl + ` ``) i uruchom go:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Pasek stanu wyświetla **SSH: Linux** — dowód na to, że Twój kod działa na Ryzen AI Halo, a nie na laptopie.
### Wypróbuj Terminal

Kliknij **Terminal**, aby przejść do tego samego folderu przez SSH bez odrywania rąk od klawiatury.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

W systemie Windows domyślnym terminalem jest **PowerShell** — jeśli wolisz, przełącz się na **Windows Command Prompt** w menu Ustawień. W systemie Linux AMD Sync korzysta z domyślnego terminala systemowego.

---

## Jak działa Katalog

Rozwijana lista **Katalog** to najważniejszy element sterujący w AMD Sync — decyduje o tym, gdzie na Ryzen AI Halo trafia każde uruchamiane narzędzie.

- **`~/Documents/AMD_Sync` (domyślnie)** — uruchomienie VS Code lub JupyterLab z tego miejsca automatycznie tworzy nowy folder projektu (`Project_1`, `Project_2`, … dla VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … dla JupyterLab).
- **Istniejące foldery projektów** — każdy bezpośredni podfolder `AMD_Sync` (w tym foldery utworzone ręcznie na Ryzen AI Halo) pojawia się na liście rozwijanej. Ostatnio używany folder staje się domyślnym przy następnym uruchomieniu.
- **Ścieżki niestandardowe** — wpisz dowolną ścieżkę bezwzględną, aby otworzyć folder w innym miejscu na Ryzen AI Halo. AMD Sync jedynie *otwiera* taki folder — nie tworzy folderów poza `AMD_Sync`, a ścieżki niestandardowe nie są zapamiętywane między sesjami.

Jeśli niestandardowa ścieżka nie działa, AMD Sync informuje dlaczego: nieprawidłowa składnia, folder nie istnieje lub ścieżka wskazuje na plik.

---

## Metryki na żywo i JupyterLab

- **Metryki na żywo** — panel na żywo z wykorzystaniem GPU, pamięci i CPU. Najszybszy sposób na potwierdzenie, że zdalne zadanie treningowe faktycznie obciąża sprzęt.
- **JupyterLab** — pełny projekt notatnika połączony przez SSH z Ryzen AI Halo, z własnym zintegrowanym terminalem umożliwiającym łączenie komórek notatnika z poleceniami powłoki bez opuszczania interfejsu.

---

## Ustawienia i wiele urządzeń

Menu **Ustawienia** zawiera trzy zakładki:

| Zakładka | Co obejmuje |
|-----|----------------|
| **Urządzenia** | Wyświetla listę wszystkich urządzeń Ryzen AI Halo, z którymi udało się nawiązać połączenie. Umożliwia ponowne połączenie, edycję danych uwierzytelniających lub dodanie nowego urządzenia. |
| **Informacje** | Łącza do dokumentacji i wsparcia na forum. |
| **Dostosuj** | Zmiana położenia aplikacji na pulpicie, przełączanie typu terminala (tylko Windows) oraz sprawdzanie dostępności aktualizacji AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminala (Windows)** — wybór między **PowerShell** (domyślnie) a **Windows Command Prompt**.
- **Typ terminala (Linux)** — dostępny jest tylko domyślny terminal systemowy.
- **Aktualizacje aplikacji** — ta zakładka to właściwe miejsce do sprawdzania i instalowania nowych wersji AMD Sync bezpośrednio z poziomu interfejsu; nie jest potrzebny osobny program aktualizujący.

> Urządzenie pojawia się w zakładce **Urządzenia** dopiero po pomyślnym pierwszym połączeniu, więc nieudane próby nie zaśmiecają listy.

---

## Rozwiązywanie problemów

- **Połączenie natychmiast się nie powodzi** — upewnij się, że serwer SSH jest włączony w zakładce **Remote** w Developer Center na Ryzen AI Halo.
- **Błąd nieprawidłowego hasła** — użyj **hasła logowania do systemu operacyjnego** na Ryzen AI Halo, a nie haseł pobranych z Developer Center.
- **Przycisk VS Code nic nie robi** — zainstaluj VS Code na swoim komputerze klienckim ze strony [code.visualstudio.com](https://code.visualstudio.com).
- **Brak ikony AMD Sync w zasobniku systemowym (Linux/GNOME)** — zainstaluj i włącz rozszerzenie AppIndicator.
- **Plik `.deb` nie otwiera się z menedżera plików** — użyj polecenia `sudo apt install ./AMDSyncInstaller.deb` w terminalu.

---