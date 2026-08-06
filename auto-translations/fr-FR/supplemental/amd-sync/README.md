<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Développement à distance avec AMD Sync

## Présentation

**AMD Sync** transforme votre ordinateur portable en un poste de pilotage à distance pour l'AMD Ryzen™ AI Halo. Oubliez la configuration manuelle de SSH, des clés et de l'IDE — installez AMD Sync et bénéficiez d'un accès en un clic à un terminal distant, à VS Code, à JupyterLab et à un tableau de bord en direct GPU/CPU/mémoire sur le Ryzen AI Halo.

Votre machine locale reste familière ; chaque commande, notebook et modèle s'exécute sur le Ryzen AI Halo.

> **Astuce** : Cette page contiendra toutes les nouvelles mises à jour d'AMDSync. 

## Ce que vous allez apprendre

- Activer SSH sur le Ryzen AI Halo et vous y connecter depuis AMD Sync
- Lancer VS Code, Terminal, JupyterLab et Live Metrics sur le Ryzen AI Halo en un clic
- Organiser le travail à distance à l'aide des dossiers de projet gérés par AMD Sync

---

## Concepts fondamentaux

AMD Sync comporte deux volets : un **client** (votre ordinateur portable, exécutant l'application AMD Sync) et un **serveur** (le Ryzen AI Halo, exécutant un serveur SSH vers lequel AMD Sync établit un tunnel). Tout ce que vous lancez depuis AMD Sync — VS Code, un terminal, un notebook — s'ouvre localement mais s'exécute sur le Ryzen AI Halo.

> **Clients pris en charge :** Windows 11 et Linux. macOS n'est pas pris en charge.

---

## Étape 1 — Activer SSH sur le Ryzen AI Halo


> **Remarque :** Sur Windows, le Ryzen AI Halo est livré avec le serveur SSH *désactivé par défaut*. Sur Linux, il est livré avec le serveur SSH *activé par défaut*.

1. Sur le Ryzen AI Halo, ouvrez l'**AMD Ryzen™ AI Developer Center**.
2. Accédez à l'onglet **Remote**.
3. Activez **SSH Server**.
4. Notez l'**IP Address**, le **Port** et le **Username** affichés sous **Server Information** — vous les collerez dans AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Remarque :** Il s'agit de l'AMD Developer Center pour Windows. Celui de Linux peut présenter une interface différente, mais des fonctionnalités distantes similaires.

> **Astuce :** AMD Sync demande le **mot de passe de connexion au système d'exploitation** de cet utilisateur, et non un mot de passe du Developer Center.

---

## Étape 2 — Installer AMD Sync sur votre client

AMD Sync fonctionne sous Windows 11 et Linux. Téléchargez le programme d'installation correspondant à votre système d'exploitation, puis suivez les étapes ci-dessous. Après l'installation, cliquez sur **Accept & Install** sur l'écran **Get Started** — AMD Sync se lance automatiquement une fois l'opération terminée.

### Windows

[Télécharger AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Double-cliquez sur `AMDSyncInstaller.exe`.
2. Cliquez sur **Accept & Install**.

> Si le pare-feu Windows vous le demande, autorisez l'accès réseau d'AMD Sync afin qu'il puisse atteindre le Ryzen AI Halo via SSH.

### Linux

Cliquez sur le lien pour télécharger le format de votre choix :

| Format | Téléchargement | Commande d'installation |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Remarque :** L'App Center d'Ubuntu peut signaler un fichier `.deb` ouvert localement comme *« Potentiellement dangereux »*. Il s'agit de l'avertissement standard pour tout programme d'installation local tiers. Si le double-clic sur le `.deb` échoue, utilisez la commande de terminal ci-dessus.

---

## Étape 3 — Se connecter à votre Ryzen AI Halo

Au premier lancement, AMD Sync affiche le formulaire **Add a Remote Device**. Remplissez-le à l'aide des valeurs de l'onglet **Remote** du Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Champ | Remarques |
|-------|-------|
| **Device Name** *(facultatif)* | Un nom convivial comme `Ryzen AI Halo`. Par défaut : `Device 1`, `Device 2`, … |
| **Hostname or IP** | Depuis l'onglet Remote |
| **SSH Port** | Depuis l'onglet Remote (chiffres uniquement) |
| **Username** | Le nom de votre compte système sur le Ryzen AI Halo |
| **Password** | Votre mot de passe de connexion au système d'exploitation — masqué lors de la saisie |

Cliquez sur **Add Device**. Après un bref écran de chargement, vous verrez apparaître **« Connection Successful »** et arriverez sur la vue d'accueil, qui réside dans votre barre d'état système. Cliquez en dehors de la fenêtre pour la fermer ; AMD Sync continue de fonctionner en arrière-plan et reste accessible en un clic.

> **En cas d'échec de la connexion,** AMD Sync revient au formulaire en conservant vos valeurs. Les causes habituelles sont SSH désactivé sur le Ryzen AI Halo, un mot de passe incorrect, ou les deux appareils se trouvant sur des réseaux différents.

---

## Étape 4 — Lancer votre premier outil distant

La vue d'accueil vous propose cinq composants accessibles en un clic — tous disponibles quel que soit le système d'exploitation du client et du Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Composant | Fonction |
|-----------|--------------|
| **Directory** | Sélectionne le dossier sur le Ryzen AI Halo dans lequel VS Code, Terminal et JupyterLab s'ouvriront. Par défaut, un espace de travail géré `Documents/AMD_Sync`. |
| **VS Code** | Ouvre VS Code localement avec un tunnel SSH vers le dossier sélectionné. |
| **Terminal** | Ouvre un terminal local connecté en SSH au Ryzen AI Halo, dans le dossier sélectionné. |
| **JupyterLab** | Lance un projet notebook connecté en SSH au Ryzen AI Halo, limité au dossier sélectionné. |
| **Live Metrics** | Vue en temps réel de l'utilisation du GPU, de la mémoire et du CPU sur le Ryzen AI Halo. |

### Essayer VS Code

Pour votre premier lancement, essayez **VS Code**.

1. Laissez **Directory** sur la valeur par défaut `~/Documents/AMD_Sync`.
2. Cliquez sur **VS Code**.
3. AMD Sync crée `Documents/AMD_Sync/Project_1` sur le Ryzen AI Halo et ouvre VS Code localement, avec un tunnel vers ce dossier.

Vous êtes maintenant en train de modifier des fichiers hébergés sur le Ryzen AI Halo avec votre configuration VS Code locale. Créez `helloworld.py`, ajoutez `print("hello world")`, ouvrez le terminal intégré (`` Ctrl + ` ``) et exécutez-le :

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barre d'état affiche **SSH: Linux** — preuve que votre code s'exécute sur le Ryzen AI Halo, et non sur votre ordinateur portable.
### Essayez le Terminal

Cliquez sur **Terminal** pour accéder au même dossier via SSH sans quitter le clavier.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Sous Windows, le terminal par défaut est **PowerShell** — passez à **Windows Command Prompt** depuis le menu Paramètres si vous préférez. Sous Linux, AMD Sync utilise le terminal système par défaut.

---

## Fonctionnement du répertoire

La liste déroulante **Directory** est le contrôle le plus important d'AMD Sync — c'est elle qui détermine où atterrit chaque outil que vous lancez sur le Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (par défaut)** — Lancer VS Code ou JupyterLab depuis cet emplacement crée automatiquement un nouveau dossier de projet (`Project_1`, `Project_2`, … pour VS Code ; `Notebook_Project_1`, `Notebook_Project_2`, … pour JupyterLab).
- **Dossiers de projet existants** — Tout sous-dossier direct de `AMD_Sync` (y compris les dossiers que vous créez manuellement sur le Ryzen AI Halo) apparaît dans la liste déroulante. Le dernier dossier utilisé devient le dossier par défaut la fois suivante.
- **Chemins personnalisés** — Saisissez n'importe quel chemin absolu pour ouvrir un dossier ailleurs sur le Ryzen AI Halo. AMD Sync se contente d'*ouvrir* ce dossier — il ne créera pas de dossiers en dehors de `AMD_Sync`, et les chemins personnalisés ne sont pas enregistrés d'une session à l'autre.

Si un chemin personnalisé ne fonctionne pas, AMD Sync vous indique pourquoi : syntaxe invalide, dossier inexistant, ou chemin pointant vers un fichier.

---

## Métriques en direct et JupyterLab

- **Live Metrics** — Un tableau de bord en direct de l'utilisation du GPU, de la mémoire et du CPU. Le moyen le plus rapide de vérifier qu'un entraînement distant sollicite réellement le matériel.
- **JupyterLab** — Un projet de notebook complet connecté en SSH au Ryzen AI Halo, avec son propre terminal intégré pour combiner cellules de notebook et commandes shell sans quitter l'interface.

---

## Paramètres et appareils multiples

Le menu **Settings** comporte trois onglets :

| Onglet | Contenu |
|-----|----------------|
| **Devices** | Répertorie tous les Ryzen AI Halo auxquels vous vous êtes connecté avec succès. Reconnectez-vous, modifiez les identifiants, ou ajoutez un nouvel appareil. |
| **Information** | Liens vers la documentation et l'assistance sur le forum. |
| **Customize** | Repositionnez l'application sur votre bureau, changez le type de terminal (Windows uniquement), et vérifiez les mises à jour d'AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Type de terminal (Windows)** — Choisissez entre **PowerShell** (par défaut) et **Windows Command Prompt**.
- **Type de terminal (Linux)** — Seul le terminal système par défaut est disponible.
- **Mises à jour de l'application** — Cet onglet est l'endroit idéal pour rechercher et installer de nouvelles versions d'AMD Sync directement depuis l'interface ; aucun outil de mise à jour séparé n'est nécessaire.

> Un appareil n'apparaît sous **Devices** qu'après une première connexion réussie, de sorte que les tentatives échouées n'encombrent pas la liste.

---

## Dépannage

- **La connexion échoue immédiatement** — Vérifiez que le serveur SSH est activé sur l'onglet **Remote** du Developer Center du Ryzen AI Halo.
- **Erreur de mot de passe incorrect** — Utilisez votre **mot de passe de connexion au système d'exploitation** sur le Ryzen AI Halo, et non des mots de passe provenant du Developer Center.
- **Le bouton VS Code ne fait rien** — Installez VS Code sur votre machine cliente depuis [code.visualstudio.com](https://code.visualstudio.com).
- **Icône de la barre d'état AMD Sync manquante (Linux/GNOME)** — Installez et activez l'extension AppIndicator.
- **Le fichier `.deb` ne s'ouvre pas depuis le gestionnaire de fichiers** — Utilisez `sudo apt install ./AMDSyncInstaller.deb` depuis un terminal.

---