#!/usr/bin/env node

import dotenv from 'dotenv';
import path from 'path';
import { CaptureSession, SessionStore } from './state';
import {
  MangaCaptureAgent,
  MangaCaptureAgentBuilder,
} from './agent';
import {
  VisionLLMManager,
  MockVisionLLMManager,
} from './vision-llm';

// 環境変数を読み込み
dotenv.config();

/**
 * メインCLIプログラム
 *
 * 使用例:
 *   npm run dev capture          # キャプチャモード開始
 *   npm run dev process          # 未処理ページを文字起こし
 *   npm run dev capture --mock   # モックモード（テスト用）
 */

interface CLIOptions {
  mock?: boolean;
  noObs?: boolean;
  interval?: number;
  sessionId?: string;
}

class MangaCaptureСLI {
  private store: SessionStore;
  private captureDir: string;
  private outputDir: string;

  constructor() {
    this.captureDir =
      process.env.CAPTURE_DIR || path.join(process.cwd(), 'captures');
    this.outputDir =
      process.env.OUTPUT_DIR || path.join(process.cwd(), 'output');
    this.store = new SessionStore(this.captureDir, this.outputDir);
  }

  /**
   * キャプチャモード: ページめくり検知して自動キャプチャ
   */
  async runCaptureMode(options: CLIOptions = {}): Promise<void> {
    console.log('📚 漫画キャプチャモード開始\n');

    // セッション作成
    const session = this.store.createSession();
    console.log(`🆔 セッションID: ${session.sessionId}\n`);

    // Vision LLM設定
    const visionLLM = options.mock
      ? new MockVisionLLMManager()
      : new VisionLLMManager();

    // モックでない場合はBAMLクライアントを設定
    if (!options.mock) {
      try {
        // BAMLクライアントをインポート
        // const { b } = require('../baml_client');
        // visionLLM.setBAMLClient(b);
        console.log(
          '⚠️  BAMLクライアントが見つかりません。モックモードで実行します。'
        );
        console.log('   npx baml-cli generate を実行してください。\n');
      } catch (error) {
        console.log('⚠️  モックモードで実行します\n');
      }
    }

    // エージェント構築
    const agent = new MangaCaptureAgentBuilder()
      .setCaptureDir(this.captureDir)
      .setOutputDir(this.outputDir)
      .setCaptureInterval(
        options.interval || parseInt(process.env.CAPTURE_INTERVAL_MS || '1000')
      )
      .setAutoTranscribe(true)
      .build(session, visionLLM);

    // OBS設定
    if (!options.noObs) {
      const obsUrl = process.env.OBS_WEBSOCKET_URL || 'ws://localhost:4455';
      const obsPassword = process.env.OBS_WEBSOCKET_PASSWORD;
      console.log(`🎥 OBS WebSocket: ${obsUrl}`);
    } else {
      console.log('🖥️  システムスクリーンキャプチャを使用');
    }

    // イベントリスナー設定
    agent.on('page_detected', (data: any) => {
      console.log(
        `\n📖 新しいページを検知: ページ ${data.pageNumber}`
      );
      console.log(`   画像: ${path.basename(data.imagePath)}`);
    });

    agent.on('transcription_completed', (data: any) => {
      console.log(`\n✅ ページ ${data.pageNumber} 文字起こし完了`);
      const t = data.transcription;
      console.log(`   セリフ: ${t.speech_bubbles.length}個`);
      console.log(`   ナレーション: ${t.narrations.length}個`);
      console.log(`   効果音: ${t.sound_effects.length}個`);
    });

    agent.on('error', (data: any) => {
      console.error(`\n❌ エラー: ${data.error.message}`);
    });

    // 初期化
    await agent.initialize();

    // キャプチャループ開始
    await agent.startCaptureLoop();

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📸 キャプチャ実行中...');
    console.log('   OBSで漫画を表示し、ページをめくってください');
    console.log('   Ctrl+C で終了');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    // Ctrl+C でクリーンアップ
    process.on('SIGINT', async () => {
      console.log('\n\n⏹️  キャプチャ停止中...');
      await agent.cleanup();

      const stats = agent.getStats();
      console.log('\n📊 セッション統計:');
      console.log(`   総ページ数: ${stats.totalPages}`);
      console.log(`   処理済み: ${stats.processedPages}`);
      console.log(`   未処理: ${stats.unprocessedPages}`);
      console.log(`   実行時間: ${Math.round(stats.duration / 1000)}秒`);

      process.exit(0);
    });
  }

