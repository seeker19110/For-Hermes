import fs from 'fs/promises';
import path from 'path';

/**
 * ページキャプチャの状態
 */
export interface PageCapture {
  pageNumber: number;
  timestamp: number;
  imagePath: string;
  processed: boolean;
  transcription?: any; // MangaPageTranscription
}

/**
 * セッション全体の状態管理
 * Factor 5: Unify execution state and business state
 */
export class CaptureSession {
  sessionId: string;
  startTime: number;
  pages: PageCapture[] = [];
  currentPage: number = 0;
  captureDir: string;
  outputDir: string;

  constructor(sessionId: string, captureDir: string, outputDir: string) {
    this.sessionId = sessionId;
    this.startTime = Date.now();
    this.captureDir = captureDir;
    this.outputDir = outputDir;
  }

  /**
   * 新しいページキャプチャを追加
   */
  addCapture(imagePath: string): PageCapture {
    this.currentPage++;
    const capture: PageCapture = {
      pageNumber: this.currentPage,
      timestamp: Date.now(),
      imagePath,
      processed: false,
    };
    this.pages.push(capture);
    return capture;
  }

  /**
   * ページの文字起こし結果を保存
   */
  setTranscription(pageNumber: number, transcription: any): void {
    const page = this.pages.find(p => p.pageNumber === pageNumber);
    if (page) {
      page.transcription = transcription;
      page.processed = true;
    }
  }

  /**
   * セッション状態をJSONファイルに保存
   */
  async save(): Promise<void> {
    const outputPath = path.join(
      this.outputDir,
      `session-${this.sessionId}.json`
    );

    const data = {
      sessionId: this.sessionId,
      startTime: this.startTime,
      endTime: Date.now(),
      totalPages: this.pages.length,
      pages: this.pages.map(p => ({
        pageNumber: p.pageNumber,
        timestamp: p.timestamp,
        imagePath: p.imagePath,
        processed: p.processed,
        transcription: p.transcription,
      })),
    };

    await fs.mkdir(this.outputDir, { recursive: true });
    await fs.writeFile(outputPath, JSON.stringify(data, null, 2), 'utf-8');
    console.log(`✅ セッションを保存しました: ${outputPath}`);
  }

  /**
   * セッションを読み込み
   */
  static async load(
    sessionId: string,
    outputDir: string,
    captureDir: string
  ): Promise<CaptureSession> {
    const outputPath = path.join(outputDir, `session-${sessionId}.json`);
    const data = JSON.parse(await fs.readFile(outputPath, 'utf-8'));

    const session = new CaptureSession(sessionId, captureDir, outputDir);
    session.startTime = data.startTime;
    session.currentPage = data.totalPages;
    session.pages = data.pages;

    return session;
  }

  /**
   * 未処理のページを取得
   */
  getUnprocessedPages(): PageCapture[] {
    return this.pages.filter(p => !p.processed);
  }

  /**
   * 統計情報を取得
   */
  getStats() {
    return {
      totalPages: this.pages.length,
      processedPages: this.pages.filter(p => p.processed).length,
      unprocessedPages: this.pages.filter(p => !p.processed).length,
      duration: Date.now() - this.startTime,
    };
  }
}

/**
 * セッションストア（複数セッション管理）
 */
export class SessionStore {
  private sessions: Map<string, CaptureSession> = new Map();
  private captureDir: string;
  private outputDir: string;

  constructor(captureDir: string, outputDir: string) {
    this.captureDir = captureDir;
    this.outputDir = outputDir;
  }

  /**
   * 新しいセッションを作成
   */
  createSession(): CaptureSession {
    const sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const session = new CaptureSession(
      sessionId,
      this.captureDir,
      this.outputDir
    );
    this.sessions.set(sessionId, session);
    return session;
  }

  /**
   * セッションを取得
   */
  getSession(sessionId: string): CaptureSession | undefined {
    return this.sessions.get(sessionId);
  }

  /**
   * 全セッションを取得
   */
  getAllSessions(): CaptureSession[] {
    return Array.from(this.sessions.values());
  }
}
