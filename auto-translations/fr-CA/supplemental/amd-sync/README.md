<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Développement à distance avec AMD Sync

## Aperçu

**AMD Sync** transforme votre ordinateur portable en poste de pilotage à distance pour l'AMD Ryzen™ AI Halo. Oubliez la configuration manuelle de SSH, des clés et de l'IDE — installez AMD Sync et obtenez un accès en un clic à un terminal à distance, à VS Code, à JupyterLab et à un tableau de bord GPU/CPU/mémoire en direct sur le Ryzen AI Halo.

Votre machine locale reste familière; chaque commande, cahier et modèle s'exécute sur le Ryzen AI Halo.

> **Astuce** : Cette page contiendra toute nouvelle mise à jour d'AMDSync.

## Ce que vous apprendrez

- Activer SSH sur le Ryzen AI Halo et vous y connecter depuis AMD Sync
- Lancer VS Code, Terminal, JupyterLab et Live Metrics sur le Ryzen AI Halo en un clic
- Organiser le travail à distance à l'aide des dossiers de projet gérés d'AMD Sync

---

## Concepts de base

AMD Sync comporte deux volets : un **client** (votre ordinateur portable, exécutant l'application AMD Sync) et un **serveur** (le Ryzen AI Halo, exécutant un serveur SSH dans lequel AMD Sync crée un tunnel). Tout ce que vous lancez depuis AMD Sync — VS Code, un terminal, un cahier — s'ouvre localement, mais s'exécute sur le Ryzen AI Halo.

> **Clients pris en charge :** Windows 11 et Linux. macOS n'est pas pris en charge.

---

## Étape 1 — Activer SSH sur le Ryzen AI Halo


> **Remarque :** Sous Windows, le Ryzen AI Halo est livré avec le serveur SSH *désactivé par défaut*. Sous Linux, il est livré avec le serveur SSH *activé par défaut*.

1. Sur le Ryzen AI Halo, ouvrez le **AMD Ryzen™ AI Developer Center**.
2. Accédez à l'onglet **Remote**.
3. Activez **SSH Server**.
4. Notez l'**IP Address**, le **Port** et le **Username** affichés sous **Server Information** — vous les collerez dans AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Remarque :** Il s'agit du AMD Developer Center pour Windows. Celui pour Linux peut avoir une interface utilisateur différente, mais une fonctionnalité à distance semblable.

> **Astuce :** AMD Sync demande le **mot de passe de connexion du système d'exploitation** de cet utilisateur, et non un mot de passe provenant du Developer Center.

---

## Étape 2 — Installer AMD Sync sur votre client

AMD Sync fonctionne sous Windows 11 et Linux. Téléchargez le programme d'installation pour votre système d'exploitation, puis suivez les étapes ci-dessous. Une fois l'installation terminée, cliquez sur **Accept & Install** dans l'écran **Get Started** — AMD Sync se lance automatiquement une fois terminé.

### Windows

[Télécharger AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Double-cliquez sur `AMDSyncInstaller.exe`.
2. Cliquez sur **Accept & Install**.

> Si le pare-feu Windows vous le demande, autorisez l'accès réseau d'AMD Sync afin qu'il puisse joindre le Ryzen AI Halo par SSH.

### Linux

Cliquez sur le lien pour télécharger le format de votre choix :

| Format | Téléchargement | Commande d'installation |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Remarque :** Ubuntu App Center peut signaler un `.deb` ouvert localement comme étant *« potentiellement dangereux »*. Il s'agit de l'avertissement standard pour tout programme d'installation local tiers. Si le double-clic sur le `.deb` échoue, utilisez la commande de terminal ci-dessus.

---

## Étape 3 — Se connecter à votre Ryzen AI Halo

Au premier lancement, AMD Sync affiche le formulaire **Add a Remote Device**. Remplissez-le à l'aide des valeurs de l'onglet **Remote** du Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Champ | Remarques |
|-------|-------|
| **Device Name** *(facultatif)* | Une étiquette conviviale comme `Ryzen AI Halo`. La valeur par défaut est `Device 1`, `Device 2`, … |
| **Hostname or IP** | Depuis l'onglet Remote |
| **SSH Port** | Depuis l'onglet Remote (chiffres seulement) |
| **Username** | Le nom de votre compte du système d'exploitation sur le Ryzen AI Halo |
| **Password** | Votre mot de passe de connexion du système d'exploitation — masqué à la saisie |

Cliquez sur **Add Device**. Après un bref écran de chargement, vous verrez **« Connection Successful »** et arriverez à la vue d'accueil, qui réside dans votre barre d'état système. Cliquez à l'extérieur de la fenêtre pour la fermer; AMD Sync continue de fonctionner et reste accessible en un clic.

> **Si la connexion échoue,** AMD Sync revient au formulaire en conservant vos valeurs. Les causes habituelles sont SSH désactivé sur le Ryzen AI Halo, un mot de passe erroné, ou les deux appareils se trouvant sur des réseaux différents.

---

## Étape 4 — Lancer votre premier outil à distance

La vue d'accueil vous offre cinq composants en un clic — tous accessibles peu importe le système d'exploitation exécuté par le client et le Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Composant | Fonction |
|-----------|--------------|
| **Directory** | Choisit le dossier sur le Ryzen AI Halo dans lequel VS Code, Terminal et JupyterLab s'ouvriront. La valeur par défaut est un espace de travail géré `Documents/AMD_Sync`. |
| **VS Code** | Ouvre VS Code localement avec un tunnel SSH vers le dossier sélectionné. |
| **Terminal** | Ouvre un terminal local connecté par SSH au Ryzen AI Halo, dans le dossier sélectionné. |
| **JupyterLab** | Lance un projet de cahier connecté par SSH au Ryzen AI Halo, limité au dossier sélectionné. |
| **Live Metrics** | Vue en temps réel de l'utilisation du GPU, de la mémoire et du CPU sur le Ryzen AI Halo. |

### Essayer VS Code

Pour votre premier lancement, essayez **VS Code**.

1. Laissez **Directory** sur la valeur par défaut `~/Documents/AMD_Sync`.
2. Cliquez sur **VS Code**.
3. AMD Sync crée `Documents/AMD_Sync/Project_1` sur le Ryzen AI Halo et ouvre VS Code localement, en tunnel vers celui-ci.

Vous modifiez maintenant des fichiers qui résident sur le Ryzen AI Halo avec votre configuration locale de VS Code. Créez `helloworld.py`, ajoutez `print("hello world")`, ouvrez le terminal intégré (`` Ctrl + ` ``) et exécutez-le :

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barre d'état affiche **SSH: Linux** — la preuve que votre code s'exécute sur le Ryzen AI Halo, et non sur votre ordinateur portable.
### Essayer le terminal

Cliquez sur **Terminal** pour accéder directement au même dossier par SSH sans quitter le clavier.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Sous Windows, le terminal par défaut est **PowerShell** — passez à **Invite de commandes Windows** à partir du menu Paramètres si vous préférez. Sous Linux, AMD Sync utilise le terminal système par défaut.

---

## Fonctionnement du répertoire

Le menu déroulant **Directory** est le contrôle le plus important d'AMD Sync — il détermine où atterrit chaque outil que vous lancez sur le Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (par défaut)** — Le lancement de VS Code ou de JupyterLab à partir d'ici crée automatiquement un nouveau dossier de projet (`Project_1`, `Project_2`, … pour VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … pour JupyterLab).
- **Dossiers de projet existants** — Tout sous-dossier direct de `AMD_Sync` (y compris les dossiers que vous créez manuellement sur le Ryzen AI Halo) apparaît dans le menu déroulant. Le dernier dossier utilisé devient le dossier par défaut la prochaine fois.
- **Chemins personnalisés** — Saisissez un chemin absolu pour ouvrir un dossier ailleurs sur le Ryzen AI Halo. AMD Sync se contente d'*ouvrir* ce dossier — il ne crée pas de dossiers en dehors d'`AMD_Sync`, et les chemins personnalisés ne sont pas enregistrés d'une session à l'autre.

Si un chemin personnalisé ne fonctionne pas, AMD Sync vous indique pourquoi : syntaxe invalide, dossier inexistant ou chemin pointant vers un fichier.

---

## Métriques en temps réel et JupyterLab

- **Live Metrics** — Un tableau de bord en temps réel de l'utilisation du GPU, de la mémoire et du CPU. La façon la plus rapide de confirmer qu'une exécution d'entraînement à distance sollicite bel et bien le matériel.
- **JupyterLab** — Un projet de notebook complet connecté par SSH au Ryzen AI Halo, avec son propre terminal intégré pour combiner cellules de notebook et commandes shell sans quitter l'interface utilisateur.

---

## Paramètres et appareils multiples

Le menu **Settings** comporte trois onglets :

| Onglet | Ce qu'il couvre |
|-----|----------------|
| **Devices** | Répertorie tous les Ryzen AI Halo auxquels vous vous êtes connecté avec succès. Reconnectez-vous, modifiez les identifiants ou ajoutez un nouvel appareil. |
| **Information** | Liens vers la documentation et le soutien sur le forum. |
| **Customize** | Repositionnez l'application sur votre bureau, changez de type de terminal (Windows seulement) et vérifiez les mises à jour d'AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Type de terminal (Windows)** — Choisissez entre **PowerShell** (par défaut) et **Invite de commandes Windows**.
- **Type de terminal (Linux)** — Seul le terminal système par défaut est disponible.
- **Mises à jour de l'application** — Cet onglet est l'endroit idéal pour vérifier et installer les nouvelles versions d'AMD Sync directement depuis l'interface utilisateur; aucun outil de mise à jour distinct n'est nécessaire.

> Un appareil n'apparaît sous **Devices** qu'après une première connexion réussie, de sorte que les tentatives échouées n'encombrent pas la liste.

---

## Dépannage

- **La connexion échoue immédiatement** — Assurez-vous que le serveur SSH est activé dans l'onglet **Remote** du Ryzen AI Halo, dans le Developer Center.
- **Erreur de mot de passe incorrect** — Utilisez votre **mot de passe de connexion du système d'exploitation** sur le Ryzen AI Halo, et non les mots de passe provenant du Developer Center.
- **Le bouton VS Code ne fait rien** — Installez VS Code sur votre machine cliente à partir de [code.visualstudio.com](https://code.visualstudio.com).
- **Icône AMD Sync absente de la zone de notification (Linux/GNOME)** — Installez et activez l'extension AppIndicator.
- **Le fichier `.deb` ne s'ouvre pas depuis le gestionnaire de fichiers** — Utilisez `sudo apt install ./AMDSyncInstaller.deb` à partir d'un terminal.
- **La configuration réapparaît à chaque lancement (Linux)** : déverrouillez votre trousseau de connexion, ou lancez avec `--password-store=gnome-libsecret`, puis refaites la configuration une fois.

---