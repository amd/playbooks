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

開発者は、ラベル付きプルリクエストのレビュー、GitHub コメントへの返信、新規イシューのトリアージ、Slack スレッドをスタンドアップメモやインシデント対応に変換する作業、リリースやリサーチのシグナルの追跡など、頻繁に繰り返される小さな作業ループに多くの時間を費やしています。それぞれのループは見慣れたものですが、依然として判断力が求められます。適切なコンテキストを収集し、何が重要かを判断し、チームがすでに作業している場所に明確な更新情報を投稿する必要があります。

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)は、こうしたループをスケジュール実行またはイベントトリガー型のエージェント会話に変換します。これは、AI ソフトウェアエージェントがコンテキストを読み取り、ツールを呼び出し、更新情報を生成する実行のことです。OpenHands 拡張機能カタログに含まれる共有オートメーションテンプレートは、GitHub プルリクエストレビュー、リポジトリ監視、Linear イシュートリアージ、インシデント振り返り、Slack スタンドアップダイジェスト、リサーチブリーフに対して、このパターンに従っています。すなわち、オートメーションが起動し、GitHub や Slack などの設定済みインテグレーションを使ってコンテキストを取得し、そのコンテキストを大規模言語モデル(LLM)で推論し、結果を書き戻すという流れです。

