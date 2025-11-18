import fs from 'fs/promises';
import path from 'path';

/**
 * Ollama API クライアント
 *
 * Windows + Ollama + Qwen2-VL 環境専用
 */
export interface OllamaConfig {
  baseUrl: string;
  model: string;
  temperature?: number;
  numCtx?: number;
}

export interface OllamaVisionRequest {
  model: string;
  prompt: string;
  images: string[];  // base64エンコード画像
  stream?: boolean;
  format?: 'json';
  options?: {
    temperature?: number;
    num_ctx?: number;
    num_predict?: number;
  };
}

export interface OllamaResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
  context?: number[];
  total_duration?: number;
  load_duration?: number;
  prompt_eval_duration?: number;
  eval_duration?: number;
}

/**
 * Ollama APIクライアント
 */
export class OllamaClient {
  private baseUrl: string;
  private model: string;
  private defaultOptions: any;

  constructor(config: OllamaConfig) {
    this.baseUrl = config.baseUrl || 'http://localhost:11434';
    this.model = config.model || 'qwen2-vl:7b';
    this.defaultOptions = {
      temperature: config.temperature || 0.7,
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
      console.log(`🔍 Qwen2-VL でVision処理開始: ${path.basename(imagePath)}`);

      // 画像をBase64エンコード
      const imageBase64 = await this.imageToBase64(imagePath);

      // リクエスト構築
      const request: OllamaVisionRequest = {
        model: this.model,
        prompt,
        images: [imageBase64],
        stream: options?.stream || false,
        format: options?.format,
        options: {
          temperature: options?.temperature || this.defaultOptions.temperature,
          num_ctx: this.defaultOptions.num_ctx,
        },
      };

      // API呼び出し
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(
          `Ollama API エラー: ${response.status} ${response.statusText}`
        );
      }

      const data: OllamaResponse = await response.json();

      console.log(`✅ Vision処理完了`);
      return data.response;
    } catch (error) {
      console.error('❌ Ollama Vision APIエラー:', error);
      throw error;
    }
  }

  /**
   * チャット形式でリクエスト（オプション）
   */
  async chat(
    messages: Array<{
      role: 'system' | 'user' | 'assistant';
      content: string;
      images?: string[];
    }>
  ): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.model,
          messages,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`Ollama Chat APIエラー: ${response.status}`);
      }

      const data = await response.json();
      return data.message.content;
    } catch (error) {
      console.error('Ollama Chat APIエラー:', error);
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
        (m: any) => m.name === this.model
      );

      if (!modelExists) {
        console.warn(
          `⚠️ モデル ${this.model} が見つかりません。` +
            `\nollama pull ${this.model} を実行してください。`
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
      return response.ok;
    } catch (error) {
      console.error('❌ Ollamaサーバーに接続できません');
      console.log('💡 Ollamaが起動しているか確認してください：');
      console.log('   1. Ollama for Windows を起動');
      console.log(`   2. ブラウザで ${this.baseUrl} にアクセス`);
      return false;
    }
  }
}
