<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# AMD Sync ile Uzaktan Geliştirme

## Genel Bakış

**AMD Sync**, dizüstü bilgisayarınızı AMD Ryzen™ AI Halo için uzak bir kokpite dönüştürür. Manuel SSH, anahtar ve IDE kurulumunu atlayın — AMD Sync'i yükleyin ve Ryzen AI Halo üzerinde uzak terminale, VS Code'a, JupyterLab'e ve canlı GPU/CPU/bellek panosuna tek tıkla erişim elde edin.

Yerel makineniz tanıdık kalır; her komut, defter ve model Ryzen AI Halo üzerinde çalışır.

> **İpucu**: Bu sayfa AMDSync'e yapılacak yeni güncellemeleri içerecektir. 

## Öğrenecekleriniz

- Ryzen AI Halo'da SSH'ı etkinleştirme ve AMD Sync'ten ona bağlanma
- VS Code, Terminal, JupyterLab ve Canlı Metrikler'i Ryzen AI Halo'ya karşı tek tıkla başlatma
- AMD Sync'in yönetilen proje klasörlerini kullanarak uzak çalışmayı organize etme

---

## Temel Kavramlar

AMD Sync'in iki tarafı vardır: bir **istemci** (dizüstü bilgisayarınız, AMD Sync uygulamasını çalıştıran) ve bir **sunucu** (AMD Sync'in tünellediği bir SSH sunucusu çalıştıran Ryzen AI Halo). AMD Sync'ten başlattığınız her şey — VS Code, bir terminal, bir defter — yerel olarak açılır ancak Ryzen AI Halo üzerinde çalışır.

> **Desteklenen istemciler:** Windows 11 ve Linux. macOS desteklenmemektedir.

---

## Adım 1 — Ryzen AI Halo'da SSH'ı Etkinleştirme


> **Not:** Windows'ta, Ryzen AI Halo SSH sunucusu *varsayılan olarak kapalı* şekilde gelir. Linux'ta ise SSH sunucusu *varsayılan olarak açık* gelir.

1. Ryzen AI Halo üzerinde, **AMD Ryzen™ AI Developer Center**'ı açın.
2. **Remote** sekmesine gidin.
3. **SSH Server**'ı açık konuma getirin.
4. **Server Information** altında gösterilen **IP Address**, **Port** ve **Username** bilgilerini not edin — bunları AMD Sync'e yapıştıracaksınız.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Not:** Bu, Windows için AMD Developer Center'dır. Linux sürümünün kullanıcı arayüzü farklı olabilir, ancak benzer uzak işlevsellik sunar.

> **İpucu:** AMD Sync, Developer Center'daki bir parola değil, o kullanıcının **işletim sistemi giriş parolasını** ister.

---

## Adım 2 — AMD Sync'i İstemcinize Yükleme

AMD Sync, Windows 11 ve Linux üzerinde çalışır. İşletim sisteminize uygun yükleyiciyi indirin, ardından aşağıdaki adımları izleyin. Kurulumdan sonra, **Get Started** ekranında **Accept & Install**'a tıklayın — işlem tamamlandığında AMD Sync otomatik olarak başlar.

### Windows

