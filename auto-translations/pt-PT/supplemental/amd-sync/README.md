<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Desenvolvimento Remoto com o AMD Sync

## Visão geral

O **AMD Sync** transforma o seu portátil num cockpit remoto para o AMD Ryzen™ AI Halo. Evite a configuração manual de SSH, chaves e IDE — instale o AMD Sync e obtenha acesso com um clique a um terminal remoto, VS Code, JupyterLab e um painel em tempo real de GPU/CPU/memória no Ryzen AI Halo.

O seu computador local mantém-se familiar; todos os comandos, notebooks e modelos são executados no Ryzen AI Halo.

> **Dica**: Esta página irá conter quaisquer atualizações novas ao AMDSync. 

## O que vai aprender

- Ativar o SSH no Ryzen AI Halo e ligar-se a ele a partir do AMD Sync
- Iniciar o VS Code, Terminal, JupyterLab e Métricas em Tempo Real no Ryzen AI Halo com um clique
- Organizar o trabalho remoto utilizando as pastas de projeto geridas pelo AMD Sync

---

## Conceitos Principais

O AMD Sync tem dois lados: um **cliente** (o seu portátil, com a aplicação AMD Sync em execução) e um **servidor** (o Ryzen AI Halo, com um servidor SSH em execução ao qual o AMD Sync se liga através de um túnel). Tudo o que iniciar a partir do AMD Sync — VS Code, um terminal, um notebook — abre localmente mas é executado no Ryzen AI Halo.

> **Clientes suportados:** Windows 11 e Linux. O macOS não é suportado.

---

## Passo 1 — Ativar o SSH no Ryzen AI Halo


> **Nota:** No Windows, o Ryzen AI Halo vem com o servidor SSH *desativado por predefinição*. No Linux, vem com o servidor SSH *ativado por predefinição*.

1. No Ryzen AI Halo, abra o **AMD Ryzen™ AI Developer Center**.
2. Vá ao separador **Remote**.
3. Ative a opção **SSH Server**.
4. Anote o **IP Address**, o **Port** e o **Username** apresentados em **Server Information** — vai colá-los no AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Nota:** Este é o AMD Developer Center para Windows. A versão Linux pode ter uma interface diferente, mas com funcionalidades remotas semelhantes.

> **Dica:** O AMD Sync pede a **palavra-passe de início de sessão do SO** desse utilizador, e não uma palavra-passe do Developer Center.

---

## Passo 2 — Instalar o AMD Sync no Seu Cliente

O AMD Sync funciona no Windows 11 e no Linux. Transfira o instalador para o seu SO e siga os passos abaixo. Após a instalação, clique em **Accept & Install** no ecrã **Get Started** — o AMD Sync é iniciado automaticamente após a conclusão.

### Windows

