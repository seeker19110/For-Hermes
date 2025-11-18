import { OllamaClient } from './ollama-client';
import { MANGA_OCR_PROMPT, MANGA_STRUCTURE_PROMPT } from './prompts';

/**
 * 漫画ページの文字起こし結果
 */
export interface MangaPageTranscription {
  page_number?: number;
  speech_bubbles: SpeechBubble[];
  narrations: Narration[];
  sound_effects: string[];
  page_description: string;
  has_text: boolean;
}

export interface SpeechBubble {
  speaker?: string;
  text: string;
  position: string;
  reading_order: number;
}

export interface Narration {
  text: string;
  position: string;
}

/**
 * Ollama Vision 漫画文字起こしマネージャー
 *
 * Windows + Ollama + LLaVA 環境専用
 * OCR不要で画像から直接セリフを抽出
 *
 * サポート済みモデル:
 * - llava:7b, llava:13b, llava:34b (推奨)
 * - llama3.2-vision:11b, llama3.2-vision:90b
 * - bakllava (軽量版)
 */
export class OllamaVisionManager {
  private ollama: OllamaClient;
  private verbose: boolean;
  private modelName: string;

  constructor(
    ollamaBaseUrl: string = 'http://localhost:11434',
    model: string = 'llava:7b',
    verbose: boolean = false
  ) {
    this.ollama = new OllamaClient({
      baseUrl: ollamaBaseUrl,
      model,
      temperature: 0.3, // 構造化出力なので低めに設定
      numCtx: 4096,
    });
    this.modelName = model;
    this.verbose = verbose;
  }

  /**
   * 初期化とヘルスチェック
   */
  async initialize(): Promise<void> {
    console.log(`🚀 Ollama 初期化中 (${this.modelName})...`);

    // Ollamaサーバー確認
    const isHealthy = await this.ollama.healthCheck();
    if (!isHealthy) {
      throw new Error(
        'Ollamaサーバーに接続できません。Ollamaを起動してください。'
      );
    }

    // モデル確認
    const modelExists = await this.ollama.checkModel();
    if (!modelExists) {
      throw new Error(
        `モデル ${this.modelName} が見つかりません。\n` +
          `以下を実行してください: ollama pull ${this.modelName}\n\n` +
          `推奨モデル:\n` +
          `  - llava:7b (バランス型、4.7GB)\n` +
          `  - llava:13b (高性能、8GB)\n` +
          `  - bakllava (軽量版、4.7GB)`
      );
    }

    console.log(`✅ Ollama 初期化完了 (${this.modelName})`);
  }

  /**
   * 漫画ページから文字起こしを実行
   *
   * @param imagePath 画像ファイルパス
   * @param pageNumber ページ番号（オプション）
   * @returns 構造化された文字起こし結果
   */
  async transcribePage(
    imagePath: string,
    pageNumber?: number
  ): Promise<MangaPageTranscription> {
    try {
      console.log(
        `\n📖 ページ ${pageNumber || '?'} の文字起こし開始...`
      );

      // プロンプトを構築
      const prompt = this.buildPrompt(pageNumber);

      // Ollama Vision で処理
      const response = await this.ollama.vision(prompt, imagePath, {
        format: 'json',
        temperature: 0.3,
      });

      // JSONパース
      const transcription = this.parseResponse(response, pageNumber);

      // 統計出力
      this.logStatistics(transcription);

      return transcription;
    } catch (error) {
      console.error(`❌ ページ ${pageNumber} の文字起こしエラー:`, error);

      // フォールバック：空の結果を返す
      return {
        page_number: pageNumber,
        speech_bubbles: [],
        narrations: [],
        sound_effects: [],
        page_description: 'エラーにより処理できませんでした',
        has_text: false,
      };
    }
  }

  /**
   * プロンプトを構築
   */
  private buildPrompt(pageNumber?: number): string {
    let prompt = MANGA_OCR_PROMPT;

    if (pageNumber) {
      prompt = `ページ番号: ${pageNumber}\n\n` + prompt;
    }

    return prompt;
  }

