<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Zdalne programowanie z AMD Sync

## Przegląd

**AMD Sync** zamienia Twój laptop w zdalny kokpit dla AMD Ryzen™ AI Halo. Pomiń ręczną konfigurację SSH, kluczy i IDE — zainstaluj AMD Sync i uzyskaj jednym kliknięciem dostęp do zdalnego terminala, VS Code, JupyterLab oraz aktualnego pulpitu GPU/CPU/pamięci na Ryzen AI Halo.

Twoja lokalna maszyna pozostaje znajoma; każde polecenie, notatnik i model działa na Ryzen AI Halo.

> **Wskazówka**: Ta strona będzie zawierać wszelkie nowe aktualizacje AMDSync.

## Czego się nauczysz

- Włączyć SSH na Ryzen AI Halo i połączyć się z nim z poziomu AMD Sync
- Uruchamiać VS Code, Terminal, JupyterLab i Live Metrics na Ryzen AI Halo jednym kliknięciem
- Organizować pracę zdalną przy użyciu zarządzanych folderów projektów AMD Sync

---

## Podstawowe pojęcia

AMD Sync ma dwie strony: **klient** (Twój laptop, na którym działa aplikacja AMD Sync) i **serwer** (Ryzen AI Halo, na którym działa serwer SSH, do którego AMD Sync tworzy tunel). Wszystko, co uruchamiasz z AMD Sync — VS Code, terminal, notatnik — otwiera się lokalnie, ale wykonuje na Ryzen AI Halo.

> **Obsługiwane klienty:** Windows 11 i Linux. macOS nie jest obsługiwany.

---

## Krok 1 — Włącz SSH na Ryzen AI Halo


> **Uwaga:** W systemie Windows Ryzen AI Halo jest dostarczany z serwerem SSH *domyślnie wyłączonym*. W systemie Linux jest dostarczany z serwerem SSH *domyślnie włączonym*.

1. Na Ryzen AI Halo otwórz **AMD Ryzen™ AI Developer Center**.
2. Przejdź do zakładki **Remote**.
3. Włącz przełącznik **SSH Server**.
4. Zanotuj **adres IP**, **port** i **nazwę użytkownika** widoczne w sekcji **Server Information** — wkleisz je do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Uwaga:** To jest AMD Developer Center dla systemu Windows. Wersja dla systemu Linux może mieć inny interfejs, ale podobną funkcjonalność zdalną.

> **Wskazówka:** AMD Sync prosi o **hasło logowania do systemu operacyjnego** danego użytkownika, a nie o hasło z Developer Center.

---

## Krok 2 — Zainstaluj AMD Sync na swoim kliencie

AMD Sync działa na Windows 11 i Linux. Pobierz instalator dla swojego systemu operacyjnego, a następnie wykonaj poniższe kroki. Po instalacji kliknij **Accept & Install** na ekranie **Get Started** — AMD Sync uruchamia się automatycznie po zakończeniu.

### Windows

[Pobierz AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kliknij dwukrotnie `AMDSyncInstaller.exe`.
2. Kliknij **Accept & Install**.

> Jeśli Zapora systemu Windows wyświetli monit, zezwól AMD Sync na dostęp do sieci, aby mógł połączyć się z Ryzen AI Halo przez SSH.

### Linux

Kliknij link, aby pobrać preferowany format:

| Format | Pobieranie | Polecenie instalacji |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Uwaga:** Ubuntu App Center może oznaczyć lokalnie otwierany plik `.deb` jako *„Potencjalnie niebezpieczny"*. To standardowe ostrzeżenie dla każdego lokalnego instalatora firm trzecich. Jeśli dwukrotne kliknięcie pliku `.deb` nie powiedzie się, użyj powyższego polecenia terminalowego.

---

## Krok 3 — Połącz się z Ryzen AI Halo

Przy pierwszym uruchomieniu AMD Sync wyświetla formularz **Add a Remote Device**. Wypełnij go, używając wartości z zakładki **Remote** w Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Uwagi |
|-------|-------|
| **Device Name** *(opcjonalne)* | Przyjazna etykieta, np. `Ryzen AI Halo`. Domyślnie `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z zakładki Remote |
| **SSH Port** | Z zakładki Remote (tylko cyfry) |
| **Username** | Nazwa Twojego konta systemowego na Ryzen AI Halo |
| **Password** | Hasło logowania do systemu operacyjnego — maskowane podczas wpisywania |

Kliknij **Add Device**. Po krótkim ekranie ładowania zobaczysz **„Connection Successful"** i trafisz do widoku głównego, który znajduje się w zasobniku systemowym. Kliknij poza oknem, aby je zamknąć; AMD Sync pozostaje uruchomiony i jest dostępny jednym kliknięciem.

> **Jeśli połączenie nie powiedzie się,** AMD Sync powraca do formularza z zachowanymi wartościami. Typowe przyczyny to wyłączony SSH na Ryzen AI Halo, błędne hasło lub urządzenia w różnych sieciach.

---

## Krok 4 — Uruchom swoje pierwsze zdalne narzędzie

Widok główny oferuje pięć komponentów dostępnych jednym kliknięciem — wszystkie dostępne niezależnie od systemu operacyjnego klienta i Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Co robi |
|-----------|--------------|
| **Directory** | Wybiera folder na Ryzen AI Halo, w którym VS Code, Terminal i JupyterLab będą otwierane. Domyślnie zarządzany obszar roboczy `Documents/AMD_Sync`. |
| **VS Code** | Otwiera VS Code lokalnie z tunelem SSH do wybranego folderu. |
| **Terminal** | Otwiera lokalny terminal połączony przez SSH z Ryzen AI Halo, w wybranym folderze. |
| **JupyterLab** | Uruchamia projekt notatnikowy połączony przez SSH z Ryzen AI Halo, ograniczony do wybranego folderu. |
| **Live Metrics** | Widok w czasie rzeczywistym wykorzystania GPU, pamięci i CPU na Ryzen AI Halo. |

### Wypróbuj VS Code

Przy pierwszym uruchomieniu wypróbuj **VS Code**.

1. Pozostaw **Directory** na domyślnym `~/Documents/AMD_Sync`.
2. Kliknij **VS Code**.
3. AMD Sync tworzy `Documents/AMD_Sync/Project_1` na Ryzen AI Halo i otwiera VS Code lokalnie, z tunelem do tego folderu.

Teraz edytujesz pliki znajdujące się na Ryzen AI Halo przy użyciu lokalnej konfiguracji VS Code. Utwórz `helloworld.py`, dodaj `print("hello world")`, otwórz zintegrowany terminal (`` Ctrl + ` ``) i uruchom go:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Pasek stanu wyświetla **SSH: Linux** — dowód, że Twój kod działa na Ryzen AI Halo, a nie na laptopie.

