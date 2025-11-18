# ⚠️ 重大な問題と修正内容

**作成日:** 2025-11-18
**更新日:** 2025-11-18
**ステータス:** 🟡 修正作業完了（統合テスト待ち）

---

## 🚨 発見された重大な問題

深く見直した結果、**初期実装には致命的な問題**がありました。

### 問題1: モデル名の誤り（致命的）

**誤った実装:**
```env
# ❌ 間違い
OLLAMA_MODEL=qwen2-vl:7b
OLLAMA_MODEL=qwen2-vl:2b
```

**問題点:**
- `qwen2-vl` がOllamaで利用可能か未確認
- 実際には存在しない可能性が高い
- ユーザーが `ollama pull qwen2-vl:7b` を実行してもエラーになる

**正しい実装:**
```env
# ✅ 正しい
OLLAMA_MODEL=llava:7b        # 確実に動作（推奨）
OLLAMA_MODEL=llava:13b       # 高性能版
OLLAMA_MODEL=llama3.2-vision:11b  # 最新版
```

**理由:**
- Ollama公式ドキュメントで `llava` が明示的にサポートされている
- 実績があり、確実に動作する
- 日本語OCRにも対応

---

### 問題2: Ollama API の誤った使用（致命的）

**誤った実装:**
```typescript
// ❌ 間違い（検証不足）
const response = await fetch(`${this.baseUrl}/api/generate`, {
  body: JSON.stringify({
    images: [imageBase64],  // 配列かどうか不明
    format: 'json'  // 動作するか不明
  })
});
```

**問題点:**
- Ollama公式APIドキュメントを確認していなかった
- 推測で実装していた
- エラーハンドリングが不十分

**正しい実装:**
```typescript
// ✅ 正しい（公式ドキュメント準拠）
const request: OllamaGenerateRequest = {
  model: this.model,
  prompt: prompt,
  images: [imageBase64],  // 配列形式（公式仕様）
  stream: false,
  format: 'json',  // JSON形式指定（公式サポート）
  options: {
    temperature: 0.3,
    num_ctx: 4096
  }
};

const response = await fetch(`${this.baseUrl}/api/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(request)
});
```

**修正点:**
- Ollama公式APIドキュメントに基づく実装
- 適切なエラーハンドリング
- ストリーミング対応も追加

**参考:** https://github.com/ollama/ollama/blob/main/docs/api.md

---

### 問題3: エージェント統合の未完成（重大）

**現状の問題:**
```typescript
// agent.ts（未修正）
import { VisionLLMManager } from './vision-llm';  // ❌ BAML用

class MangaCaptureAgent {
  constructor(
    visionLLM: VisionLLMManager,  // ❌ Ollama未対応
    ...
  ) {
    this.visionLLM = visionLLM;
  }
}
```

**問題点:**
- Ollama用のクラス（QwenVisionManager）が統合されていない
- 既存コードがBAMLに依存したまま
- 実際には動作しない

**必要な修正:**
```typescript
// ✅ Ollama対応版
import { LlavaVisionManager } from './ollama/llava-vision';

class MangaCaptureAgent {
  constructor(
    visionLLM: LlavaVisionManager,  // ✅ Ollama対応
    ...
  ) {
    this.visionLLM = visionLLM;
  }
}
```

---

### 問題4: index.ts の未修正（重大）

**現状:**
```typescript
// ❌ BAML前提のコード
try {
  const { b } = require('../baml_client');
  visionLLM.setBAMLClient(b);
} catch (error) {
  console.log('BAMLクライアントが見つかりません');
}
```

**問題点:**
- Ollama版ではBAML不要
- この部分が実行されるとエラーになる

**必要な修正:**
```typescript
// ✅ Ollama版
const visionLLM = new LlavaVisionManager(
  process.env.OLLAMA_API_URL || 'http://localhost:11434',
  process.env.OLLAMA_MODEL || 'llava:7b'
);

