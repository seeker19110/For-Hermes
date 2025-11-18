# 🚀 5分で始める - Windows + Ollama + LLaVA

**完全ローカル実行** - APIキー不要、インターネット不要（初回セットアップ後）

---

## ⚡ 超簡単セットアップ（5ステップ）

### ステップ1: Node.js インストール（2分）

1. https://nodejs.org/ にアクセス
2. **LTS版**をダウンロード＆インストール

確認:
```cmd
node --version
```

### ステップ2: Ollama インストール（3分）

1. https://ollama.ai/download/windows にアクセス
2. インストーラーをダウンロード＆実行
3. 自動起動を確認（タスクトレイにアイコン表示）

### ステップ3: LLaVA ダウンロード（10-15分）

**GPU搭載PC（推奨）:**
```cmd
ollama pull llava:7b
```

**CPU環境または低スペックPC:**
```cmd
ollama pull llava:7b
```

待ち時間: コーヒーブレイク☕

### ステップ4: プロジェクトセットアップ（2分）

```cmd
cd 12-factor-agents_fork\obs-manga-capture
npm install
copy .env.windows .env
```

**`.env`を編集**（メモ帳で開く）:
```env
# GPU環境（推奨）
OLLAMA_MODEL=llava:7b

# その他の選択肢
# OLLAMA_MODEL=llava:13b         # 高性能版（8GB）
# OLLAMA_MODEL=llama3.2-vision:11b  # 最新版（7.9GB）
# OLLAMA_MODEL=bakllava           # 軽量版（4.7GB）
```

### ステップ5: テスト実行（1分）

```cmd
npm run dev capture --no-obs
```

**成功したら:**
```
✅ Ollama 初期化完了
📸 キャプチャ実行中...
```

完了！🎉

---

## 📖 基本的な使い方

### シナリオ1: ブラウザで漫画を読みながら自動記録

```cmd
# 1. ブラウザで漫画を全画面表示

# 2. キャプチャ開始
npm run dev capture --no-obs

# 3. ページめくり
#    → 自動でスクリーンショット + 文字起こし

# 4. 終了: Ctrl+C

# 5. 結果確認
dir output
type output\session-*.json
```

### シナリオ2: OBS Studioを使う（より高品質）

**OBSセットアップ:**
1. OBS Studio をインストール
2. **ツール > WebSocketサーバー設定**
3. **有効化** にチェック
4. ポート: `4455`

**実行:**
```cmd
# OBSで漫画表示シーンを作成

# キャプチャ開始
npm run dev capture

# ページめくりで自動記録
```

---

## 📊 処理速度の目安

| 環境 | モデル | 速度 |
|------|--------|------|
| RTX 3060 | llava:13b | ⚡ 1-2秒/ページ |
| GTX 1060 | llava:7b | ⚡⚡ 2-3秒/ページ |
| Core i7 CPU | llava:7b | ⚡⚡⚡ 5-10秒/ページ |

---

## ⚙️ よくある設定

### キャプチャ間隔を変更

```env
# .env ファイル
CAPTURE_INTERVAL_MS=2000  # 2秒ごと
```

### ページ検知感度を調整

```env
# より敏感に検知
IMAGE_SIMILARITY_THRESHOLD=0.75

# 通常
IMAGE_SIMILARITY_THRESHOLD=0.85
```

### 軽量化（低スペックPC向け）

```env
OLLAMA_MODEL=bakllava
OLLAMA_NUM_CTX=2048
CAPTURE_INTERVAL_MS=3000
```

---

## 🐛 トラブルシューティング

### Ollamaに接続できない

```cmd
# Ollamaを再起動
# タスクトレイ > Ollama右クリック > Quit
# スタートメニュー > Ollama

# ブラウザで確認
start http://localhost:11434
```

### モデルが見つからない

```cmd
ollama list
# llava が表示されない場合

ollama pull llava:7b
```

### 処理が遅い

**.envを編集:**
```env
# 軽量モデルに変更
OLLAMA_MODEL=bakllava

# コンテキストサイズ削減
OLLAMA_NUM_CTX=2048

# キャプチャ間隔を長く
CAPTURE_INTERVAL_MS=2000
```

### PowerShellエラー

```cmd
# PowerShellバージョン確認
powershell $PSVersionTable.PSVersion

# 5.1以上が必要
# Windows Updateで更新
```

---

## 💡 ヒント

### 1. GPU使用率を確認

```
タスクマネージャー > パフォーマンス > GPU
```

Ollama実行中にGPU使用率が上がっていればGPUが使われています。

### 2. APIコスト削減

完全ローカル実行なので**$0**！
- OpenAI API不要
- インターネット接続不要（初回ダウンロード後）
- プライバシー保護（データは外部送信されない）

### 3. バッチ処理

```cmd
# まず画像だけキャプチャ（文字起こしなし）
npm run dev capture --no-auto-transcribe

# 後でまとめて文字起こし
npm run dev process --sessionId=XXXXX
```

---

## 📁 出力ファイル

### captures/ - スクリーンショット

```
captures\
  capture-1234567890.png
  capture-1234567891.png
  ...
```

### output/ - 文字起こし結果（JSON）

```json
{
  "sessionId": "1234567890-abc",
  "totalPages": 5,
  "pages": [
    {
      "pageNumber": 1,
      "transcription": {
        "speech_bubbles": [
          {
            "text": "やっと見つけた！",
            "reading_order": 1
          }
        ],
        "sound_effects": ["ゴゴゴゴ"]
      }
    }
  ]
}
```

---

## 🎯 コマンド一覧

```cmd
# ヘルプ
npm run dev help

# キャプチャ（OBSなし）
npm run dev capture --no-obs

# キャプチャ（OBS使用）
npm run dev capture

# モックモード（テスト）
npm run dev capture --mock --no-obs

# バッチ処理
npm run dev process --sessionId=XXXXX

# Ollama確認
npm run ollama:check
```

---

## 📖 詳しい情報

- **詳細ドキュメント**: `README.windows.md`
- **エラー対処**: 上記のトラブルシューティング参照
- **カスタマイズ**: `.env` ファイルを編集

---

## 🎉 完了！

これでWindows環境での完全ローカル実行ができるようになりました！

**次のステップ:**
1. 実際の漫画で試してみる
2. 設定をカスタマイズ
3. `README.windows.md` で詳細を確認

**Happy manga reading!** 📚✨
