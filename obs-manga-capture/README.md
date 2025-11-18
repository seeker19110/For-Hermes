# 📚 OBS漫画自動キャプチャ＆文字起こしシステム

**12-Factor Agents** の原則に基づいて構築された、漫画の自動記録システムです。

OBS Studio で漫画を表示し、ページをめくると自動的にスクリーンショットを撮影し、Vision LLMでセリフを文字起こしして記録します。

## ✨ 特徴

- 🎥 **OBS Studio統合** - WebSocket経由で自動キャプチャ
- 📖 **自動ページ検知** - 画像差分でページめくりを検出
- 🤖 **AI文字起こし** - GPT-4V、Claude、Geminiでセリフを抽出
- 💾 **構造化データ保存** - JSON形式でセリフ、ナレーション、効果音を記録
- ⏸️ **Pause/Resume対応** - いつでも停止・再開可能
- 🎯 **12-Factor Agents準拠** - 本番レベルの信頼性とメンテナンス性

## 🏗️ アーキテクチャ

### 12-Factor Agentsの適用

| Factor | 実装内容 |
|--------|---------|
| **Factor 1** | 画像→セリフ抽出のツール呼び出しパターン |
| **Factor 2** | Vision LLMプロンプトをBAMLで完全管理 |
| **Factor 3** | キャプチャ履歴をコンテキストとして管理 |
| **Factor 4** | セリフデータを構造化出力（TypeScript型付き） |
| **Factor 5** | キャプチャ状態とセリフ記録の統合管理 |
| **Factor 6** | Launch/Pause/Resume API実装 |
| **Factor 8** | ページ検知→キャプチャ→文字起こしフローの完全制御 |

### システム構成

```
┌─────────────────┐
│  OBS Studio     │  漫画を表示
│  (漫画表示)      │
└────────┬────────┘
         │ WebSocket / システムキャプチャ
         ↓
┌─────────────────┐     ┌──────────────┐
│ CaptureManager  │ →  │ PageDetector │
│ (スクリーンショット) │     │ (差分検出)   │
└────────┬────────┘     └──────────────┘
         │ 新ページ検知
         ↓
┌─────────────────┐     ┌──────────────┐
│ VisionLLMManager│ →  │ BAML Prompts │
│ (文字起こし)     │     │ (構造化出力)  │
└────────┬────────┘     └──────────────┘
         │
         ↓
┌─────────────────┐
│ CaptureSession  │  JSON保存
│ (状態管理)       │
└─────────────────┘
```

## 📦 インストール

### 前提条件

- Node.js 20+
- OBS Studio 28+ (オプション、なくても動作可能)
- OpenAI/Anthropic/Google API キー

### セットアップ手順

```bash
# 1. リポジトリをクローン
cd 12-factor-agents_fork/obs-manga-capture

# 2. 依存関係をインストール
npm install

# 3. BAML初期化と生成
npx baml-cli init
npx baml-cli generate

# 4. 環境変数を設定
cp .env.example .env
# .env ファイルを編集してAPIキーを設定

# 5. OBS Studioを起動してWebSocketを有効化
# ツール > WebSocketサーバー設定
# ポート: 4455（デフォルト）
# パスワードを設定する場合は .env に記載
```

### 環境変数設定

`.env` ファイルを編集：

```env
# Vision LLM APIキー（いずれか1つ）
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...

# OBS WebSocket
OBS_WEBSOCKET_URL=ws://localhost:4455
OBS_WEBSOCKET_PASSWORD=your_password

# ディレクトリ設定
CAPTURE_DIR=./captures
OUTPUT_DIR=./output

# キャプチャ設定
CAPTURE_INTERVAL_MS=1000
PAGE_CHANGE_THRESHOLD=0.15
IMAGE_SIMILARITY_THRESHOLD=0.85

# LLMプロバイダー
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

## 🚀 使用方法

### 基本的な使い方

#### 1. キャプチャモード（リアルタイム）

```bash
# OBSで漫画を表示し、ページをめくると自動キャプチャ
npm run dev capture
```

**動作:**
1. OBSで漫画を表示
2. ページをめくる
3. 自動的にスクリーンショットを撮影
4. ページ検知（画像差分）
5. Vision LLMで文字起こし
6. JSON形式で保存

#### 2. 処理モード（バッチ処理）

```bash
# 未処理のページをまとめて文字起こし
npm run dev process --sessionId=<session-id>
```

#### 3. モックモード（テスト用）

```bash
# APIキーなしでテスト
npm run dev capture --mock
```

### コマンドオプション

```bash
# OBSなしでシステムキャプチャを使用
npm run dev capture --no-obs

# キャプチャ間隔を変更（ミリ秒）
npm run dev capture --interval=2000

# ヘルプ表示
npm run dev help
```

## 📊 出力形式

### JSON形式（session-xxx.json）

```json
{
  "sessionId": "1234567890-abc123",
  "startTime": 1640000000000,
  "endTime": 1640001000000,
  "totalPages": 10,
  "pages": [
    {
      "pageNumber": 1,
      "timestamp": 1640000000000,
      "imagePath": "captures/capture-1640000000000.png",
      "processed": true,
      "transcription": {
        "page_number": 1,
        "speech_bubbles": [
          {
            "speaker": "主人公",
            "text": "やっと見つけた！",
            "position": "top-right",
            "reading_order": 1
          },
          {
            "text": "これが伝説の剣か...",
            "position": "bottom-left",
            "reading_order": 2
          }
        ],
        "narrations": [
          {
            "text": "長い旅の末、ついに目的地に辿り着いた",
            "position": "top-center"
          }
        ],
        "sound_effects": ["ゴゴゴゴ", "キラーン"],
        "page_description": "主人公が洞窟で剣を発見するシーン",
        "has_text": true
      }
    }
  ]
}
```

### Markdown形式（オプション）

```markdown
# 漫画文字起こし

