import { CaptureSession } from './state';
import { PageDetector } from './page-detector';
import { CaptureManager } from './capture';
import { VisionLLMManager, MangaPageTranscription } from './vision-llm';
import { EventEmitter } from 'events';

/**
 * エージェントイベント
 */
export interface AgentEvent {
  type:
    | 'capture_started'
    | 'page_detected'
    | 'transcription_started'
    | 'transcription_completed'
    | 'capture_completed'
    | 'error';
  data: any;
  timestamp: number;
}

/**
 * エージェント設定
 */
export interface AgentConfig {
  captureDir: string;
  outputDir: string;
  useOBS: boolean;
  obsUrl?: string;
  obsPassword?: string;
  captureInterval: number;
  autoTranscribe: boolean;
  similarityThreshold: number;
}

/**
 * 漫画キャプチャエージェント
 *
 * 12-Factor Agents原則の実装:
 * - Factor 1: 画像 → セリフ抽出のツール呼び出し
 * - Factor 2: プロンプトをBAMLで管理
 * - Factor 3: キャプチャ履歴をコンテキストとして管理
 * - Factor 5: 状態の統合管理
 * - Factor 6: Pause/Resume可能
 * - Factor 8: 制御フローの完全管理
 */
export class MangaCaptureAgent extends EventEmitter {
  private session: CaptureSession;
  private pageDetector: PageDetector;
  private captureManager: CaptureManager;
  private visionLLM: VisionLLMManager;
  private config: AgentConfig;
  private isRunning: boolean = false;
  private captureInterval?: NodeJS.Timeout;

  constructor(
    session: CaptureSession,
    visionLLM: VisionLLMManager,
    config: AgentConfig
  ) {
    super();
    this.session = session;
    this.visionLLM = visionLLM;
    this.config = config;
    this.pageDetector = new PageDetector(
      config.similarityThreshold,
      0.15
    );
    this.captureManager = new CaptureManager(
      config.captureDir,
      config.useOBS
    );
  }

  /**
   * エージェント初期化
   */
  async initialize(): Promise<void> {
    console.log('🚀 エージェント初期化中...');

    await this.captureManager.initialize(
      this.config.obsUrl,
      this.config.obsPassword
    );

    this.emitEvent('capture_started', {
      sessionId: this.session.sessionId,
    });

    console.log('✅ エージェント初期化完了');
  }

  /**
   * キャプチャループ開始
   *
   * Factor 8: Own your control flow
   */
  async startCaptureLoop(): Promise<void> {
    if (this.isRunning) {
      console.log('⚠️ すでに実行中です');
      return;
    }

    this.isRunning = true;
    console.log(
      `▶️  キャプチャループ開始 (間隔: ${this.config.captureInterval}ms)`
    );

    this.captureInterval = setInterval(async () => {
      await this.captureAndProcess();
    }, this.config.captureInterval);
  }

  /**
   * キャプチャと処理のメインループ
   *
   * Factor 1: 自然言語→ツール呼び出しパターン
   * ここでは 画像→文字起こし のツール呼び出し
   */
  private async captureAndProcess(): Promise<void> {
    try {
      // ステップ1: スクリーンショットを撮影
      const imagePath = await this.captureManager.capture();

      // ステップ2: ページめくり検知
      const isNewPage = await this.pageDetector.detectPageChange(
        imagePath
      );

      if (!isNewPage) {
        // 同じページなので処理をスキップ
        return;
      }

      // ステップ3: 新しいページとして記録
      const capture = this.session.addCapture(imagePath);

      this.emitEvent('page_detected', {
        pageNumber: capture.pageNumber,
        imagePath,
      });

      // ステップ4: 自動文字起こし（オプション）
      if (this.config.autoTranscribe) {
        await this.transcribePage(capture.pageNumber);
      }
    } catch (error) {
      console.error('❌ キャプチャ処理エラー:', error);
      this.emitEvent('error', { error });
    }
  }