[Agent Canvas](https://github.com/OpenHands/agent-canvas)は、こうしたオートメーションを構築・テストするためのローカルコントロールプレーンです。このプレイブックでは、エージェント会話を実行するバックエンドプロセスである OpenHands Agent Server を実行し、エージェントを GitHub や Slack などの外部サービスに接続します。

ワークフローを AMD システム上に維持するために、エージェントは Lemonade Server が提供するローカルモデルと通信します。Lemonade はそのモデルを OpenAI 互換の API として公開しているため、Agent Canvas はリモートの OpenAI スタイルのエンドポイントとして設定できる一方で、モデル、プロンプト、ワークフローのコンテキストはローカルに保たれます。

このプレイブックでは、具体的なオートメーションを1つ構築します。スケジュール実行される GitHub から Slack への開発ダイジェストです。これは、GitHub を使って最近のリポジトリ活動を確認し、Slack にダイジェストを投稿し、Agent Canvas API 呼び出しでオートメーションを設定・テストし、Lemonade でローカルに LLM を実行します。

![GitHub MCP、OpenHands オートメーション、Lemonade Server、Slack MCP を示すアーキテクチャ図](assets/00-architecture-overview.png)

## このプレイブックで学ぶこと

- Lemonade Server を起動し、ローカルモデルがチャットリクエストに応答することを確認する方法
- Agent Canvas を起動し、その Agent Server をローカル LLM に向ける方法
- Agent Server API を通じて GitHub と Slack の Model Context Protocol (MCP) サーバーをインストールする方法
- Slack に開発ダイジェストを投稿するスケジュール実行の OpenHands オートメーションを作成・実行する方法
- ローカルモデルおよびオートメーションで最もよく発生する障害のトラブルシューティング方法

## 基本概念

| 概念 | 概要 | このプレイブックでの役割 |
| --- | --- | --- |
| Lemonade Server | AMD ハードウェア向けに構築された、OpenAI 互換の API を公開するローカル LLM サービングプラットフォーム。データがマシンの外に出ることはありません。 | エージェントを動かすモデルを実行します。 |
| OpenHands Agent Server | OpenHands エージェント会話を実行するバックエンドプロセス。 | エージェント、その LLM プロファイル、および MCP サーバーをホストします。 |
| Agent Canvas | Agent Server と、エージェントの実行を確認するための UI を実行する OpenHands のローカルコントロールプレーン。 | バックエンドを起動し、呼び出す API を提供します。 |
| MCP server | GitHub や Slack などの外部サービス向けのツールをエージェントに提供する Model Context Protocol サーバー。 | エージェントが GitHub を読み取り、Slack に書き込めるようにします。 |
| OpenHands automation | コンテキストを取得し、それを推論し、どこかに結果を書き込む、スケジュール実行またはイベントトリガー型のエージェント会話。 | ここで構築する GitHub から Slack へのダイジェストです。 |

<!-- @device:stx,krk -->
> [!NOTE]
> コーディングエージェントのワークフローは、より大きなモデルとコンテキストウィンドウの恩恵を受けます。少なくとも 32 GB のシステムメモリを使用し、より大きな GGUF モデルの場合は 64 GB 以上を推奨します。
<!-- @device:end -->

## 前提条件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

以下が必要です。

- 標準の[Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/)に従ってインストールした Lemonade Server。
- 公開されている Agent Canvas CLI をインストールし、`npx` で MCP サーバーを実行するための Node.js 22.12 以降と `npm`。
- スキーマ駆動のエージェント設定、`LLMSummarizingCondenserSettings.max_tokens`、および LLM の `custom_tokenizer` サポートを備えた、最近公開された `@openhands/agent-canvas` パッケージ。
- Agent Server 環境で利用可能な Python の `transformers` パッケージ。`custom_tokenizer` が設定されている場合の、チャットテンプレートのトークンカウントに必要です。
- サマリー対象のリポジトリへの読み取りアクセス権を持つ GitHub トークン。
- `chat:write` およびチャンネル読み取りアクセス権を持つ Slack ボットトークン(`xoxb-...`)。
- Slack チーム ID(`T...`)。
- ダイジェストを投稿する Slack チャンネル ID(`C...`)。

オートメーションをテストする前に、Slack アプリを対象チャンネルに招待してください。

## このプレイブックで使用する変数

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

以下の値は、後の手順で Agent Canvas の UI に入力します。ここで設定しておくと、後でコピーできます。

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

`GITHUB_REPO_FILTER` には明示的な `owner/repo` の値を使用してください。組織全体を対象とする広範なワイルドカードを指定すると、ローカルモデルにとって MCP コンテキストが多すぎる場合があります。

## 1. Lemonade Server を起動する

Lemonade CLI からモデルを起動します。

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade は次の場所に OpenAI 互換の API を公開します。

```text
http://127.0.0.1:13305/api/v1
```

オプション: Agent Canvas またはオートメーションランナーが同じマシン上にない場合は、Lemonade エンドポイントをセキュアトンネル経由で公開し、その HTTPS URL を LLM のベース URL として使用してください。

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. ローカルモデルを確認する

Lemonade が選択したモデルを提供できることを確認します。

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

次に、小さなチャットリクエストを送信します。

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

これが `choices` 配列を返せば、Lemonade は Agent Canvas の準備が整っています。
## 3. Agent Canvas を起動する

公開されている Agent Canvas パッケージをインストールし、フルスタックを起動します。

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

グローバルな npm install がパーミッションエラーで失敗する場合は、下記の npm
パーミッショントラブルシューティングの項目を参照してください。

デフォルトでは、Agent Canvas は `http://localhost:8000` で起動します。そのURLを
ブラウザで開いてください。デフォルトのローカルバックエンドは、ホーム
画面で healthy と表示されるはずです。

`agent-canvas` コマンドは、エージェントサーバー、オートメーションバックエンド、
Webフロントエンドをまとめて起動します。OpenHands をローカルで実行するには、
このコマンド1つだけで十分です。このプレイブックの残りの部分では、ブラウザ内の
Agent Canvas UI を通じてすべてを設定します。

## 4. UI でローカル LLM を設定する

初回起動時、Agent Canvas はオンボーディングフローを開きます。そのフローで:

1. **OpenHands** をエージェントとして選択したままにし、**Next** をクリックします。
2. **Set up your LLM** で、**Advanced** を選択します。
3. **Authentication** は **API key** のままにしておきます。
4. **Custom Model** に `OPENHANDS_LLM_MODEL` の値、
   `openai/Qwen3.6-35B-A3B-GGUF` を設定します。
5. **Base URL** に `http://127.0.0.1:13305/api/v1` を設定します。
6. **API Key** には、`lemonade-local` のような空でないプレースホルダーを
   入力してください。Lemonade は実際のキーを必要としませんが、OpenHands
   クライアントには送信する値が必要です。

接続フィールドは次のようになるはずです。API キーフィールドは UI によって
マスクされます。

![Agent Canvas 初回利用時のLLM Advanced設定画面、Lemonadeモデルとローカルベース URL を表示](assets/01-llm-advanced-settings.png)

続いて **All** を選択し、追加のローカルモデルフィールドを設定します。

1. **Custom Tokenizer** までスクロールし、`Qwen/Qwen3.6-35B-A3B` を設定します。
2. **LiteLLM Extra Body** までスクロールし、
   `{"enable_thinking": true}` を設定します。
3. **Next** をクリックします。

![Agent Canvas 初回利用時のLLM Allタブ、Qwenカスタムトークナイザーを表示](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas 初回利用時のLLM Allタブ、LiteLLM extra bodyの設定を表示](assets/03-llm-all-extra-body-settings.png)

LLM の設定は次のように表示されるはずです。

| フィールド | 値 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` プレフィックスは、Lemonade エンドポイントに対して OpenAI 互換の
リクエストフォーマットを使用するよう LiteLLM に指示します。カスタムトークナイザーは、
GGUF モデル用のオリジナルの Hugging Face トークナイザーであり、これにより
OpenHands は、ローカルモデルサーバーが認識するのと同じチャットテンプレートの
トークンをカウントできるようになります。現在の初回利用時 LLM フォームには、
コンデンサー設定は表示されません。使用している Agent Canvas のビルドで、後から
**Settings > LLM** の下にコンデンサー設定が表示される場合は、`llm_summarizing`
を使用し、最大トークン数を `56000` のように Lemonade のコンテキストウィンドウ
より低い値に設定してください。

## 5. GitHub と Slack の MCP サーバーをインストールする

Agent Canvas の UI で、**Customize**(または **Settings > MCP**)を開き、
エージェントに GitHub と Slack のツールを提供する MCP サーバーを追加します。
トークンの値はローカルの Agent Server にのみ送信され、暗号化された設定として
保存されます。

### GitHub MCP サーバー

次の設定で新しい MCP サーバーを追加します。

| フィールド | 値 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = あなたの GitHub トークン |

要約対象のリポジトリへの読み取りアクセス権を持つ GitHub トークンを使用してください。

### Slack MCP サーバー

次の設定で2つ目の MCP サーバーを追加します。

| フィールド | 値 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = あなたのダイジェストチャンネルID |

`SLACK_CHANNEL_IDS` は、エージェントがすべての Slack チャンネルを
ページングする必要がないように、ダイジェストチャンネルID(`SLACK_DIGEST_CHANNEL`
と同じ値)に設定してください。

両方のサーバーを追加したら、それぞれの **Test** ボタンを使って、接続が確立し
ツールがアドバタイズされることを確認してください。GitHub サーバーは GitHub の
ツールを一覧表示し、Slack サーバーは Slack のツールを一覧表示するはずです。

![GitHubとSlackのサーバーがインストールされたAgent Canvas MCPページ](assets/04-mcp-servers-installed.png)

## 6. ダイジェストオートメーションを作成する

Agent Canvas の UI で **Automations** ページを開き、新しいオートメーションを
作成します。

1. **Create automation** を選択し、**Prompt preset** タイプを選択します。
2. **Name** に `GitHub Development Digest to Slack` を設定します。
3. **Prompt** に次のテキストを設定し、リポジトリとチャンネルのプレースホルダーを
   あなたの値に置き換えます。

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. **Trigger** を **Cron** に設定し、スケジュールを `0 9 * * 1-5`(平日の
   午前9時)にし、**Timezone** をあなたのタイムゾーン、例えば
   `America/New_York` に設定します。
5. **Timeout** を `900` 秒に設定します。
6. オートメーションを保存します。

オートメーションの詳細ページには、新しいオートメーションが cron トリガーと
生成されたプロンプトプリセットのエントリポイントとともに表示されます。

![作成後のAgent Canvasオートメーション詳細画面](assets/05-automation-created.png)
## 7. 自動化のテスト

Agent Canvas UI の自動化詳細ページから:

1. **Run now**(または **Dispatch**)をクリックして、自動化をすぐに1回実行します。
2. 同じページの実行リストを確認します。最新の実行が `COMPLETED` に遷移するはずです。
3. 対象の Slack チャンネルを開きます。生成されたダイジェストが投稿されているはずです。

cron スケジュールの発火を待つ必要はありません。**Run now** はオンデマンドで実行をトリガーするため、スケジュールに任せる前に、プロンプト、MCP 接続、Slack への投稿がすべて機能していることを確認できます。

![Agent Canvas の自動化実行が正常に完了した様子](assets/06-automation-run-completed.png)

![生成された OpenHands ダイジェストが表示された Slack チャンネル](assets/07-slackbot-message.png)

## トラブルシューティング

- **Lemonade が停止している場合:** 手順1の `lemonade run "${LEMONADE_MODEL}"` コマンドで再起動し、ヘルスチェックを再実行してください。
- **`npm install -g` が権限エラーで失敗する場合:** Linux または WSL では、ユーザー所有のグローバル npm ディレクトリを設定し、シェルの起動ファイルに追加した後、Agent Canvas を再度インストールしてください:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  `zsh` を使用している場合は、`~/.bashrc` の代わりに `~/.zshrc` に同じ `export PATH=...` の行を追加してください。
- **`custom_tokenizer` を設定した後、Agent Canvas が LLM 設定を拒否する場合:** Agent Server の Python 環境に `transformers` をインストールし、必要に応じて Agent Canvas を再起動してから、LLM 設定の保存を再試行してください。`custom_tokenizer` が設定されている場合、OpenHands はトークナイザーのチャットテンプレートを読み込むために Transformers を必要とします。
- **Agent Canvas が Lemonade に到達できない場合:** `curl -fsS "${LEMONADE_BASE_URL}/health"` を確認し、初回利用時の LLM フォームまたは **Settings > LLM** に入力したベース URL が、実行中のローカルエンドポイントまたは HTTPS トンネルと一致していることを確認してください。
- **LLM 設定が保存されなかった場合:** 値を入力した後に **Next** をクリックしたことを確認してください。**Settings > LLM** を再度開いて、値が保持されていることを確認してください。
- **GitHub MCP がプライベートリポジトリを参照できない場合:** GitHub トークンが対象リポジトリへの読み取りアクセス権を持っていること、および **Customize** 内の MCP **Test** ボタンが GitHub ツールを表示することを確認してください。
- **Slack がチャンネルを読み取れるが投稿できない場合:** Slack アプリを対象チャンネルに招待し、ボットが `chat:write` 権限を持っていることを確認してください。
- **自動化が Slack チャンネルを多数リストする場合:** Slack チャンネル ID を使用し、**Customize** で Slack MCP サーバーに `SLACK_CHANNEL_IDS` を設定してください。
- **自動化の実行が失敗する、またはコンテキストを超える場合:** Lemonade が `ctx_size=65536` で起動されていることを確認し、OpenHands の LLM に `custom_tokenizer` が設定されていることを確認した上で、GitHub の結果セットを3〜5件に制限した明示的なリポジトリを使用してください。お使いの Agent Canvas ビルドにコンデンサー設定が表示される場合は、コンデンサーの最大トークン数を Lemonade のコンテキストウィンドウより低く設定してください。

## 次のステップ

- 週次のリリースのみのダイジェストを追加する。
- より高速な PR やプッシュ通知のために、GitHub イベントトリガー型の自動化を追加する。
- 同じダイジェストを Notion、Linear、その他の MCP 対応ツールにルーティングする。

## リソース

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server ドキュメント](https://lemonade-server.ai/docs)
- [OpenHands 拡張機能リポジトリ](https://github.com/OpenHands/extensions)
- [Model Context Protocol サーバー](https://github.com/modelcontextprotocol/servers)
- [Slack MCP パッケージ](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)