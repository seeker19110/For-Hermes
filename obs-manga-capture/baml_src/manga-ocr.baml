// Vision LLM用の構造化出力定義

// セリフの位置情報
class SpeechBubble {
  speaker string? @description("話者の名前（分かる場合）")
  text string @description("セリフの内容")
  position string @description("画面上の位置: top-left, top-right, center, bottom-left, bottom-right")
  reading_order int @description("読む順番（1から開始）")
}

// ナレーションやモノローグ
class Narration {
  text string @description("ナレーションの内容")
  position string @description("位置")
}

// ページ全体の文字起こし結果
class MangaPageTranscription {
  page_number int? @description("ページ番号")
  speech_bubbles SpeechBubble[] @description("セリフの吹き出しリスト")
  narrations Narration[] @description("ナレーションリスト")
  sound_effects string[] @description("効果音テキスト（ドカーン、など）")
  page_description string @description("ページ全体の簡単な説明")
  has_text bool @description("このページにテキストが含まれているか")
}

// OpenAI GPT-4V用のクライアント設定
client<llm> GPT4Vision {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

// Anthropic Claude用のクライアント設定
client<llm> ClaudeVision {
  provider anthropic
  options {
    model "claude-3-5-sonnet-20241022"
    api_key env.ANTHROPIC_API_KEY
  }
}

// Google Gemini用のクライアント設定
client<llm> GeminiVision {
  provider google-ai
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GOOGLE_API_KEY
  }
}

// メイン関数: 漫画ページから文字起こしを実行
function TranscribeMangaPage(
  image_path string,
  page_number int?
) -> MangaPageTranscription {
  // デフォルトはGPT-4o、環境変数で切り替え可能
  client GPT4Vision
  // client ClaudeVision
  // client GeminiVision

  prompt #"
    {{ _.role("system") }}

    あなたは漫画の文字起こし専門AIです。

    漫画のページ画像を分析し、以下を抽出してください：

    1. **セリフ（吹き出し内のテキスト）**
       - 話者名（分かる場合）
       - セリフの内容
       - 画面上の位置
       - 読む順番（右上→左下の順が基本）

    2. **ナレーション・モノローグ**
       - 吹き出しに入っていないテキスト

    3. **効果音**
       - 「ドカーン」「ざわざわ」などの擬音語

    4. **ページ全体の説明**
       - どんなシーンか簡潔に

    **重要な注意点:**
    - 日本語の漫画は右から左、上から下に読みます
    - セリフは読む順番を正確に
    - テキストが全くない場合は has_text を false に
    - 判読できない文字は [判読不能] と記載

    {{ _.role("user") }}

    {% if page_number %}
    ページ番号: {{ page_number }}
    {% endif %}

    この漫画ページを分析して、すべてのテキストを抽出してください。

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

// テスト用のシンプルなプロンプト
function DetectPageChange(
  description1 string,
  description2 string
) -> bool {
  client GPT4Vision

  prompt #"
    {{ _.role("system") }}

    2つの画像説明を比較して、漫画のページが変わったかを判断してください。

    {{ _.role("user") }}

    説明1: {{ description1 }}
    説明2: {{ description2 }}

    これらは異なるページですか？

    {{ ctx.output_format }}
  "#
}

// テスト
test SampleTranscription {
  functions [TranscribeMangaPage]
  args {
    image_path "test.jpg"
    page_number 1
  }
}
