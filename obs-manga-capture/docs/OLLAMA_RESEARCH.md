# Ollama + Vision モデル 調査メモ

## 調査が必要な項目

### 1. Vision対応モデルの確認

**Ollamaで利用可能なVisionモデル:**

公式確認方法:
```bash
# インストール済みモデル一覧
ollama list

# 利用可能なモデル検索
# https://ollama.com/library
```

**候補モデル（2024年時点）:**

| モデル名 | Vision対応 | サイズ | 推奨度 |
|---------|-----------|--------|--------|
| `llava:7b` | ✅ | 4.7GB | ⭐⭐⭐⭐⭐ |
| `llava:13b` | ✅ | 8GB | ⭐⭐⭐⭐ |
| `llava:34b` | ✅ | 20GB | ⭐⭐⭐ |
| `llama3.2-vision:11b` | ✅ | 7.9GB | ⭐⭐⭐⭐⭐ |
| `llama3.2-vision:90b` | ✅ | 55GB | ⭐⭐ |
| `bakllava` | ✅ | 4.7GB | ⭐⭐⭐ |
| `qwen2-vl` | ❓ | ❓ | **要確認** |

**重要:**
- `qwen2-vl` がOllamaで利用可能か要確認
- 実際には `llava` または `llama3.2-vision` を推奨すべき可能性

### 2. Vision API の正しい仕様

**Ollama Vision API エンドポイント:**

```
POST http://localhost:11434/api/generate
POST http://localhost:11434/api/chat
```

**リクエスト形式（要確認）:**

```json
{
  "model": "llava:7b",
  "prompt": "この画像を説明してください",
  "images": ["base64_encoded_image"],
  "stream": false,
  "format": "json"
}
```

**または:**

```json
{
  "model": "llama3.2-vision:11b",
  "messages": [
    {
      "role": "user",
      "content": "この画像を説明してください",
      "images": ["base64_encoded_image"]
    }
  ],
  "stream": false
}
```

**確認事項:**
- [ ] 画像フィールド名は `images` か `image` か？
- [ ] Base64エンコード方式は正しいか？
- [ ] `format: "json"` が機能するか？
- [ ] レスポンス形式は想定通りか？

### 3. 実際のテスト結果（TODO）

```bash
# テストコマンド
curl http://localhost:11434/api/generate -d '{
  "model": "llava:7b",
  "prompt": "この画像に何が写っていますか？",
  "images": ["'$(base64 < test.jpg)'"],
  "stream": false
}'
```

**結果:** （実行後に記載）

---

## 推奨モデルの変更案

### 案1: LLaVA を使用（最も安全）

```env
OLLAMA_MODEL=llava:7b
# または
OLLAMA_MODEL=llava:13b
```

**理由:**
- Ollamaで確実にサポートされている
- Visionタスクで実績あり
- ドキュメントが豊富

### 案2: Llama 3.2 Vision を使用

```env
OLLAMA_MODEL=llama3.2-vision:11b
```

**理由:**
- 最新のMetaモデル
- 高性能
- 日本語対応

### 案3: Qwen2-VL（要確認）

```bash
# まず確認
ollama pull qwen2-vl

# 失敗したら代替モデルを使用
```

---

## API仕様の確認（TODO）

1. **公式ドキュメント確認:**
   - https://github.com/ollama/ollama/blob/main/docs/api.md
   - Vision API のセクションを確認

2. **実際のテスト:**
   ```bash
   ollama run llava:7b "この画像を説明して" < test.jpg
   ```

3. **APIレスポンス確認:**
   - レスポンス形式
   - エラーハンドリング
   - ストリーミング vs 非ストリーミング

---

## 修正が必要なファイル

### 高優先度
- [ ] `src/ollama/ollama-client.ts` - API呼び出し方法
- [ ] `.env.windows` - デフォルトモデル名
- [ ] `README.windows.md` - セットアップ手順
- [ ] `QUICKSTART.windows.md` - モデル名

### 中優先度
- [ ] `src/ollama/qwen-vision.ts` - モデル名の柔軟化
- [ ] `src/agent.ts` - QwenVisionManager統合
- [ ] `src/index.ts` - BAML依存削除

### 低優先度
- [ ] `package.json` - BAML削除
- [ ] `baml_src/` - ディレクトリ削除

---

## 次のアクション

1. ✅ Ollama公式APIドキュメントを確認
2. ✅ 利用可能なVisionモデルを特定
3. ✅ 実際のAPI呼び出しをテスト
4. ⏳ コードを修正
5. ⏳ ドキュメントを更新
6. ⏳ 統合テスト

---

**更新日:** 2025-11-18
**ステータス:** 🔴 調査中（未完成）
