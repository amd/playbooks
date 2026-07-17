<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Développement à distance avec AMD Sync

## Vue d'ensemble

**AMD Sync** transforme votre ordinateur portable en cockpit distant pour le AMD Ryzen™ AI Halo. Oubliez la configuration manuelle de SSH, des clés et de l'IDE — installez AMD Sync et accédez en un clic à un terminal distant, VS Code, JupyterLab, ainsi qu'un tableau de bord en direct GPU/CPU/mémoire sur le Ryzen AI Halo.

Votre machine locale reste familière ; chaque commande, notebook et modèle s'exécute sur le Ryzen AI Halo.

> **Conseil** : Cette page contiendra toutes les nouvelles mises à jour d'AMDSync.

## Ce que vous apprendrez

- Activer SSH sur le Ryzen AI Halo et s'y connecter depuis AMD Sync
- Lancer VS Code, Terminal, JupyterLab et les métriques en direct sur le Ryzen AI Halo en un seul clic
- Organiser le travail à distance à l'aide des dossiers de projet gérés par AMD Sync

---

## Concepts fondamentaux

AMD Sync comporte deux côtés : un **client** (votre ordinateur portable, exécutant l'application AMD Sync) et un **serveur** (le Ryzen AI Halo, exécutant un serveur SSH dans lequel AMD Sync crée un tunnel). Tout ce que vous lancez depuis AMD Sync — VS Code, un terminal, un notebook — s'ouvre localement mais s'exécute sur le Ryzen AI Halo.

> **Clients pris en charge :** Windows 11 et Linux. macOS n'est pas pris en charge.

---

## Étape 1 — Activer SSH sur le Ryzen AI Halo


> **Remarque :** Sous Windows, le Ryzen AI Halo est livré avec le serveur SSH *désactivé par défaut*. Sous Linux, il est livré avec le serveur SSH *activé par défaut*.

1. Sur le Ryzen AI Halo, ouvrez le **AMD Ryzen™ AI Developer Center**.
2. Accédez à l'onglet **Remote**.
3. Activez le **SSH Server**.
4. Notez l'**adresse IP**, le **port** et le **nom d'utilisateur** affichés sous **Server Information** — vous les saisirez dans AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Remarque :** Il s'agit du AMD Developer Center pour Windows. Celui pour Linux peut avoir une interface différente, mais des fonctionnalités distantes similaires.

> **Conseil :** AMD Sync demande le **mot de passe de connexion OS** de cet utilisateur, et non un mot de passe provenant du Developer Center.

---

## Étape 2 — Installer AMD Sync sur votre client

AMD Sync fonctionne sur Windows 11 et Linux. Téléchargez le programme d'installation pour votre système d'exploitation, puis suivez les étapes ci-dessous. Après l'installation, cliquez sur **Accept & Install** sur l'écran **Get Started** — AMD Sync se lance automatiquement une fois terminé.

### Windows

[Télécharger AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Double-cliquez sur `AMDSyncInstaller.exe`.
2. Cliquez sur **Accept & Install**.

> Si le pare-feu Windows vous y invite, autorisez l'accès réseau d'AMD Sync afin qu'il puisse atteindre le Ryzen AI Halo via SSH.

### Linux

Cliquez sur le lien pour télécharger le format de votre choix :

| Format | Téléchargement | Commande d'installation |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Remarque :** L'Ubuntu App Center peut signaler un fichier `.deb` ouvert localement comme *« Potentiellement dangereux »*. Il s'agit de l'avertissement standard pour tout programme d'installation tiers local. Si un double-clic sur le fichier `.deb` échoue, utilisez la commande terminal ci-dessus.

---

## Étape 3 — Se connecter à votre Ryzen AI Halo

Au premier lancement, AMD Sync affiche le formulaire **Add a Remote Device**. Remplissez-le avec les valeurs de l'onglet **Remote** du Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Champ | Remarques |
|-------|-------|
| **Device Name** *(facultatif)* | Un libellé convivial comme `Ryzen AI Halo`. Par défaut : `Device 1`, `Device 2`, … |
| **Hostname or IP** | Depuis l'onglet Remote |
| **SSH Port** | Depuis l'onglet Remote (chiffres uniquement) |
| **Username** | Le nom de votre compte OS sur le Ryzen AI Halo |
| **Password** | Votre mot de passe de connexion OS — masqué à la saisie |

Cliquez sur **Add Device**. Après un bref écran de chargement, vous verrez **« Connection Successful »** et arriverez sur la vue d'accueil, qui réside dans votre barre des tâches. Cliquez en dehors de la fenêtre pour la fermer ; AMD Sync continue de fonctionner et est accessible en un clic.

> **Si la connexion échoue,** AMD Sync revient au formulaire avec vos valeurs conservées. Les causes habituelles sont : SSH désactivé sur le Ryzen AI Halo, mot de passe incorrect, ou les deux appareils se trouvant sur des réseaux différents.

---

## Étape 4 — Lancer votre premier outil distant

La vue d'accueil vous propose cinq composants accessibles en un clic — tous disponibles quel que soit le système d'exploitation du client et du Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Composant | Ce qu'il fait |
|-----------|--------------|
| **Directory** | Sélectionne le dossier sur le Ryzen AI Halo dans lequel VS Code, Terminal et JupyterLab s'ouvriront. Par défaut, un espace de travail géré `Documents/AMD_Sync`. |
| **VS Code** | Ouvre VS Code localement avec un tunnel SSH vers le dossier sélectionné. |
| **Terminal** | Ouvre un terminal local connecté en SSH au Ryzen AI Halo, dans le dossier sélectionné. |
| **JupyterLab** | Lance un projet de notebook connecté en SSH au Ryzen AI Halo, limité au dossier sélectionné. |
| **Live Metrics** | Vue en temps réel de l'utilisation du GPU, de la mémoire et du CPU sur le Ryzen AI Halo. |

### Essayer VS Code

Pour votre premier lancement, essayez **VS Code**.

1. Laissez **Directory** sur la valeur par défaut `~/Documents/AMD_Sync`.
2. Cliquez sur **VS Code**.
3. AMD Sync crée `Documents/AMD_Sync/Project_1` sur le Ryzen AI Halo et ouvre VS Code localement, avec un tunnel vers ce dossier.

Vous modifiez maintenant des fichiers qui résident sur le Ryzen AI Halo avec votre configuration VS Code locale. Créez `helloworld.py`, ajoutez `print("hello world")`, ouvrez le terminal intégré (`` Ctrl + ` ``), et exécutez-le :

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barre d'état affiche **SSH: Linux** — preuve que votre code s'exécute sur le Ryzen AI Halo, et non sur votre ordinateur portable.

### Essayer le Terminal

Cliquez sur **Terminal** pour accéder au même dossier via SSH sans quitter le clavier.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Sous Windows, le terminal par défaut est **PowerShell** — passez à **Windows Command Prompt** depuis le menu Paramètres si vous préférez. Sous Linux, AMD Sync utilise votre terminal système par défaut.

---

## Fonctionnement du répertoire

Le menu déroulant **Directory** est le contrôle le plus important dans AMD Sync — il détermine l'emplacement sur le Ryzen AI Halo où chaque outil que vous lancez sera ouvert.

- **`~/Documents/AMD_Sync` (par défaut)** — Lancer VS Code ou JupyterLab depuis ici crée automatiquement un nouveau dossier de projet (`Project_1`, `Project_2`, … pour VS Code ; `Notebook_Project_1`, `Notebook_Project_2`, … pour JupyterLab).
- **Dossiers de projet existants** — Tout enfant direct de `AMD_Sync` (y compris les dossiers que vous créez manuellement sur le Ryzen AI Halo) apparaît dans le menu déroulant. Le dernier dossier utilisé devient le dossier par défaut la prochaine fois.
- **Chemins personnalisés** — Saisissez n'importe quel chemin absolu pour ouvrir un dossier ailleurs sur le Ryzen AI Halo. AMD Sync se contente de l'*ouvrir* — il ne créera pas de dossiers en dehors de `AMD_Sync`, et les chemins personnalisés ne sont pas sauvegardés entre les sessions.

Si un chemin personnalisé ne fonctionne pas, AMD Sync vous en indique la raison : syntaxe invalide, dossier inexistant, ou le chemin pointe vers un fichier.

---

## Métriques en direct et JupyterLab

- **Live Metrics** — Un tableau de bord en direct de l'utilisation du GPU, de la mémoire et du CPU. Le moyen le plus rapide de confirmer qu'une exécution d'entraînement à distance sollicite bien le matériel.
- **JupyterLab** — Un projet de notebook complet connecté en SSH au Ryzen AI Halo, avec son propre terminal intégré pour mélanger cellules de notebook et commandes shell sans quitter l'interface.

---

## Paramètres et appareils multiples

Le menu **Settings** comporte trois onglets :

| Onglet | Ce qu'il couvre |
|-----|----------------|
| **Devices** | Liste tous les Ryzen AI Halo auxquels vous vous êtes connecté avec succès. Reconnectez-vous, modifiez les identifiants ou ajoutez un nouvel appareil. |
| **Information** | Liens vers la documentation et le support du forum. |
| **Customize** | Repositionnez l'application sur votre bureau, changez le type de terminal (Windows uniquement) et vérifiez les mises à jour d'AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Type de terminal (Windows)** — Choisissez entre **PowerShell** (par défaut) et **Windows Command Prompt**.
- **Type de terminal (Linux)** — Seul le terminal système par défaut est disponible.
- **Mises à jour de l'application** — Cet onglet est l'endroit approprié pour vérifier et installer les nouvelles versions d'AMD Sync depuis l'interface ; aucun programme de mise à jour séparé n'est nécessaire.

> Un appareil n'apparaît sous **Devices** qu'après une première connexion réussie, de sorte que les tentatives échouées n'encombreront pas la liste.

---

## Dépannage

- **La connexion échoue immédiatement** — Vérifiez que le serveur SSH est activé dans l'onglet **Remote** du Developer Center sur le Ryzen AI Halo.
- **Erreur de mot de passe incorrect** — Utilisez votre **mot de passe de connexion OS** sur le Ryzen AI Halo, et non des mots de passe provenant du Developer Center.
- **Le bouton VS Code ne fait rien** — Installez VS Code sur votre machine cliente depuis [code.visualstudio.com](https://code.visualstudio.com).
- **Icône AMD Sync manquante dans la barre des tâches (Linux/GNOME)** — Installez et activez l'extension AppIndicator.
- **Le fichier `.deb` ne s'ouvre pas depuis le gestionnaire de fichiers** — Utilisez `sudo apt install ./AMDSyncInstaller.deb` depuis un terminal.

---