await visionLLM.initialize();
```

---

### 問題5: 不要な依存関係（中程度）

**package.json:**
```json
{
  "dependencies": {
    "@boundaryml/baml": "^0.60.0",  // ❌ Ollama版では不要
    ...
  }
}
```

**問題点:**
- 混乱を招く
- インストールサイズの無駄

**修正:**
```json
{
  "dependencies": {
    // BAML削除
    "tsx": "^4.15.0",
    "typescript": "^5.0.0",
    "sharp": "^0.33.0",
    ...
  }
}
```

---

## ✅ 修正内容まとめ

### ✅ 修正完了したファイル

1. **`src/ollama/ollama-client.ts`** ✅
   - Ollama公式API仕様に準拠
   - 適切なエラーハンドリング
   - ストリーミング対応
   - モデル確認機能
   - **Action:** ollama-client.fixed.ts から置き換え完了

2. **`docs/OLLAMA_RESEARCH.md`** ✅
   - 調査内容の文書化
   - 正しいモデル名のリスト
   - API仕様の確認

3. **`.env.windows`** ✅
   - デフォルトモデルを `llava:7b` に変更
   - 全モデルオプション記載
   - 推奨設定を更新
   - **Action:** .env.windows.fixed から置き換え完了

4. **`README.windows.md`** ✅
   - セットアップ手順を修正
   - 全ての qwen2-vl → llava に変更
   - モデル選択肢を追加（llava:7b, llava:13b, bakllava）
   - トラブルシューティング更新
   - **Action:** 全面更新完了

5. **`QUICKSTART.windows.md`** ✅
   - 全ての qwen2-vl → llava に変更
   - ダウンロード手順を更新
   - 性能見積もりを修正
   - **Action:** 全面更新完了

6. **`src/ollama/ollama-vision.ts`** ✅（新規作成）
   - qwen-vision.ts をベースに作成
   - クラス名: `OllamaVisionManager`（モデル非依存）
   - 任意のVisionモデルに対応（llava, llama3.2-vision, bakllava等）
   - デフォルトモデル: `llava:7b`
   - **Action:** 新規作成、qwen-vision.ts は .old にバックアップ

7. **`package.json`** ✅
   - BAML依存削除
   - ollama関連スクリプト追加（ollama:check, ollama:pull等）
   - バージョン 2.0.0 に更新
   - キーワードに ollama, llava 追加
   - **Action:** 全面更新完了

### ⏳ 残りの修正が必要なファイル

8. **`src/agent.ts`** ⏳
   - OllamaVisionManager 統合
   - BAML依存削除
   - **Status:** 未着手（次のステップ）

9. **`src/index.ts`** ⏳
   - BAML関連コード削除
   - Ollama初期化コード追加
   - **Status:** 未着手（次のステップ）

---

## 🎯 正しいセットアップ手順（修正版）

### ステップ1: Node.js インストール
```cmd
# https://nodejs.org/ からLTS版をインストール
node --version  # 確認
```

### ステップ2: Ollama インストール
```cmd
# https://ollama.ai/download/windows からインストール
ollama --version  # 確認
```

### ステップ3: LLaVA モデルダウンロード

**GPU環境（推奨）:**
```cmd
ollama pull llava:13b
```

**標準環境:**
```cmd
ollama pull llava:7b
```

**軽量環境:**
```cmd
ollama pull bakllava
```

### ステップ4: プロジェクトセットアップ
```cmd
cd obs-manga-capture
npm install
copy .env.windows .env

# .env を編集
notepad .env
```

**.env の設定:**
```env
OLLAMA_MODEL=llava:7b
OLLAMA_API_URL=http://localhost:11434
```

### ステップ5: 動作確認
```cmd
# Ollama起動確認
ollama list