  /**
   * 特定のページを文字起こし
   *
   * Factor 4: Tools are structured outputs
   */
  async transcribePage(pageNumber: number): Promise<void> {
    const page = this.session.pages.find(
      p => p.pageNumber === pageNumber
    );

    if (!page) {
      throw new Error(`ページ ${pageNumber} が見つかりません`);
    }

    if (page.processed) {
      console.log(`⏭️  ページ ${pageNumber} は処理済みです`);
      return;
    }

    try {
      this.emitEvent('transcription_started', {
        pageNumber,
        imagePath: page.imagePath,
      });

      // Vision LLMで文字起こし
      const transcription = await this.visionLLM.transcribePage(
        page.imagePath,
        pageNumber
      );

      // セッションに保存
      this.session.setTranscription(pageNumber, transcription);

      this.emitEvent('transcription_completed', {
        pageNumber,
        transcription,
      });

      console.log(`✅ ページ ${pageNumber} の文字起こし完了`);
    } catch (error) {
      console.error(`❌ ページ ${pageNumber} の文字起こしエラー:`, error);
      this.emitEvent('error', { error, pageNumber });
      throw error;
    }
  }

  /**
   * 未処理のページをまとめて文字起こし
   */
  async transcribeUnprocessedPages(): Promise<void> {
    const unprocessed = this.session.getUnprocessedPages();

    console.log(`📝 未処理ページ: ${unprocessed.length}件`);

    for (const page of unprocessed) {
      await this.transcribePage(page.pageNumber);
      // レート制限対策
      await this.sleep(1000);
    }
  }

  /**
   * キャプチャループ停止
   *
   * Factor 6: Pause/Resume
   */
  async stopCaptureLoop(): Promise<void> {
    if (!this.isRunning) {
      console.log('⚠️ 実行されていません');
      return;
    }

    if (this.captureInterval) {
      clearInterval(this.captureInterval);
      this.captureInterval = undefined;
    }

    this.isRunning = false;
    console.log('⏸️  キャプチャループ停止');

    // セッションを保存
    await this.session.save();
  }

  /**
   * 再開
   *
   * Factor 6: Resume
   */
  async resumeCaptureLoop(): Promise<void> {
    console.log('▶️  キャプチャループ再開');
    await this.startCaptureLoop();
  }

  /**
   * クリーンアップ
   */
  async cleanup(): Promise<void> {
    await this.stopCaptureLoop();
    await this.captureManager.cleanup();
    console.log('🧹 クリーンアップ完了');
  }

  /**
   * イベント発行
   */
  private emitEvent(
    type: AgentEvent['type'],
    data: any
  ): void {
    const event: AgentEvent = {
      type,
      data,
      timestamp: Date.now(),
    };
    this.emit('event', event);
    this.emit(type, data);
  }

  /**
   * 統計情報取得
   */
  getStats() {
    return this.session.getStats();
  }

  /**
   * セッション取得
   */
  getSession(): CaptureSession {
    return this.session;
  }

  /**
   * ユーティリティ: スリープ
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * エージェントビルダー
 *
 * 設定を簡単に組み立てるためのビルダーパターン
 */
export class MangaCaptureAgentBuilder {
  private config: Partial<AgentConfig> = {
    useOBS: true,
    captureInterval: 1000,
    autoTranscribe: true,
    similarityThreshold: 0.85,
  };

  setCaptureDir(dir: string): this {
    this.config.captureDir = dir;
    return this;
  }

  setOutputDir(dir: string): this {
    this.config.outputDir = dir;
    return this;
  }

  setOBS(url: string, password?: string): this {
    this.config.useOBS = true;
    this.config.obsUrl = url;
    this.config.obsPassword = password;
    return this;
  }

  disableOBS(): this {
    this.config.useOBS = false;
    return this;
  }

  setCaptureInterval(ms: number): this {
    this.config.captureInterval = ms;
    return this;
  }

  setAutoTranscribe(enabled: boolean): this {
    this.config.autoTranscribe = enabled;
    return this;
  }

  setSimilarityThreshold(threshold: number): this {
    this.config.similarityThreshold = threshold;
    return this;
  }

  build(
    session: CaptureSession,
    visionLLM: VisionLLMManager
  ): MangaCaptureAgent {
    if (!this.config.captureDir || !this.config.outputDir) {
      throw new Error(
        'captureDir と outputDir は必須です'
      );
    }

    return new MangaCaptureAgent(
      session,
      visionLLM,
      this.config as AgentConfig
    );
  }
}