  /**
   * レスポンスをパース
   */
  private parseResponse(
    response: string,
    pageNumber?: number
  ): MangaPageTranscription {
    try {
      // JSONとして解析
      const cleaned = this.cleanJsonResponse(response);
      const parsed = JSON.parse(cleaned);

      // ページ番号を設定
      if (pageNumber) {
        parsed.page_number = pageNumber;
      }

      // 必須フィールドの検証
      return {
        page_number: parsed.page_number,
        speech_bubbles: Array.isArray(parsed.speech_bubbles)
          ? parsed.speech_bubbles
          : [],
        narrations: Array.isArray(parsed.narrations)
          ? parsed.narrations
          : [],
        sound_effects: Array.isArray(parsed.sound_effects)
          ? parsed.sound_effects
          : [],
        page_description:
          parsed.page_description || 'ページの説明がありません',
        has_text: parsed.has_text !== false,
      };
    } catch (error) {
      console.error('JSON解析エラー:', error);
      console.error('元のレスポンス:', response);

      // パースに失敗した場合は空のデータを返す
      return {
        page_number: pageNumber,
        speech_bubbles: [],
        narrations: [],
        sound_effects: [],
        page_description: 'JSON解析に失敗しました',
        has_text: false,
      };
    }
  }

  /**
   * JSONレスポンスをクリーンアップ
   */
  private cleanJsonResponse(response: string): string {
    // コードブロックを削除
    let cleaned = response.replace(/```json\n?/g, '');
    cleaned = cleaned.replace(/```\n?/g, '');

    // 前後の空白を削除
    cleaned = cleaned.trim();

    return cleaned;
  }

  /**
   * 統計情報をログ出力
   */
  private logStatistics(transcription: MangaPageTranscription): void {
    const stats = {
      セリフ: transcription.speech_bubbles.length,
      ナレーション: transcription.narrations.length,
      効果音: transcription.sound_effects.length,
    };

    console.log('✅ 文字起こし完了:');
    console.log(
      `   セリフ: ${stats.セリフ}個, ナレーション: ${stats.ナレーション}個, 効果音: ${stats.効果音}個`
    );

    if (this.verbose && transcription.speech_bubbles.length > 0) {
      console.log('\n📝 抽出されたセリフ:');
      transcription.speech_bubbles.forEach((bubble, index) => {
        const speaker = bubble.speaker ? `[${bubble.speaker}] ` : '';
        console.log(`   ${index + 1}. ${speaker}「${bubble.text}」`);
      });
    }
  }

  /**
   * バッチ処理：複数ページを処理
   */
  async transcribePages(
    imagePaths: string[],
    startPageNumber: number = 1
  ): Promise<MangaPageTranscription[]> {
    const results: MangaPageTranscription[] = [];

    for (let i = 0; i < imagePaths.length; i++) {
      const imagePath = imagePaths[i];
      const pageNumber = startPageNumber + i;

      try {
        const result = await this.transcribePage(imagePath, pageNumber);
        results.push(result);

        // API負荷軽減のため待機
        if (i < imagePaths.length - 1) {
          await this.sleep(1000);
        }
      } catch (error) {
        console.error(`ページ ${pageNumber} の処理に失敗:`, error);
        continue;
      }
    }

    return results;
  }

  /**
   * スリープ
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 結果をMarkdown形式でフォーマット
   */
  formatAsMarkdown(transcription: MangaPageTranscription): string {
    let output = '';

    output += `## ページ ${transcription.page_number || '?'}\n\n`;
    output += `**概要**: ${transcription.page_description}\n\n`;

    if (transcription.speech_bubbles.length > 0) {
      output += `### セリフ\n\n`;
      // 読む順番でソート
      const sorted = [...transcription.speech_bubbles].sort(
        (a, b) => a.reading_order - b.reading_order
      );

      sorted.forEach((bubble, index) => {
        const speaker = bubble.speaker ? `**${bubble.speaker}**: ` : '';
        output += `${index + 1}. ${speaker}「${bubble.text}」 _(${bubble.position})_\n`;
      });
      output += '\n';
    }

    if (transcription.narrations.length > 0) {
      output += `### ナレーション\n\n`;
      transcription.narrations.forEach((narration, index) => {
        output += `${index + 1}. ${narration.text} _(${narration.position})_\n`;
      });
      output += '\n';
    }

    if (transcription.sound_effects.length > 0) {
      output += `### 効果音\n\n`;
      output += `${transcription.sound_effects.join(', ')}\n\n`;
    }

    output += '---\n\n';

    return output;
  }
}