生成日時: 2025-01-15 10:30:00
総ページ数: 10

---

=== ページ 1 ===

【概要】
主人公が洞窟で剣を発見するシーン

【セリフ】
  1. 主人公:「やっと見つけた！」 (top-right)
  2. 「これが伝説の剣か...」 (bottom-left)

【ナレーション】
  1. 長い旅の末、ついに目的地に辿り着いた (top-center)

【効果音】
  ゴゴゴゴ, キラーン

---
```

## 🎯 高度な使い方

### カスタムプロンプトの編集

`baml_src/manga-ocr.baml` を編集してプロンプトをカスタマイズ：

```rust
function TranscribeMangaPage(
  image_path string,
  page_number int?
) -> MangaPageTranscription {
  client GPT4Vision

  prompt #"
    {{ _.role("system") }}

    あなたは漫画の文字起こし専門AIです。

    // ここにカスタム指示を追加
    特に注意すべき点:
    - セリフの読む順番を正確に
    - 吹き出しの形状も記録
    - 感情表現（！、...など）も保持

    {{ _.role("user") }}
    この漫画ページを分析してください。
    {{ ctx.output_format }}
  "#
}
```

編集後は再生成：

```bash
npx baml-cli generate
```

### LLMプロバイダーの切り替え

#### OpenAI GPT-4V を使う

```rust
// baml_src/manga-ocr.baml
function TranscribeMangaPage(...) -> MangaPageTranscription {
  client GPT4Vision  // ← これ
  // ...
}
```

#### Anthropic Claude を使う

```rust
function TranscribeMangaPage(...) -> MangaPageTranscription {
  client ClaudeVision  // ← これに変更
  // ...
}
```

#### Google Gemini を使う

```rust
function TranscribeMangaPage(...) -> MangaPageTranscription {
  client GeminiVision  // ← これに変更
  // ...
}
```

### プログラムから使用

```typescript
import { MangaCaptureAgentBuilder } from './src/agent';
import { CaptureSession } from './src/state';
import { VisionLLMManager } from './src/vision-llm';

// セッション作成
const session = new CaptureSession(
  'my-session',
  './captures',
  './output'
);

// Vision LLM設定
const visionLLM = new VisionLLMManager();
// visionLLM.setBAMLClient(b); // BAMLクライアントを設定

// エージェント構築
const agent = new MangaCaptureAgentBuilder()
  .setCaptureDir('./captures')
  .setOutputDir('./output')
  .setCaptureInterval(1000)
  .setAutoTranscribe(true)
  .build(session, visionLLM);

// イベントリスナー
agent.on('page_detected', (data) => {
  console.log(`新しいページ: ${data.pageNumber}`);
});

// 開始
await agent.initialize();
await agent.startCaptureLoop();

// 停止
await agent.stopCaptureLoop();
```

## 🧪 テスト

```bash
# BAMLプロンプトのテスト
npx baml-cli test

# TypeScriptビルドテスト
npm run build
```

## 📁 プロジェクト構造

```
obs-manga-capture/
├── src/
│   ├── index.ts          # CLIエントリーポイント
│   ├── agent.ts          # エージェントロジック（Factor 8）
│   ├── capture.ts        # OBS/システムキャプチャ
│   ├── page-detector.ts  # ページ検知アルゴリズム
│   ├── vision-llm.ts     # Vision LLM統合（Factor 1, 4）
│   └── state.ts          # 状態管理（Factor 5）
├── baml_src/
│   └── manga-ocr.baml    # プロンプト定義（Factor 2）
├── captures/             # スクリーンショット保存先
├── output/               # 文字起こし結果
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

## 🔧 トラブルシューティング

### OBSに接続できない

1. OBS StudioでWebSocketサーバーが有効か確認
2. ポート番号（デフォルト4455）が正しいか確認
3. パスワードが設定されている場合は `.env` に記載

### ページが検知されない

1. `IMAGE_SIMILARITY_THRESHOLD` を調整（デフォルト0.85）
2. `PAGE_CHANGE_THRESHOLD` を調整（デフォルト0.15）
3. `--interval` でキャプチャ間隔を長くする

### 文字起こしが不正確

1. `baml_src/manga-ocr.baml` のプロンプトを調整
2. 使用するLLMモデルを変更（GPT-4o推奨）
3. 画像解像度を上げる

### BAMLエラー

```bash
# BAMLを再初期化
rm -rf baml_client/
npx baml-cli init
npx baml-cli generate
```

## 🎓 学習リソース

- [12-Factor Agents 公式ガイド](https://github.com/humanlayer/12-factor-agents)
- [BAMLドキュメント](https://docs.boundaryml.com/)
- [OBS WebSocketドキュメント](https://github.com/obsproject/obs-websocket)

## 📝 ライセンス

このプロジェクトは12-Factor Agentsのサンプル実装です。

## 🤝 貢献

Issue、Pull Requestを歓迎します！

## 📞 サポート

問題が発生した場合は、Issueを作成してください。

---

**Built with 12-Factor Agents principles** 🚀