[Transferir AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Faça duplo clique em `AMDSyncInstaller.exe`.
2. Clique em **Accept & Install**.

> Se a Firewall do Windows apresentar um aviso, permita o acesso à rede ao AMD Sync para que este possa alcançar o Ryzen AI Halo através de SSH.

### Linux

Clique na ligação para transferir o formato pretendido:

| Formato | Transferência | Comando de instalação |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Nota:** O Ubuntu App Center pode assinalar um ficheiro `.deb` aberto localmente como *"Potencialmente inseguro."* Este é o aviso padrão para qualquer instalador local de terceiros. Se o duplo clique no `.deb` falhar, utilize o comando de terminal acima.

---

## Passo 3 — Ligar ao Seu Ryzen AI Halo

No primeiro arranque, o AMD Sync apresenta o formulário **Add a Remote Device**. Preencha-o utilizando os valores do separador **Remote** do Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Campo | Notas |
|-------|-------|
| **Device Name** *(opcional)* | Um nome amigável como `Ryzen AI Halo`. Por predefinição é `Device 1`, `Device 2`, … |
| **Hostname or IP** | Do separador Remote |
| **SSH Port** | Do separador Remote (apenas números) |
| **Username** | O nome da sua conta do SO no Ryzen AI Halo |
| **Password** | A sua palavra-passe de início de sessão do SO — ocultada enquanto escreve |

Clique em **Add Device**. Após um breve ecrã de carregamento, verá **"Connection Successful"** e chegará à vista principal, que reside na barra de tarefas do sistema. Clique fora da janela para a fechar; o AMD Sync continua em execução e está a um clique de distância.

> **Se a ligação falhar,** o AMD Sync regressa ao formulário com os seus valores preservados. As causas habituais são o SSH estar desativado no Ryzen AI Halo, a palavra-passe estar incorreta, ou os dois dispositivos estarem em redes diferentes.

---

## Passo 4 — Inicie a Sua Primeira Ferramenta Remota

A vista principal disponibiliza cinco componentes de um clique — todos disponíveis independentemente do SO em que o cliente e o Ryzen AI Halo estejam a funcionar.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componente | O que faz |
|-----------|--------------|
| **Directory** | Seleciona a pasta no Ryzen AI Halo em que o VS Code, o Terminal e o JupyterLab irão abrir. Por predefinição, utiliza um espaço de trabalho gerido `Documents/AMD_Sync`. |
| **VS Code** | Abre o VS Code localmente com um túnel SSH para a pasta selecionada. |
| **Terminal** | Abre um terminal local ligado por SSH ao Ryzen AI Halo, na pasta selecionada. |
| **JupyterLab** | Inicia um projeto de notebook ligado por SSH ao Ryzen AI Halo, limitado à pasta selecionada. |
| **Live Metrics** | Vista em tempo real da utilização de GPU, memória e CPU no Ryzen AI Halo. |

### Experimente o VS Code

Para o seu primeiro arranque, experimente o **VS Code**.

1. Deixe **Directory** com a predefinição `~/Documents/AMD_Sync`.
2. Clique em **VS Code**.
3. O AMD Sync cria `Documents/AMD_Sync/Project_1` no Ryzen AI Halo e abre o VS Code localmente, ligado por túnel.

Está agora a editar ficheiros que residem no Ryzen AI Halo com a sua configuração local do VS Code. Crie `helloworld.py`, adicione `print("hello world")`, abra o terminal integrado (`` Ctrl + ` ``) e execute-o:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

A barra de estado apresenta **SSH: Linux** — prova de que o seu código está a ser executado no Ryzen AI Halo, e não no seu portátil.
### Experimente o Terminal

Clique em **Terminal** para aceder à mesma pasta através de SSH sem largar o teclado.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

No Windows, o terminal predefinido é o **PowerShell** — mude para o **Windows Command Prompt** no menu Definições, se preferir. No Linux, o AMD Sync utiliza o terminal predefinido do sistema.

---

## Como Funciona o Diretório

A lista pendente **Diretório** é o controlo mais importante do AMD Sync — decide onde é colocada cada ferramenta que iniciar no Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (predefinição)** — Iniciar o VS Code ou o JupyterLab a partir daqui cria automaticamente uma nova pasta de projeto (`Project_1`, `Project_2`, … para o VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … para o JupyterLab).
- **Pastas de projeto existentes** — Qualquer pasta diretamente contida em `AMD_Sync` (incluindo pastas que crie manualmente no Ryzen AI Halo) aparece na lista pendente. A última pasta utilizada torna-se a predefinição na próxima vez.
- **Caminhos personalizados** — Introduza qualquer caminho absoluto para abrir uma pasta noutro local do Ryzen AI Halo. O AMD Sync apenas *abre* essa pasta — não cria pastas fora de `AMD_Sync`, e os caminhos personalizados não são guardados entre sessões.

Se um caminho personalizado não funcionar, o AMD Sync indica o motivo: sintaxe inválida, a pasta não existe, ou o caminho aponta para um ficheiro.

---

## Métricas em Tempo Real e JupyterLab

- **Métricas em Tempo Real** — Um painel em tempo real de utilização da GPU, memória e CPU. A forma mais rápida de confirmar que uma execução de treino remota está de facto a utilizar o hardware.
- **JupyterLab** — Um projeto de notebook completo ligado por SSH ao Ryzen AI Halo, com o seu próprio terminal integrado para combinar células de notebook com comandos de shell sem sair da interface.

---

## Definições e Vários Dispositivos

O menu **Definições** tem três separadores:

| Separador | O que abrange |
|-----|----------------|
| **Dispositivos** | Lista todos os Ryzen AI Halo aos quais já se ligou com sucesso. Volte a ligar, edite credenciais ou adicione um novo dispositivo. |
| **Informação** | Ligações para documentação e apoio no fórum. |
| **Personalizar** | Reposicione a aplicação no seu ambiente de trabalho, mude o tipo de terminal (apenas Windows) e verifique se existem atualizações do AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipo de terminal (Windows)** — Escolha entre **PowerShell** (predefinição) e **Windows Command Prompt**.
- **Tipo de terminal (Linux)** — Apenas o terminal predefinido do sistema está disponível.
- **Atualizações da aplicação** — Este separador é o local certo para verificar e instalar novas versões do AMD Sync a partir da interface; não é necessário nenhum atualizador em separado.

> Um dispositivo só aparece em **Dispositivos** após uma primeira ligação bem-sucedida, pelo que as tentativas falhadas não sobrecarregam a lista.

---

## Resolução de Problemas

- **A ligação falha imediatamente** — Confirme que o servidor SSH está ativado no separador **Remote** do Ryzen AI Halo, no Developer Center.
- **Erro de palavra-passe incorreta** — Utilize a sua **palavra-passe de início de sessão do SO** no Ryzen AI Halo, e não palavras-passe obtidas no Developer Center.
- **O botão do VS Code não faz nada** — Instale o VS Code na sua máquina cliente a partir de [code.visualstudio.com](https://code.visualstudio.com).
- **Ícone do AMD Sync em falta na área de notificações (Linux/GNOME)** — Instale e ative a extensão AppIndicator.
- **O `.deb` não abre a partir do gestor de ficheiros** — Utilize `sudo apt install ./AMDSyncInstaller.deb` a partir de um terminal.

---