  /**
   * 処理モード: 未処理ページを文字起こし
   */
  async runProcessMode(options: CLIOptions = {}): Promise<void> {
    console.log('📝 未処理ページ処理モード\n');

    if (!options.sessionId) {
      console.error('❌ --sessionId が必要です');
      process.exit(1);
    }

    // セッション読み込み
    const session = await CaptureSession.load(
      options.sessionId,
      this.outputDir,
      this.captureDir
    );

    console.log(`🆔 セッションID: ${session.sessionId}`);

    const unprocessed = session.getUnprocessedPages();
    console.log(`📄 未処理ページ: ${unprocessed.length}件\n`);

    if (unprocessed.length === 0) {
      console.log('✅ すべて処理済みです');
      return;
    }

    // Vision LLM設定
    const visionLLM = options.mock
      ? new MockVisionLLMManager()
      : new VisionLLMManager();

    // エージェント構築
    const agent = new MangaCaptureAgentBuilder()
      .setCaptureDir(this.captureDir)
      .setOutputDir(this.outputDir)
      .setAutoTranscribe(false)
      .build(session, visionLLM);

    await agent.initialize();

    // 未処理ページを処理
    await agent.transcribeUnprocessedPages();

    // セッション保存
    await session.save();

    console.log('\n✅ すべてのページを処理しました');
  }

  /**
   * ヘルプ表示
   */
  showHelp(): void {
    console.log(`
OBS漫画自動キャプチャ＆文字起こしシステム
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

使用方法:

  📸 キャプチャモード（リアルタイムでページを検知）:
    npm run dev capture

  📝 処理モード（未処理ページを文字起こし）:
    npm run dev process --sessionId=<session-id>

オプション:
  --mock           モックモード（テスト用）
  --no-obs         OBSを使わずシステムキャプチャを使用
  --interval=<ms>  キャプチャ間隔（デフォルト: 1000ms）
  --sessionId=<id> セッションID（処理モードで必要）

環境変数（.envファイルに設定）:
  OPENAI_API_KEY            OpenAI APIキー
  ANTHROPIC_API_KEY         Anthropic APIキー
  OBS_WEBSOCKET_URL         OBS WebSocket URL
  OBS_WEBSOCKET_PASSWORD    OBS WebSocket パスワード
  CAPTURE_DIR               キャプチャ保存先
  OUTPUT_DIR                出力先

セットアップ:
  1. npm install
  2. .envファイルを作成（.env.exampleを参照）
  3. npx baml-cli init
  4. npx baml-cli generate
  5. OBS Studioを起動してWebSocketを有効化

詳細: README.md を参照
`);
  }
}

/**
 * メイン関数
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // オプション解析
  const options: CLIOptions = {
    mock: args.includes('--mock'),
    noObs: args.includes('--no-obs'),
  };

  // interval オプション
  const intervalArg = args.find(arg => arg.startsWith('--interval='));
  if (intervalArg) {
    options.interval = parseInt(intervalArg.split('=')[1]);
  }

  // sessionId オプション
  const sessionIdArg = args.find(arg => arg.startsWith('--sessionId='));
  if (sessionIdArg) {
    options.sessionId = sessionIdArg.split('=')[1];
  }

  const cli = new MangaCaptureСLI();

  try {
    switch (command) {
      case 'capture':
        await cli.runCaptureMode(options);
        break;

      case 'process':
        await cli.runProcessMode(options);
        break;

      case 'help':
      case '--help':
      case '-h':
        cli.showHelp();
        break;

      default:
        console.log('❌ 不明なコマンド:', command);
        cli.showHelp();
        process.exit(1);
    }
  } catch (error) {
    console.error('❌ エラー:', error);
    process.exit(1);
  }
}

// 実行
if (require.main === module) {
  main();
}

export { MangaCaptureСLI };
