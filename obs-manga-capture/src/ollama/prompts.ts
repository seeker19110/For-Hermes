/**
 * Qwen2-VL用 漫画文字起こしプロンプト
 *
 * 日本語漫画に特化したプロンプトテンプレート
 */

export const MANGA_OCR_PROMPT = `
あなたは日本語漫画の文字起こし専門AIです。

この漫画ページ画像を分析し、以下の情報を抽出してJSON形式で出力してください。

## 抽出する情報

### 1. セリフ（speech_bubbles）
- 吹き出し内のテキスト
- 話者名（分かる場合、または推測できる場合）
- 画面上の位置
- 読む順番（重要！）

### 2. ナレーション（narrations）
- 吹き出しに入っていないテキスト
- モノローグ、説明文など

### 3. 効果音（sound_effects）
- 擬音語、擬態語
- 例：「ドカーン」「ざわざわ」「キラキラ」など

### 4. ページ全体の説明（page_description）
- このページで何が起きているかを簡潔に説明

## 重要な注意点

1. **日本語漫画は右から左、上から下に読みます**
   - reading_order は右上が1、左下が最後

2. **位置の分類**
   - "top-left", "top-right", "center", "bottom-left", "bottom-right"

3. **テキストがない場合**
   - has_text を false に設定
   - 空の配列を返す

4. **判読できない文字**
   - [判読不能] と記載

5. **セリフとナレーションの区別**
   - 吹き出しに入っている → speech_bubbles
   - 枠外やナレーション枠 → narrations

## 出力形式（JSON）

{
  "speech_bubbles": [
    {
      "speaker": "キャラクター名（分かる場合）",
      "text": "セリフの内容",
      "position": "top-right",
      "reading_order": 1
    }
  ],
  "narrations": [
    {
      "text": "ナレーションの内容",
      "position": "top-center"
    }
  ],
  "sound_effects": [
    "ドカーン",
    "ざわざわ"
  ],
  "page_description": "主人公が敵と対峙しているシーン",
  "has_text": true
}

## 例

【入力画像例】
右上: 「やっと見つけた！」
左上: 「これが伝説の剣か...」
中央下: ゴゴゴゴ（効果音）

【出力JSON】
{
  "speech_bubbles": [
    {
      "speaker": null,
      "text": "やっと見つけた！",
      "position": "top-right",
      "reading_order": 1
    },
    {
      "speaker": null,
      "text": "これが伝説の剣か...",
      "position": "top-left",
      "reading_order": 2
    }
  ],
  "narrations": [],
  "sound_effects": ["ゴゴゴゴ"],
  "page_description": "主人公が洞窟で剣を発見するシーン",
  "has_text": true
}

それでは、この画像を分析してJSON形式で出力してください。
JSONのみを出力し、説明文は不要です。
`.trim();

/**
 * 構造化プロンプト（オプション：2段階処理用）
 */
export const MANGA_STRUCTURE_PROMPT = `
以下のOCR結果を漫画のセリフとして構造化してください。

【OCR結果】
{ocr_text}

【位置情報】
{bbox_info}

以下のJSON形式で出力してください：

{
  "speech_bubbles": [...],
  "narrations": [...],
  "sound_effects": [...],
  "page_description": "...",
  "has_text": true
}
`.trim();

/**
 * ページ変更検出用プロンプト（オプション）
 */
export const PAGE_CHANGE_DETECTION_PROMPT = `
2つの漫画ページ画像を比較して、異なるページかどうかを判定してください。

判定基準：
- コマ割りが違う
- キャラクターの配置が大きく異なる
- 背景が変わった

以下のJSON形式で出力してください：

{
  "is_different_page": true,
  "confidence": 0.95,
  "reason": "コマ割りとキャラクター配置が完全に異なる"
}
`.trim();

/**
 * ページ番号検出プロンプト（オプション）
 */
export const PAGE_NUMBER_DETECTION_PROMPT = `
この漫画ページ画像からページ番号を抽出してください。

ページ番号は通常以下の場所にあります：
- 右下または左下の隅
- 小さい数字
- 「p.」「ページ」などの接頭辞がある場合もある

JSON形式で出力してください：

{
  "page_number": 15,
  "found": true,
  "location": "bottom-right"
}

ページ番号が見つからない場合：

{
  "page_number": null,
  "found": false,
  "location": null
}
`.trim();
