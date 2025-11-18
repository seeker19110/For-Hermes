import fs from 'fs/promises';
import path from 'path';

/**
 * Vision LLMインテグレーション
 *
 * Factor 1: Natural Language to Tool Calls
 * Factor 2: Own your prompts (BAMLで管理)
 * Factor 4: Tools are structured outputs
 *
 * 注意: このファイルはBAML generateコマンド実行後に
 * baml_clientからインポートして使用します
 */

// BAMLクライアントの型定義（generate後に利用可能）
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

export interface MangaPageTranscription {
  page_number?: number;
  speech_bubbles: SpeechBubble[];
  narrations: Narration[];
  sound_effects: string[];
  page_description: string;
  has_text: boolean;
}

/**
 * Vision LLMマネージャー
 *
 * BAMLで定義したプロンプトを使って画像解析を実行
 */
export class VisionLLMManager {
  private bamlClient: any; // BAMLクライアント

  constructor() {
    // BAMLクライアントは動的にインポート
    // 実際の実装ではnpx baml-cli generate後にこうなります:
    // import { b } from '../baml_client';
    // this.bamlClient = b;
  }

  /**
   * BAMLクライアントを設定
   */
  setBAMLClient(client: any): void {
    this.bamlClient = client;
  }

  /**
   * 画像をBase64エンコード
   */
  private async imageToBase64(imagePath: string): Promise<string> {
    const imageBuffer = await fs.readFile(imagePath);
    return imageBuffer.toString('base64');
  }

  /**
   * 漫画ページから文字起こしを実行
   *
   * @param imagePath 画像ファイルのパス
   * @param pageNumber ページ番号（オプション）
   * @returns 構造化された文字起こし結果
   */
  async transcribePage(
    imagePath: string,
    pageNumber?: number
  ): Promise<MangaPageTranscription> {
    if (!this.bamlClient) {
      throw new Error(
        'BAMLクライアントが設定されていません。npx baml-cli generateを実行してください。'
      );
    }

    try {
      console.log(`🔍 文字起こし開始: ${path.basename(imagePath)}`);

      // BAMLで定義したTranscribeMangaPage関数を呼び出し
      const result = await this.bamlClient.TranscribeMangaPage(
        imagePath,
        pageNumber
      );

      console.log(
        `✅ 文字起こし完了: セリフ ${result.speech_bubbles.length}個, ナレーション ${result.narrations.length}個`
      );

      return result;
    } catch (error) {
      console.error('❌ 文字起こしエラー:', error);
      throw error;
    }
  }

  /**
   * バッチ処理: 複数のページを一度に処理
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

        // API rate limitを避けるため少し待機
        await this.sleep(1000);
      } catch (error) {
        console.error(`ページ ${pageNumber} の処理に失敗:`, error);
        // エラーがあっても続行
        continue;
      }
    }

    return results;
  }

  /**
   * 文字起こし結果をフォーマット（人間が読みやすい形式）
   */
  formatTranscription(transcription: MangaPageTranscription): string {
    let output = '';

    output += `=== ページ ${transcription.page_number || '?'} ===\n\n`;
    output += `【概要】\n${transcription.page_description}\n\n`;

    if (transcription.speech_bubbles.length > 0) {
      output += `【セリフ】\n`;
      // 読む順番でソート
      const sortedBubbles = [...transcription.speech_bubbles].sort(
        (a, b) => a.reading_order - b.reading_order
      );

      sortedBubbles.forEach((bubble, index) => {
        const speaker = bubble.speaker ? `${bubble.speaker}: ` : '';
        output += `  ${index + 1}. ${speaker}「${bubble.text}」 (${bubble.position})\n`;
      });
      output += '\n';
    }

    if (transcription.narrations.length > 0) {
      output += `【ナレーション】\n`;
      transcription.narrations.forEach((narration, index) => {
        output += `  ${index + 1}. ${narration.text} (${narration.position})\n`;
      });
      output += '\n';
    }

    if (transcription.sound_effects.length > 0) {
      output += `【効果音】\n`;
      output += `  ${transcription.sound_effects.join(', ')}\n\n`;
    }

    return output;
  }

  /**
   * 文字起こし結果をMarkdown形式で保存
   */
  async saveAsMarkdown(
    transcriptions: MangaPageTranscription[],
    outputPath: string
  ): Promise<void> {
    let markdown = '# 漫画文字起こし\n\n';
    markdown += `生成日時: ${new Date().toLocaleString('ja-JP')}\n\n`;
    markdown += `総ページ数: ${transcriptions.length}\n\n`;
    markdown += '---\n\n';

    for (const transcription of transcriptions) {
      markdown += this.formatTranscription(transcription);
      markdown += '---\n\n';
    }

    await fs.writeFile(outputPath, markdown, 'utf-8');
    console.log(`📄 Markdownファイルを保存しました: ${outputPath}`);
  }

  /**
   * ユーティリティ: スリープ
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * モックVision LLMマネージャー（テスト用）
 *
 * BAMLが設定されていない場合や、テスト時に使用
 */
export class MockVisionLLMManager extends VisionLLMManager {
  async transcribePage(
    imagePath: string,
    pageNumber?: number
  ): Promise<MangaPageTranscription> {
    console.log(`🎭 [MOCK] 文字起こし: ${path.basename(imagePath)}`);

    // ダミーデータを返す
    return {
      page_number: pageNumber,
      speech_bubbles: [
        {
          speaker: '主人公',
          text: 'これはモックデータです',
          position: 'top-right',
          reading_order: 1,
        },
        {
          text: 'BAMLを設定すると実際の文字起こしが実行されます',
          position: 'bottom-left',
          reading_order: 2,
        },
      ],
      narrations: [
        {
          text: 'こうして物語は始まった...',
          position: 'top-center',
        },
      ],
      sound_effects: ['ゴゴゴゴ', 'ドーン'],
      page_description: 'モックページの説明',
      has_text: true,
    };
  }
}
