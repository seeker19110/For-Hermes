import fs from 'fs/promises';
import path from 'path';

/**
 * Ollama API クライアント（修正版）
 *
 * 公式APIドキュメントに基づく正しい実装
 * https://github.com/ollama/ollama/blob/main/docs/api.md
 */

export interface OllamaConfig {
  baseUrl: string;
  model: string;
  temperature?: number;
  numCtx?: number;
}

export interface OllamaGenerateRequest {
  model: string;
  prompt: string;
  images?: string[];  // Base64エンコード画像の配列
  stream?: boolean;
  format?: 'json' | object;  // "json" または JSONスキーマ
  options?: {
    temperature?: number;
    num_ctx?: number;
    num_predict?: number;
  };
}

export interface OllamaGenerateResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
  context?: number[];
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  prompt_eval_duration?: number;
  eval_count?: number;
  eval_duration?: number;
}

/**
 * Ollama APIクライアント
 *
 * サポート済みVisionモデル:
 * - llava:7b, llava:13b, llava:34b
 * - llama3.2-vision:11b, llama3.2-vision:90b
 * - bakllava
 */
export class OllamaClient {
  private baseUrl: string;
  private model: string;
  private defaultOptions: any;

  constructor(config: OllamaConfig) {
    this.baseUrl = config.baseUrl || 'http://localhost:11434';
    // デフォルトは確実に動作する llava:7b
    this.model = config.model || 'llava:7b';
    this.defaultOptions = {
      temperature: config.temperature || 0.3,
      num_ctx: config.numCtx || 4096,
    };
  }

  /**
   * 画像ファイルをBase64エンコード
   */
  private async imageToBase64(imagePath: string): Promise<string> {
    try {
      const imageBuffer = await fs.readFile(imagePath);
      return imageBuffer.toString('base64');
    } catch (error) {
      console.error(`画像読み込みエラー: ${imagePath}`, error);
      throw error;
    }
  }

  /**
   * Visionリクエストを送信
   *
   * @param prompt テキストプロンプト
   * @param imagePath 画像ファイルパス
   * @param options オプション設定
   * @returns LLMの応答テキスト
   */
  async vision(
    prompt: string,
    imagePath: string,
    options?: {
      format?: 'json';
      temperature?: number;
      stream?: boolean;
    }
  ): Promise<string> {
    try {
      console.log(`🔍 ${this.model} でVision処理開始: ${path.basename(imagePath)}`);

      // 画像をBase64エンコード
      const imageBase64 = await this.imageToBase64(imagePath);

      // リクエスト構築（公式ドキュメント準拠）
      const request: OllamaGenerateRequest = {
        model: this.model,
        prompt,
        images: [imageBase64],  // 配列形式
        stream: options?.stream ?? false,
        options: {
          temperature: options?.temperature ?? this.defaultOptions.temperature,
          num_ctx: this.defaultOptions.num_ctx,
        },
      };

      // JSON形式指定（オプション）
      if (options?.format === 'json') {
        request.format = 'json';
      }

      // API呼び出し
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Ollama API エラー: ${response.status} ${response.statusText}\n${errorText}`
        );
      }

      // ストリーミングなしの場合、単一のJSONレスポンス
      const data: OllamaGenerateResponse = await response.json();

      console.log(`✅ Vision処理完了 (${data.eval_count || 0} tokens)`);

      return data.response;
    } catch (error) {
      console.error('❌ Ollama Vision APIエラー:', error);
      throw error;
    }
  }

  /**
   * ストリーミングVisionリクエスト（オプション）
   *
   * リアルタイムでレスポンスを受信
   */
  async visionStream(
    prompt: string,
    imagePath: string,
    onChunk: (chunk: string) => void,
    options?: {
      format?: 'json';
      temperature?: number;
    }
  ): Promise<string> {
    try {
      const imageBase64 = await this.imageToBase64(imagePath);

      const request: OllamaGenerateRequest = {
        model: this.model,
        prompt,
        images: [imageBase64],
        stream: true,  // ストリーミング有効
        options: {
          temperature: options?.temperature ?? this.defaultOptions.temperature,
          num_ctx: this.defaultOptions.num_ctx,
        },
      };

      if (options?.format === 'json') {
        request.format = 'json';
      }

      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Ollama API エラー: ${response.status}`);
      }

      // ストリーミングレスポンスを処理
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('レスポンスボディが取得できません');
      }

      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data: OllamaGenerateResponse = JSON.parse(line);
            if (data.response) {
              fullResponse += data.response;
              onChunk(data.response);
            }
          } catch (e) {
            // JSON解析エラーは無視
          }
        }
      }

      return fullResponse;
    } catch (error) {
      console.error('Ollama Vision Streamエラー:', error);
      throw error;
    }
  }

  /**
   * モデルが利用可能か確認
   */
  async checkModel(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`);
      const data = await response.json();

      const modelExists = data.models?.some(
        (m: any) => m.name.startsWith(this.model.split(':')[0])
      );

      if (!modelExists) {
        console.warn(
          `⚠️ モデル ${this.model} が見つかりません。\n` +
          `   ollama pull ${this.model} を実行してください。\n\n` +
          `   利用可能なVisionモデル:\n` +
          `   - llava:7b (推奨、4.7GB)\n` +
          `   - llava:13b (高性能、8GB)\n` +
          `   - llama3.2-vision:11b (最新、7.9GB)\n` +
          `   - bakllava (軽量、4.7GB)`
        );
      }

      return modelExists;
    } catch (error) {
      console.error('Ollama接続確認エラー:', error);
      return false;
    }
  }

  /**
   * Ollamaサーバーの状態確認
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, {
        signal: AbortSignal.timeout(5000),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ Ollama接続成功`);
        console.log(`   インストール済みモデル: ${data.models?.length || 0}個`);
        return true;
      }

      return false;
    } catch (error) {
      console.error('❌ Ollamaサーバーに接続できません');
      console.log('\n💡 トラブルシューティング:');
      console.log('   1. Ollama for Windows が起動しているか確認');
      console.log(`   2. ブラウザで ${this.baseUrl} にアクセス`);
      console.log('   3. タスクマネージャーで "ollama" プロセスを確認\n');
      return false;
    }
  }

  /**
   * 利用可能なモデル一覧を取得
   */
  async listModels(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`);
      const data = await response.json();

      return data.models?.map((m: any) => m.name) || [];
    } catch (error) {
      console.error('モデル一覧取得エラー:', error);
      return [];
    }
  }

  /**
   * モデルの詳細情報を取得
   */
  async getModelInfo(modelName?: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/show`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: modelName || this.model }),
      });

      return await response.json();
    } catch (error) {
      console.error('モデル情報取得エラー:', error);
      return null;
    }
  }
}
