# 🚀 クイックスタートガイド

このガイドに従って、5分で漫画自動キャプチャシステムを動かしましょう！

## ステップ1: 環境準備（2分）

### 必要なもの

- ✅ Node.js 20+ がインストール済み
- ✅ OpenAI APIキー（または Anthropic/Google）
- ✅ OBS Studio（オプション）

### インストール

```bash
cd obs-manga-capture
npm install
```

## ステップ2: BAML設定（1分）

```bash
# BAML初期化
npx baml-cli init

# プロンプトファイルはすでに作成済み
# baml_src/manga-ocr.baml

# TypeScript型を生成
npx baml-cli generate
```

## ステップ3: API キー設定（1分）

```bash
# .env ファイルを作成
cp .env.example .env
```

`.env` ファイルを編集：

```env
# OpenAI APIキーを設定（GPT-4o推奨）
OPENAI_API_KEY=sk-proj-your-key-here

# OBSを使わない場合はこれでOK
# システムのスクリーンショット機能を使います
```

## ステップ4: テスト実行（1分）

### モックモードでテスト

```bash
# APIキー不要のモックモード
npm run dev capture --mock --no-obs
```

これで動作確認できます！

### OBSと連携

OBS Studioを使う場合：

1. OBS Studio を起動
2. **ツール > WebSocketサーバー設定**
3. **有効化**をチェック
4. ポート: `4455`（デフォルト）
5. パスワードを設定した場合は `.env` に追加

```bash
# OBSモードで実行
npm run dev capture
```

## ステップ5: 実際に使ってみる

### シナリオ: 漫画を読みながら自動記録

```bash
# 1. キャプチャモード開始
npm run dev capture

# 2. OBSまたはブラウザで漫画を表示

# 3. ページをめくる
#    → 自動的にスクリーンショット撮影
#    → ページ変更を検知
#    → Vision LLMで文字起こし

# 4. Ctrl+C で終了

# 5. 結果を確認
cat output/session-*.json
```

### 出力例

```json
{
  "sessionId": "1234567890-abc",
  "totalPages": 5,
  "pages": [
    {
      "pageNumber": 1,
      "imagePath": "captures/capture-1234567890.png",
      "transcription": {
        "speech_bubbles": [
          {
            "speaker": "主人公",
            "text": "やっと見つけた！",
            "reading_order": 1
          }
        ],
        "page_description": "主人公が剣を発見するシーン"
      }
    }
  ]
}
```

## 📚 次のステップ

### プロンプトをカスタマイズ

`baml_src/manga-ocr.baml` を編集して、抽出内容をカスタマイズ：

```rust
function TranscribeMangaPage(...) -> MangaPageTranscription {
  prompt #"
    {{ _.role("system") }}

    あなたは漫画の文字起こし専門AIです。

    // ここに独自の指示を追加
    特別な注意事項:
    - キャラクター名を正確に
    - 感情を表す記号も保持（！、...、など）
    - 吹き出しの形状も記録

    ...
  "#
}
```

編集後：

```bash
npx baml-cli generate
```

### LLMプロバイダーを変更

#### Claude を使う

```rust
// baml_src/manga-ocr.baml
function TranscribeMangaPage(...) {
  client ClaudeVision  // ← GPT4Vision から変更
  // ...
}
```

`.env` に追加：

```env
ANTHROPIC_API_KEY=sk-ant-your-key
```

再生成：

```bash
npx baml-cli generate
```

### 未処理ページをバッチ処理

```bash
# セッションIDを確認
ls output/

# バッチ処理
npm run dev process --sessionId=1234567890-abc
```

## 🎯 よくある使い方

### 1. リアルタイムで読みながら記録

```bash
npm run dev capture
# ページめくりで自動記録
```

### 2. まず画像だけ保存、後で文字起こし

```bash
# キャプチャのみ（文字起こしなし）
npm run dev capture --no-auto-transcribe

# 後でまとめて文字起こし
npm run dev process --sessionId=xxx
```

### 3. OBSなしで既存の画像を処理

```bash
# 画像を captures/ に配置

# 手動でセッション作成
# (TODO: 画像インポート機能を実装予定)
```

## ⚙️ 設定のカスタマイズ

### キャプチャ間隔を調整

```bash
# 2秒ごとにキャプチャ（デフォルトは1秒）
npm run dev capture --interval=2000
```

### ページ検知の感度を調整

`.env` で設定：

```env
# 類似度が85%以下なら別ページと判定（デフォルト）
IMAGE_SIMILARITY_THRESHOLD=0.85

# 15%以上の変化で別ページと判定（デフォルト）
PAGE_CHANGE_THRESHOLD=0.15
```

値を小さくすると検知が敏感になります。

## 🐛 トラブルシューティング

### ページが検知されない

```bash
# 感度を上げる（類似度閾値を下げる）
# .env で調整
IMAGE_SIMILARITY_THRESHOLD=0.75
```

### OBSに接続できない

```bash
# システムキャプチャを使用
npm run dev capture --no-obs
```

### BAML エラー

```bash
# 再生成
npx baml-cli generate

# それでもダメなら再初期化
rm -rf baml_client/
npx baml-cli init
npx baml-cli generate
```

## 📖 詳細ドキュメント

より詳しい情報は [README.md](./README.md) を参照してください。

## 💡 ヒント

1. **最初はモックモードでテスト**
   ```bash
   npm run dev capture --mock --no-obs
   ```

2. **APIコストを抑えるには**
   - まず画像だけキャプチャ
   - 後でまとめて文字起こし
   - 不要なページは削除してから処理

3. **より正確な文字起こし**
   - GPT-4o 推奨（最も精度が高い）
   - プロンプトをカスタマイズ
   - 画像解像度を上げる

## 🎉 完了！

これで漫画の自動記録システムが使えるようになりました！

次は [README.md](./README.md) で高度な使い方を確認してください。

---

**Happy manga reading!** 📚✨
