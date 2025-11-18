# 📚 Windows + Ollama + Qwen2-VL セットアップガイド

**完全ローカル実行**の漫画自動キャプチャ&文字起こしシステム

---

## ✨ システム概要

```
┌─────────────────┐
│  OBS Studio     │  漫画を表示
│  (Windows)      │
└────────┬────────┘
         │ PowerShellスクリーンショット
         ↓
┌─────────────────┐
│ ページめくり検知 │  画像差分検出
└────────┬────────┘
         │
         ↓
┌───────────────────────────┐
│ Ollama + Qwen2-VL (Local) │
│ 画像 → セリフ抽出          │  **APIコスト $0**
│ 完全オフライン実行可能     │  **インターネット不要**
└───────────────────────────┘
```

**特徴:**
- ✅ 完全ローカル実行（APIキー不要）
- ✅ Qwen2-VL Vision モデル使用
- ✅ Windows 10/11 対応
- ✅ GPU加速対応（NVIDIA）
- ✅ OBS不要でも動作可能

---

## 🖥️ システム要件

### 最小要件
- **OS**: Windows 10/11 64bit
- **CPU**: Intel Core i5以上
- **RAM**: 8GB以上
- **ストレージ**: 10GB以上の空き容量
- **Node.js**: 20.x以上

### 推奨要件
- **CPU**: Intel Core i7/Ryzen 7以上
- **RAM**: 16GB以上
- **GPU**: NVIDIA GeForce GTX 1060以上（6GB VRAM）
- **ストレージ**: SSD 20GB以上

### GPU vs CPU 性能比較

| 環境 | モデル | 処理時間/ページ | 推奨度 |
|------|--------|-----------------|--------|
| **NVIDIA RTX 3060** | qwen2-vl:7b | 1-2秒 | ⭐⭐⭐⭐⭐ |
| **NVIDIA GTX 1060** | qwen2-vl:2b | 2-3秒 | ⭐⭐⭐⭐ |
| **CPU (i7-10700)** | qwen2-vl:2b | 5-10秒 | ⭐⭐⭐ |
| **CPU (i5-8400)** | qwen2-vl:2b | 10-20秒 | ⭐⭐ |

---

## 📥 インストール手順

### ステップ1: Node.js インストール（5分）