[AMDSyncInstaller.exe'yi İndirin](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe` dosyasına çift tıklayın.
2. **Accept & Install**'a tıklayın.

> Windows Firewall sizden onay isterse, Ryzen AI Halo'ya SSH üzerinden erişebilmesi için AMD Sync'e ağ erişimine izin verin.

### Linux

Tercih ettiğiniz biçimi indirmek için bağlantıya tıklayın:

| Biçim | İndirme | Kurulum komutu |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Not:** Ubuntu App Center, yerel olarak açılan bir `.deb` dosyasını *"Potansiyel olarak güvensiz"* olarak işaretleyebilir. Bu, üçüncü taraf herhangi bir yerel yükleyici için standart bir uyarıdır. `.deb` dosyasına çift tıklamak başarısız olursa, yukarıdaki terminal komutunu kullanın.

---

## Adım 3 — Ryzen AI Halo'nuza Bağlanma

İlk başlatmada, AMD Sync **Add a Remote Device** formunu gösterir. Bu formu, Developer Center'ın **Remote** sekmesindeki değerleri kullanarak doldurun.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Alan | Notlar |
|-------|-------|
| **Device Name** *(isteğe bağlı)* | `Ryzen AI Halo` gibi anlaşılır bir etiket. Varsayılan olarak `Device 1`, `Device 2`, … şeklindedir. |
| **Hostname or IP** | Remote sekmesinden |
| **SSH Port** | Remote sekmesinden (yalnızca rakamlar) |
| **Username** | Ryzen AI Halo üzerindeki işletim sistemi hesap adınız |
| **Password** | İşletim sistemi giriş parolanız — yazarken maskelenir |

**Add Device**'e tıklayın. Kısa bir yükleme ekranının ardından, **"Connection Successful"** mesajını görecek ve sistem tepsinizde bulunan ana görünüme geçeceksiniz. Pencereyi kapatmak için pencerenin dışına tıklayın; AMD Sync çalışmaya devam eder ve tek tıkla erişilebilir durumda kalır.

> **Bağlantı başarısız olursa,** AMD Sync girdiğiniz değerleri koruyarak forma geri döner. Yaygın nedenler, Ryzen AI Halo'da SSH'ın devre dışı olması, yanlış parola veya iki cihazın farklı ağlarda bulunmasıdır.

---

## Adım 4 — İlk Uzak Aracınızı Başlatma

Ana görünüm, istemci ve Ryzen AI Halo hangi işletim sistemini çalıştırıyor olursa olsun kullanılabilen beş tek tıklamalı bileşen sunar.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Bileşen | Ne yapar |
|-----------|--------------|
| **Directory** | VS Code, Terminal ve JupyterLab'in açılacağı Ryzen AI Halo üzerindeki klasörü seçer. Varsayılan olarak yönetilen bir `Documents/AMD_Sync` çalışma alanı kullanılır. |
| **VS Code** | Seçilen klasöre bir SSH tüneli ile yerel olarak VS Code'u açar. |
| **Terminal** | Ryzen AI Halo'ya SSH ile bağlı, seçilen klasörde yerel bir terminal açar. |
| **JupyterLab** | Ryzen AI Halo'ya SSH ile bağlı, seçilen klasörle sınırlı bir defter projesi başlatır. |
| **Live Metrics** | Ryzen AI Halo üzerindeki GPU, bellek ve CPU kullanımının gerçek zamanlı görünümü. |

### VS Code'u Deneyin

İlk başlatmanız için **VS Code**'u deneyin.

1. **Directory**'yi varsayılan `~/Documents/AMD_Sync` olarak bırakın.
2. **VS Code**'a tıklayın.
3. AMD Sync, Ryzen AI Halo üzerinde `Documents/AMD_Sync/Project_1` klasörünü oluşturur ve VS Code'u yerel olarak, buna tünellenmiş şekilde açar.

Artık Ryzen AI Halo üzerinde bulunan dosyaları yerel VS Code kurulumunuzla düzenliyorsunuz. `helloworld.py` dosyasını oluşturun, `print("hello world")` ekleyin, entegre terminali açın (`` Ctrl + ` ``) ve çalıştırın:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Durum çubuğunda **SSH: Linux** yazısı görünür — bu, kodunuzun dizüstü bilgisayarınızda değil, Ryzen AI Halo üzerinde çalıştığının kanıtıdır.
### Terminal'i Deneyin

Klavyeyi bırakmadan SSH üzerinden aynı klasöre girmek için **Terminal**'e tıklayın.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows'ta varsayılan terminal **PowerShell**'dir — tercih ederseniz Settings menüsünden **Windows Command Prompt**'a geçebilirsiniz. Linux'ta AMD Sync, varsayılan sistem terminalinizi kullanır.

---

## Directory Nasıl Çalışır

**Directory** açılır menüsü, AMD Sync'teki en önemli tek kontroldür — başlattığınız her aracın Ryzen AI Halo üzerinde nereye ineceğine karar verir.

- **`~/Documents/AMD_Sync` (varsayılan)** — Buradan VS Code veya JupyterLab başlatmak otomatik olarak yeni bir proje klasörü oluşturur (VS Code için `Project_1`, `Project_2`, …; JupyterLab için `Notebook_Project_1`, `Notebook_Project_2`, …).
- **Mevcut proje klasörleri** — `AMD_Sync`'in doğrudan alt klasörlerinden herhangi biri (Ryzen AI Halo üzerinde manuel olarak oluşturduğunuz klasörler dahil) açılır menüde görünür. Son kullandığınız klasör, bir sonraki seferde varsayılan olur.
- **Özel yollar** — Ryzen AI Halo üzerinde başka bir yerdeki bir klasörü açmak için herhangi bir mutlak yol yazın. AMD Sync sadece onu *açar* — `AMD_Sync` dışında klasör oluşturmaz ve özel yollar oturumlar arasında kaydedilmez.

Özel bir yol çalışmazsa, AMD Sync nedenini söyler: geçersiz söz dizimi, klasör mevcut değil veya yol bir dosyayı işaret ediyor.

---

## Live Metrics ve JupyterLab

- **Live Metrics** — GPU, bellek ve CPU kullanımının canlı bir panosu. Uzaktaki bir eğitim çalışmasının donanıma gerçekten ulaştığını doğrulamanın en hızlı yolu.
- **JupyterLab** — Ryzen AI Halo'ya SSH ile bağlı, kendi entegre terminaline sahip tam bir notebook projesi; böylece not defteri hücrelerini ve kabuk komutlarını arayüzden çıkmadan bir arada kullanabilirsiniz.

---

## Settings ve Birden Fazla Cihaz

**Settings** menüsünün üç sekmesi vardır:

| Sekme | Neyi kapsar |
|-----|----------------|
| **Devices** | Başarıyla bağlandığınız her Ryzen AI Halo cihazını listeler. Yeniden bağlanın, kimlik bilgilerini düzenleyin veya yeni bir cihaz ekleyin. |
| **Information** | Belgelere ve forum desteğine bağlantılar. |
| **Customize** | Uygulamayı masaüstünüzde yeniden konumlandırın, terminal türünü değiştirin (yalnızca Windows) ve AMD Sync güncellemelerini kontrol edin. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminal türü (Windows)** — **PowerShell** (varsayılan) ile **Windows Command Prompt** arasında seçim yapın.
- **Terminal türü (Linux)** — Yalnızca varsayılan sistem terminali kullanılabilir.
- **Uygulama güncellemeleri** — Bu sekme, arayüzden ayrılmadan yeni AMD Sync sürümlerini kontrol edip yüklemek için doğru yerdir; ayrı bir güncelleyiciye gerek yoktur.

> Bir cihaz, **Devices** altında ancak başarılı bir ilk bağlantıdan sonra görünür; bu sayede başarısız denemeler listeyi kalabalıklaştırmaz.

---

## Sorun Giderme

- **Bağlantı hemen başarısız oluyor** — Developer Center'daki **Remote** sekmesinde Ryzen AI Halo üzerinde SSH sunucusunun etkinleştirildiğini doğrulayın.
- **Yanlış parola hatası** — Developer Center'dan alınan parolaları değil, Ryzen AI Halo üzerindeki **işletim sistemi giriş parolanızı** kullanın.
- **VS Code düğmesi hiçbir şey yapmıyor** — İstemci makinenize [code.visualstudio.com](https://code.visualstudio.com) adresinden VS Code'u yükleyin.
- **AMD Sync tepsi simgesi eksik (Linux/GNOME)** — AppIndicator uzantısını yükleyip etkinleştirin.
- **`.deb` dosya yöneticisinden açılmıyor** — Bir terminalden `sudo apt install ./AMDSyncInstaller.deb` komutunu kullanın.
- **Kurulum her başlatmada yeniden ortaya çıkıyor (Linux)**: giriş anahtarlığınızın kilidini açın veya `--password-store=gnome-libsecret` ile başlatın, ardından kurulumu bir kez daha yapın.

---