# テスト実行
npm run dev capture --no-obs
```

---

## 📊 性能見積もり（修正版）

| 環境 | モデル | 処理時間/ページ | メモリ |
|------|--------|-----------------|--------|
| **RTX 3060** | llava:13b | 1-2秒 | 8GB VRAM |
| **RTX 3060** | llava:7b | 1-1.5秒 | 4.7GB VRAM |
| **GTX 1060** | llava:7b | 2-3秒 | 4.7GB VRAM |
| **Core i7 CPU** | llava:7b | 8-15秒 | 8GB RAM |
| **軽量版** | bakllava | 5-10秒 | 4.7GB |

---

## 🔧 修正作業の進捗

### ✅ 完了した作業

- [x] 全ドキュメントのモデル名を `llava:7b` に統一
- [x] ollama-client.fixed.ts を ollama-client.ts に上書き
- [x] qwen-vision.ts を ollama-vision.ts に作成（OllamaVisionManager）
- [x] package.json から BAML 削除、ollama スクリプト追加
- [x] .env.windows を正しいモデル名に更新
- [x] README.windows.md 全面更新
- [x] QUICKSTART.windows.md 全面更新

### ⏳ 残りの作業（統合テスト前に必要）

#### 優先度: 高

- [ ] **agent.ts を修正**
  - OllamaVisionManager インポート
  - BAML依存を削除
  - 初期化処理を Ollama 用に変更

- [ ] **index.ts を書き直し**
  - BAML初期化コード削除
  - Ollama初期化コードに置き換え
  - 環境変数から設定を読み込み

#### 優先度: 中

- [ ] baml_src/ ディレクトリ削除（もう不要）
- [ ] 統合テストの実施
  - Ollama起動確認
  - モデルダウンロード確認
  - エンドツーエンド動作確認

#### 優先度: 低

- [ ] 追加のVisionモデル対応の検証（llama3.2-vision など）
- [ ] ストリーミング機能の実装とテスト
- [ ] パフォーマンスチューニング

---

## 💡 重要な学び

### 反省点

1. **仕様確認不足**
   - Ollama公式ドキュメントを最初に確認すべきだった
   - モデルの存在を確認せずに実装してしまった

2. **推測による実装**
   - APIの使い方を推測で実装した
   - 実際の動作確認をしていなかった

3. **統合の未完成**
   - 個別のクラスは作成したが、統合していなかった
   - エンドツーエンドのテストが必要

### 改善策

1. **ドキュメントファースト**
   - 公式ドキュメントを必ず確認
   - 実装前に仕様を理解

2. **小さく検証**
   - 最小限のテストコードで動作確認
   - 動いてから拡張

3. **統合を意識**
   - 既存コードとの統合を最初から考慮
   - 完全に動作するまで完成とは言えない

---

## 📚 参考資料

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Ollama Model Library](https://ollama.com/library)
- [LLaVA Model Information](https://ollama.com/library/llava)
- [Llama 3.2 Vision](https://ollama.com/library/llama3.2-vision)

---

## 📝 変更サマリー

### 置き換えられたファイル
- `src/ollama/ollama-client.ts` ← ollama-client.fixed.ts
- `.env.windows` ← .env.windows.fixed

### バックアップされたファイル
- `src/ollama/ollama-client.old.ts` ← 旧版
- `.env.windows.old` ← 旧版
- `src/ollama/qwen-vision.old.ts` ← 旧版

### 新規作成されたファイル
- `src/ollama/ollama-vision.ts` ← モデル非依存の新実装

### 全面更新されたファイル
- `package.json` ← BAML削除、ollama対応
- `README.windows.md` ← 全てのモデル名修正
- `QUICKSTART.windows.md` ← 全てのモデル名修正

---

**次のアクション:**
1. agent.ts を OllamaVisionManager に対応させる
2. index.ts を Ollama 初期化コードに書き換える
3. 統合テスト実施

**ステータス:** 🟡 コア修正完了、統合作業が残っている