1. [Node.js公式サイト](https://nodejs.org/) にアクセス
2. **LTS版（20.x）** をダウンロード
3. インストーラーを実行
4. コマンドプロンプトで確認:

```cmd
node --version
npm --version
```

### ステップ2: Ollama インストール（10分）

1. [Ollama for Windows](https://ollama.ai/download/windows) をダウンロード
2. インストーラーを実行
3. インストール完了後、Ollamaが自動起動

**確認方法:**
```cmd
# コマンドプロンプトで実行
ollama --version
```

**タスクトレイに Ollama アイコンが表示されていればOK**

### ステップ3: Qwen2-VL モデルダウンロード（15分）

Qwen2-VLモデルをダウンロードします（約4-7GB）。

#### GPU搭載PCの場合（推奨）

```cmd
ollama pull qwen2-vl:7b
```

ダウンロード時間: 10-15分（インターネット速度による）

#### CPU環境または低スペックPCの場合

```cmd
ollama pull qwen2-vl:2b
```

ダウンロード時間: 5-10分

**確認方法:**
```cmd
ollama list
```

出力例:
```
NAME                    ID              SIZE      MODIFIED
qwen2-vl:7b             abc123...       4.7GB     2 minutes ago
```

### ステップ4: プロジェクトセットアップ（5分）

```cmd
# プロジェクトディレクトリに移動
cd 12-factor-agents_fork\obs-manga-capture

# 依存関係インストール
npm install

# 環境変数設定
copy .env.windows .env

# .envファイルを編集（メモ帳で開く）
notepad .env
```

**.envファイル編集:**
```env
# GPU環境の場合
OLLAMA_MODEL=qwen2-vl:7b

# CPU環境の場合
OLLAMA_MODEL=qwen2-vl:2b
```

### ステップ5: OBS Studio（オプション）

OBSを使わない場合はスキップ可能。

1. [OBS Studio](https://obsproject.com/download) をダウンロード
2. インストール
3. **ツール > WebSocketサーバー設定**
4. **サーバーを有効にする** にチェック
5. ポート: `4455`（デフォルト）

---

## 🚀 使い方

### テスト実行（初回確認）

```cmd
# Ollamaが起動しているか確認
ollama list

# モックモードでテスト（Ollama不要）
npm run dev capture --mock --no-obs

# Ollama使用モードでテスト
npm run dev capture --no-obs
```

### 実際の使用

#### パターン1: OBSを使う場合

```cmd
# OBS Studioを起動
# 漫画を表示するシーンを作成

# キャプチャ開始
npm run dev capture

# 漫画のページをめくる
# → 自動でキャプチャ & 文字起こし

# 終了: Ctrl+C
```

#### パターン2: OBSなし（PowerShellスクリーンショット）

```cmd
# ブラウザで漫画を全画面表示

# キャプチャ開始
npm run dev capture --no-obs

# ページめくり
# → 画面全体をキャプチャ

# 終了: Ctrl+C
```

---

## ⚙️ 設定のカスタマイズ

### モデル切り替え

```env
# 高品質モード（GPU推奨）
OLLAMA_MODEL=qwen2-vl:7b

# 軽量モード（CPU可）
OLLAMA_MODEL=qwen2-vl:2b
```

### キャプチャ間隔調整

```env
# 速いページめくり
CAPTURE_INTERVAL_MS=500

# 通常
CAPTURE_INTERVAL_MS=1000

# 低負荷モード（CPU環境）
CAPTURE_INTERVAL_MS=2000
```

### ページ検知感度

```env
# 感度高（小さな変化で検知）
IMAGE_SIMILARITY_THRESHOLD=0.75

# 通常
IMAGE_SIMILARITY_THRESHOLD=0.85

# 感度低（大きな変化のみ検知）
IMAGE_SIMILARITY_THRESHOLD=0.95
```

---

## 📊 出力結果

### JSONファイル

`output/session-XXXXX.json`:

```json
{
  "sessionId": "1234567890-abc",
  "totalPages": 5,
  "pages": [
    {
      "pageNumber": 1,
      "imagePath": "captures\\capture-1234567890.png",
      "transcription": {
        "speech_bubbles": [
          {
            "speaker": "主人公",
            "text": "やっと見つけた！",
            "position": "top-right",
            "reading_order": 1
          }
        ],
        "narrations": [],
        "sound_effects": ["ゴゴゴゴ"],
        "page_description": "主人公が剣を発見するシーン",
        "has_text": true
      }
    }
  ]
}
```

### スクリーンショット

`captures/` フォルダに保存:
```
captures/
  ├── capture-1234567890.png
  ├── capture-1234567891.png
  └── ...
```

---

## 🐛 トラブルシューティング

### Ollamaに接続できない

**症状:**
```
❌ Ollamaサーバーに接続できません
```

**解決方法:**

1. Ollamaが起動しているか確認
   ```cmd
   # タスクマネージャーで "ollama" プロセスを確認
   ```

2. 再起動
   ```cmd
   # タスクトレイのOllamaアイコン右クリック > Quit
   # スタートメニューから Ollama を再起動
   ```

3. ポート確認
   ```cmd
   netstat -ano | findstr :11434
   ```

4. ブラウザで確認
   ```
   http://localhost:11434
   → "Ollama is running" と表示されればOK
   ```

### モデルが見つからない

**症状:**
```
⚠️ モデル qwen2-vl:7b が見つかりません
```

**解決方法:**
```cmd
# モデル一覧確認
ollama list

# モデルダウンロード
ollama pull qwen2-vl:7b
# または
ollama pull qwen2-vl:2b
```

### GPU が使われていない

**確認方法:**
```cmd
# タスクマネージャー > パフォーマンス > GPU
# Ollama実行中にGPU使用率が上がっているか確認
```

**解決方法:**

1. NVIDIA GPU ドライバー更新
   - [NVIDIA公式](https://www.nvidia.com/ja-jp/geforce/drivers/)

2. CUDA Toolkit インストール（オプション）
   - Ollamaは自動で検出

3. 環境変数確認
   ```env
   USE_GPU=true
   ```

### 処理が遅い

**CPU環境の場合:**

1. 軽量モデルに切り替え
   ```env
   OLLAMA_MODEL=qwen2-vl:2b
   ```

2. コンテキストサイズ削減
   ```env
   QWEN_NUM_CTX=2048
   ```

3. キャプチャ間隔を長くする
   ```env
   CAPTURE_INTERVAL_MS=3000
   ```

### ページが検知されない

```env
# 感度を上げる
IMAGE_SIMILARITY_THRESHOLD=0.75

# または
PAGE_CHANGE_THRESHOLD=0.10
```

### PowerShellスクリーンショットが動かない

**確認:**
```cmd
# PowerShellバージョン確認
powershell $PSVersionTable.PSVersion
# → 5.1以上必要
```

**代替方法:**
```cmd
# OBSモードを使用
npm run dev capture
```

---

## 💡 パフォーマンス最適化

### GPU環境（NVIDIA）

```env
OLLAMA_MODEL=qwen2-vl:7b
USE_GPU=true
QWEN_TEMPERATURE=0.3
QWEN_NUM_CTX=4096
CAPTURE_INTERVAL_MS=1000
```

**期待性能:** 1-2秒/ページ

### CPU環境

```env
OLLAMA_MODEL=qwen2-vl:2b
USE_GPU=false
QWEN_NUM_CTX=2048
CAPTURE_INTERVAL_MS=2000
```

**期待性能:** 5-10秒/ページ

### メモリ不足の場合

```env
OLLAMA_MODEL=qwen2-vl:2b
QWEN_NUM_CTX=1024
MAX_CONCURRENT=1
```

---

## 📝 実行例

### コマンド一覧

```cmd
# ヘルプ表示
npm run dev help

# キャプチャモード（OBS使用）
npm run dev capture

# キャプチャモード（OBSなし）
npm run dev capture --no-obs

# モックモード（テスト用）
npm run dev capture --mock --no-obs

# キャプチャ間隔指定
npm run dev capture --interval=2000

# 未処理ページを文字起こし
npm run dev process --sessionId=1234567890-abc
```

### 実行ログ例

```
🚀 Qwen2-VL 初期化中...
✅ Qwen2-VL 初期化完了

📚 漫画キャプチャモード開始

🆔 セッションID: 1234567890-abc

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📸 キャプチャ実行中...
   OBSで漫画を表示し、ページをめくってください
   Ctrl+C で終了
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 画像類似度: 45.23% (閾値: 85.00%)
✅ ページめくりを検知しました！

📖 ページ 1 の文字起こし開始...
🔍 Qwen2-VL でVision処理開始: capture-1234567890.png
✅ Vision処理完了
✅ 文字起こし完了:
   セリフ: 3個, ナレーション: 1個, 効果音: 2個

📝 抽出されたセリフ:
   1. [主人公] 「やっと見つけた！」
   2. 「これが伝説の剣か...」
   3. [ナレーター] 「長い旅の末、ついに...」
```

---

## 🎓 次のステップ

1. **プロンプトカスタマイズ**
   - `src/ollama/prompts.ts` を編集
   - より正確な文字起こしのために調整

2. **自動化**
   - バッチファイル作成で1クリック起動
   - タスクスケジューラで定期実行

3. **データベース統合**
   - SQLiteに保存
   - 検索機能追加

---

## 📞 サポート

問題が発生した場合：

1. Ollama ログ確認
   ```cmd
   # タスクトレイ > Ollama > View Logs
   ```

2. システム確認
   ```cmd
   npm run dev help
   ollama list
   node --version
   ```

3. Issue作成
   - エラーメッセージ
   - 環境情報（OS, CPU, GPU, RAM）
   - 実行コマンド

---

**Windows環境での完全ローカル実行を楽しんでください！** 🎉
