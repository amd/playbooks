<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概要

[OpenHands](https://github.com/All-Hands-AI/OpenHands) は、コードを書いたり、コマンドを実行したり、Web を閲覧したり、実際のワークスペース内でファイルを編集したりできる AI ソフトウェアエージェントです。チャットウィンドウから提案をコピーする代わりに、エージェントにプロジェクトフォルダを指定し、機能の実装、バグの修正、テストの記述、コードベースの説明といった作業を任せることができます。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) は、OpenHands を実行するために推奨されるブラウザ UI です。1 つの `agent-canvas` コマンドで、エージェントサーバー、自動化バックエンド、Web フロントエンドがまとめて起動するため、ブラウザからエージェントとの会話を進めることができます。

すべてを AMD システム上で完結させるため、エージェントは Lemonade Server が提供するローカルモデルとやり取りします。Lemonade はそのモデルを OpenAI 互換 API として公開するため、Agent Canvas は他の OpenAI 形式のエンドポイントと同様にこれを設定でき、モデル、あなたのコード、会話コンテキストはすべてあなたのマシン上にとどまります。

このプレイブックでは、ローカルモデルを起動し、Agent Canvas を起動してそのモデルを指定し、実際のプロジェクトフォルダに対して最初のコーディングタスクを実行します。

## 学習内容

- Lemonade Server を起動し、ローカルモデルがチャットリクエストに応答することを確認する方法
- npm パッケージから Agent Canvas をインストールして起動する方法
- Agent Canvas を設定して、ローカルの Lemonade モデルを LLM として使用する方法
- OpenHands の会話を開始し、エージェントがワークスペース内でファイルを編集したりコマンドを実行したりする様子を確認する方法
- エージェントが変更した内容を確認し、フォローアップメッセージで操作を誘導する方法

## 中核となる概念

| 概念 | 概要 | このプレイブックでの位置づけ |
| --- | --- | --- |
| Lemonade Server | AMD ハードウェア向けに構築された、OpenAI 互換 API を公開するローカル LLM 提供プラットフォーム。データがマシンの外に出ることはありません。 | エージェントを動かすモデルを実行します。 |
| OpenHands | ワークスペース内でファイルの読み書き、シェルコマンドの実行、Web の閲覧を行う AI ソフトウェアエージェント。 | チャットから操作するエージェントです。 |
| Agent Canvas | OpenHands の会話を実行し、ツール呼び出しやファイル変更を表示するブラウザ UI とバックエンド。 | スタック全体を起動し、会話をホストします。 |
| ワークスペース | エージェントが読み取りおよび変更を許可されているプロジェクトフォルダ。 | エージェントによる編集やコマンドの対象です。 |

<!-- @device:stx,krk -->
> [!NOTE]
> コーディングエージェントのワークフローでは、より大きなモデルとコンテキストウィンドウの恩恵を受けられます。少なくとも 32 GB のシステムメモリを使用し、より大きな GGUF モデルには 64 GB 以上を推奨します。
<!-- @device:end -->

## 前提条件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

以下が必要です:

- 以下のモデルを提供できる状態でインストールされた Lemonade Server。
- Node.js 22.12 以降と `npm`(`agent-canvas` CLI で使用)。
- Agent Canvas がエージェントサーバー環境の管理に使用する Python パッケージマネージャー `uv`。まだシステムにインストールされていない場合は、Agent Canvas を起動する前に [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) からインストールしてください。
- 作業対象となるプロジェクトフォルダ。エージェントに作業させたい任意のローカル git リポジトリまたはコードディレクトリで構いません。

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Lemonade Server を起動する

Lemonade CLI からモデルを起動します:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade は以下の場所に OpenAI 互換 API を公開します:

```text
http://127.0.0.1:13305/api/v1
```



## 2. ローカルモデルを確認する

Lemonade が選択したモデルを提供できることを確認します:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

続いて、簡単なチャットリクエストを送信します:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

これにより `choices` 配列が返される場合、Lemonade は Agent Canvas を使用する準備が整っています。

## 3. Agent Canvas をインストールして起動する

公開されている Agent Canvas パッケージをグローバルにインストールします:

```bash
npm install -g @openhands/agent-canvas
```

続いて、ターミナルからスタック全体を起動します:

```bash
agent-canvas
```

デフォルトでは、Agent Canvas は `http://localhost:8000` で起動します。ブラウザでこの URL を開いてください。ポート 8000 がすでに使用されている場合は、Agent Canvas を起動する際に `--port`(または `-p`)を指定してください:

```bash
agent-canvas --port 3000
```

同じコマンドは Windows の PowerShell でも動作します。その場合は、代わりに `http://localhost:3000` を開いてください。ホーム画面には、デフォルトのローカルバックエンドが正常(healthy)であると表示されるはずです。

`agent-canvas` コマンドは、エージェントサーバー、自動化バックエンド、Web フロントエンドをまとめて起動します。OpenHands をローカルで実行するには、このコマンド 1 つだけで済みます。

## 4. ローカル LLM を設定する

初回起動時、Agent Canvas はオンボーディングフローを開きます。そのフロー内で:

1. エージェントとして **OpenHands** が選択された状態のまま、**Next** をクリックします。
2. **Set up your LLM** で **Advanced** を選択します。
3. **Authentication** を **API key** のままにします。
4. **Custom Model** を `openai/Qwen3.6-35B-A3B-GGUF` に設定します。
5. **Base URL** を `http://127.0.0.1:13305/api/v1` に設定します。
6. **API Key** には、`lemonade-local` のような空でない任意のプレースホルダーを入力します。Lemonade は実際のキーを必要としませんが、OpenHands クライアント側は何らかの値を送信する必要があります。
7. **Next** をクリックします。

完了した Advanced 設定は次のようになります。API キーフィールドは UI 上でマスクされます。

![Agent Canvas first-use LLM Advanced settings with the Lemonade model and local base URL](assets/01-llm-advanced-settings.png)

Agent Canvas はこれらの値を LLM プロファイルとして保存します。使用しているバージョンでプロファイル名の入力を求められた場合は、`lemonade-local` のようにスペースを含まない名前を使用してください。後でモデルを変更する場合は、**Settings > LLM** を開き、同じ Advanced フィールドを更新してください。チャット入力欄から `/model` コマンドで保存済みのプロファイルを切り替えることもできます。

## 5. ワークスペースを開く

エージェントは、あなたが選択したワークスペース内のファイルのみを読み取りおよび変更できます。タスクを開始する前に、Agent Canvas にプロジェクトフォルダを指定してください:

1. ホーム画面から **Open Workspace** を選択します。
2. プロジェクトが含まれるフォルダ(たとえば、エージェントに作業させたい git リポジトリ)を選択します。
3. そのワークスペースで新しい会話を開始します。

エージェントが行うこと(ファイルの読み取り、コマンドの実行、コードの編集)はすべて、そのワークスペースに限定されます。

![Agent Canvas home after onboarding](assets/02-agent-canvas-home.png)
## 6. 最初のコーディングタスクを実行する

ワークスペースを開き、ローカル LLM を選択したら、具体的なタスクをチャットに入力します。最初のタスクとしては、小さくて検証しやすいものが適しています。例えば次のようなものです。

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

会話のタイムラインを見守ってください。OpenHands は以下を行います。

- ワークスペースを読み取り、構成を把握する。
- 要求された関数とテストブロックを含む `hello.py` を作成する。
- 必要に応じて `python3 hello.py` を実行し、出力を検証する。
- 実行内容と、コマンドの出力があればそれをチャットで報告する。

ワークスペースに新しいファイルが表示され、エージェントの最終メッセージにはそれが行った変更の説明が記載されているはずです。これがまさに成果が得られる瞬間です。エージェントがあなたのプロジェクトフォルダー内で実際にコードを書き、実行したのです。

## 7. エージェントのレビューと誘導

エージェントがあるステップを終えたら、次のステップを進める前にその作業内容を確認してください。

- **ファイルの変更**: ワークスペースのファイルブラウザーやエージェントの差分ビューを使って、追加・変更・削除された内容を正確に確認します。
- **コマンドの出力**: エージェントが実行したコマンドを展開し、標準出力、標準エラー出力、終了コードを確認します。
- **フォローアップ**: 結果が期待どおりでない場合は、同じ会話の中で修正内容を返信してください。エージェントはそれまでの文脈を保持したまま、同じファイルに対して作業を続けます。

例えば、テストが期待していた挨拶を出力しなかった場合は、次のように返信します。

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

エージェントはファイルを再読み込みし、コマンドを実行し、問題を診断したうえで、同じ会話の中でファイルを再び編集します。

## トラブルシューティング

- **`agent-canvas` が PATH に存在しない場合:** `npm install -g @openhands/agent-canvas` で再インストールし、npm のグローバルバイナリディレクトリが PATH に含まれていることを確認してください。Windows では `npm config get prefix` を実行してください。返されたディレクトリ(多くの場合 `%APPDATA%\npm` または `%USERPROFILE%\.npm-global`)は、新しいターミナルから `agent-canvas` を起動できるようにするために、ユーザー PATH に含まれている必要があります。
- **`npm install -g` が権限エラーで失敗する場合:** ユーザー所有のグローバル npm ディレクトリを設定し、ターミナルを再度開いてから、Agent Canvas を再インストールしてください。

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Windows の PATH 変更を恒久的に反映させるには、**設定 > システム > バージョン情報 > システムの詳細設定 > 環境変数** から `%USERPROFILE%\.npm-global` をユーザー PATH に追加し、新しいターミナルを開いてください。
  <!-- @os:end -->
- **UI は読み込まれるが、バックエンドが unhealthy と表示される場合:** エージェントサーバーの起動が完了するまで数秒待ってから、再読み込みしてください。それでも unhealthy のままであれば、`agent-canvas` を再起動し、ターミナルの出力でエラーがないか確認してください。
- **Lemonade へのチャットリクエストが接続エラーで失敗する場合:** `curl -fsS "http://127.0.0.1:13305/api/v1/health"` が成功すること、および `lemonade status` で Lemonade がまだそのモデルを提供中であることを確認してください。
- **エージェントがコンテキスト長やトークン数の上限に関するエラーを出す場合:** より大きな `ctx_size`(例: `ctx_size=65536`)を指定して Lemonade を再起動し、新しい会話を開始することで、エージェントが過大な履歴を引き継がないようにしてください。
- **エージェントの生成する編集内容が低品質または不完全な場合:** Lemonade でより大きなモデルに切り替えるか、エージェントにより小さく具体的なタスクを与え、それを完了させてから次の変更を依頼してください。
- **`uv` が見つからない場合:** [uv のインストールガイド](https://docs.astral.sh/uv/getting-started/installation/)からインストールしてください。Agent Canvas は `uv` を使ってエージェントサーバーの Python 環境を管理します。

## 次のステップ

- 同じワークスペースでより大きなタスク、例えばユニットテストファイルの追加や既知のバグの修正などを試し、変更を確定させる前にエージェントの差分を確認してみましょう。
- **カスタマイズ** の下で GitHub や Slack などの MCP サーバーを接続すると、エージェントが作業中に issue を読んだり、更新を投稿したりできるようになります。
- 複数の LLM プロファイル(高速な小規模モデルと、より高性能な大規模モデル)を保存しておき、会話の途中で `/model` を使って切り替えてみましょう。
- 次は [OpenHands のオートメーション](https://docs.openhands.dev/openhands/usage/automations/overview)に進み、繰り返し発生する開発作業のループを、スケジュール実行またはイベント駆動のエージェント実行に変換してみましょう。

## 参考資料

- [OpenHands ドキュメント](https://docs.openhands.dev/)
- [Agent Canvas の概要](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas のセットアップ](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM プロファイルとモデル設定](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server ドキュメント](https://lemonade-server.ai/docs)