### Wypróbuj Terminal

Kliknij **Terminal**, aby przejść do tego samego folderu przez SSH bez opuszczania klawiatury.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

W systemie Windows domyślnym terminalem jest **PowerShell** — przełącz się na **Windows Command Prompt** z menu Ustawienia, jeśli wolisz. W systemie Linux AMD Sync używa domyślnego terminala systemowego.

---

## Jak działa katalog

Lista rozwijana **Directory** to najważniejsza kontrolka w AMD Sync — decyduje, gdzie na Ryzen AI Halo trafia każde uruchamiane narzędzie.

- **`~/Documents/AMD_Sync` (domyślny)** — Uruchomienie VS Code lub JupyterLab z tego miejsca automatycznie tworzy nowy folder projektu (`Project_1`, `Project_2`, … dla VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … dla JupyterLab).
- **Istniejące foldery projektów** — Każdy bezpośredni element podrzędny `AMD_Sync` (w tym foldery tworzone ręcznie na Ryzen AI Halo) pojawia się na liście rozwijanej. Ostatnio używany folder staje się domyślnym przy następnym uruchomieniu.
- **Niestandardowe ścieżki** — Wpisz dowolną ścieżkę bezwzględną, aby otworzyć folder w innym miejscu na Ryzen AI Halo. AMD Sync tylko go *otwiera* — nie tworzy folderów poza `AMD_Sync`, a niestandardowe ścieżki nie są zapisywane między sesjami.

Jeśli niestandardowa ścieżka nie działa, AMD Sync informuje o przyczynie: nieprawidłowa składnia, folder nie istnieje lub ścieżka wskazuje na plik.

---

## Live Metrics i JupyterLab

- **Live Metrics** — Aktualny pulpit wykorzystania GPU, pamięci i CPU. Najszybszy sposób na potwierdzenie, że zdalne zadanie treningowe rzeczywiście obciąża sprzęt.
- **JupyterLab** — Pełny projekt notatnikowy połączony przez SSH z Ryzen AI Halo, z własnym zintegrowanym terminalem umożliwiającym łączenie komórek notatnika i poleceń powłoki bez opuszczania interfejsu.

---

## Ustawienia i wiele urządzeń

Menu **Settings** ma trzy zakładki:

| Zakładka | Co obejmuje |
|-----|----------------|
| **Devices** | Wyświetla listę wszystkich Ryzen AI Halo, z którymi nawiązano pomyślne połączenie. Ponowne połączenie, edycja danych uwierzytelniających lub dodanie nowego urządzenia. |
| **Information** | Linki do dokumentacji i wsparcia na forum. |
| **Customize** | Zmiana położenia aplikacji na pulpicie, przełączanie typu terminala (tylko Windows) oraz sprawdzanie aktualizacji AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminala (Windows)** — Wybierz między **PowerShell** (domyślny) a **Windows Command Prompt**.
- **Typ terminala (Linux)** — Dostępny jest tylko domyślny terminal systemowy.
- **Aktualizacje aplikacji** — Ta zakładka to właściwe miejsce do sprawdzania i instalowania nowych wersji AMD Sync z poziomu interfejsu; nie jest potrzebny osobny program aktualizujący.

> Urządzenie pojawia się w sekcji **Devices** dopiero po pierwszym pomyślnym połączeniu, więc nieudane próby nie zaśmiecają listy.

---

## Rozwiązywanie problemów

- **Połączenie natychmiast się nie udaje** — Sprawdź, czy serwer SSH jest włączony w zakładce **Remote** Ryzen AI Halo w Developer Center.
- **Błąd nieprawidłowego hasła** — Użyj **hasła logowania do systemu operacyjnego** na Ryzen AI Halo, a nie haseł z Developer Center.
- **Przycisk VS Code nic nie robi** — Zainstaluj VS Code na swojej maszynie klienckiej ze strony [code.visualstudio.com](https://code.visualstudio.com).
- **Brak ikony AMD Sync w zasobniku (Linux/GNOME)** — Zainstaluj i włącz rozszerzenie AppIndicator.
- **Plik `.deb` nie otwiera się z menedżera plików** — Użyj polecenia `sudo apt install ./AMDSyncInstaller.deb` z terminala.

---