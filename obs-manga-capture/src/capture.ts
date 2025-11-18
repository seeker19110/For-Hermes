import OBSWebSocket from 'obs-websocket-js';
import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * OBS経由のスクリーンキャプチャ
 *
 * Factor 8: Own your control flow - キャプチャタイミングの完全制御
 */
export class OBSCapture {
  private obs: OBSWebSocket;
  private connected: boolean = false;
  private captureDir: string;
  private sceneName?: string;

  constructor(captureDir: string) {
    this.obs = new OBSWebSocket();
    this.captureDir = captureDir;
  }

  /**
   * OBS WebSocketに接続
   */
  async connect(
    url: string = 'ws://localhost:4455',
    password?: string
  ): Promise<void> {
    try {
      await this.obs.connect(url, password);
      this.connected = true;
      console.log('✅ OBS WebSocketに接続しました');

      // 現在のシーン名を取得
      const { currentProgramSceneName } = await this.obs.call(
        'GetCurrentProgramScene'
      );
      this.sceneName = currentProgramSceneName;
      console.log(`📺 現在のシーン: ${this.sceneName}`);
    } catch (error) {
      console.error('❌ OBS接続エラー:', error);
      throw error;
    }
  }

  /**
   * OBSからスクリーンショットを撮影
   */
  async captureScreenshot(filename?: string): Promise<string> {
    if (!this.connected) {
      throw new Error('OBSに接続されていません');
    }

    try {
      const timestamp = Date.now();
      const outputFilename =
        filename || `capture-${timestamp}.png`;
      const outputPath = path.join(this.captureDir, outputFilename);

      // ディレクトリが存在しない場合は作成
      await fs.mkdir(this.captureDir, { recursive: true });

      // OBSでスクリーンショットを撮影
      const response = await this.obs.call('SaveSourceScreenshot', {
        sourceName: this.sceneName || 'Scene', // シーン名を指定
        imageFormat: 'png',
        imageFilePath: outputPath,
        imageWidth: 1920, // 必要に応じて調整
        imageHeight: 1080,
      });

      console.log(`📸 スクリーンショット保存: ${outputPath}`);
      return outputPath;
    } catch (error) {
      console.error('❌ スクリーンショット撮影エラー:', error);
      throw error;
    }
  }

  /**
   * ホットキーでスクリーンショットをトリガー
   */
  async triggerHotkey(hotkeyName: string): Promise<void> {
    if (!this.connected) {
      throw new Error('OBSに接続されていません');
    }

    try {
      await this.obs.call('TriggerHotkeyByName', {
        hotkeyName,
      });
      console.log(`⌨️ ホットキートリガー: ${hotkeyName}`);
    } catch (error) {
      console.error('❌ ホットキートリガーエラー:', error);
      throw error;
    }
  }

  /**
   * 録画状態を取得
   */
  async getRecordingStatus(): Promise<boolean> {
    if (!this.connected) {
      return false;
    }

    try {
      const { outputActive } = await this.obs.call('GetRecordStatus');
      return outputActive;
    } catch (error) {
      console.error('録画状態取得エラー:', error);
      return false;
    }
  }

  /**
   * 切断
   */
  async disconnect(): Promise<void> {
    if (this.connected) {
      await this.obs.disconnect();
      this.connected = false;
      console.log('🔌 OBSから切断しました');
    }
  }
}

/**
 * フォールバック: OBSなしでもスクリーンショットを撮る
 *
 * macOS: screencapture
 * Linux: scrot または import (ImageMagick)
 * Windows: PowerShell
 */
export class SystemCapture {
  private captureDir: string;
  private platform: NodeJS.Platform;

  constructor(captureDir: string) {
    this.captureDir = captureDir;
    this.platform = process.platform;
  }

  /**
   * システムのスクリーンショットツールを使ってキャプチャ
   */
  async captureScreenshot(filename?: string): Promise<string> {
    const timestamp = Date.now();
    const outputFilename = filename || `capture-${timestamp}.png`;
    const outputPath = path.join(this.captureDir, outputFilename);

    await fs.mkdir(this.captureDir, { recursive: true });

    try {
      switch (this.platform) {
        case 'darwin': // macOS
          await execAsync(`screencapture -x "${outputPath}"`);
          break;

        case 'linux':
          // scrotを試す、失敗したらimportを試す
          try {
            await execAsync(`scrot "${outputPath}"`);
          } catch {
            await execAsync(`import -window root "${outputPath}"`);
          }
          break;

        case 'win32': // Windows
          const psScript = `
            Add-Type -AssemblyName System.Windows.Forms
            $screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Left, $screen.Top, 0, 0, $bitmap.Size)
            $bitmap.Save("${outputPath}")
          `;
          await execAsync(
            `powershell -Command "${psScript.replace(/\n/g, '; ')}"`
          );
          break;

        default:
          throw new Error(`サポートされていないプラットフォーム: ${this.platform}`);
      }

      console.log(`📸 スクリーンショット保存: ${outputPath}`);
      return outputPath;
    } catch (error) {
      console.error('❌ スクリーンショット撮影エラー:', error);
      throw error;
    }
  }
}

/**
 * キャプチャマネージャー（OBSとシステムキャプチャの統合）
 */
export class CaptureManager {
  private obsCapture?: OBSCapture;
  private systemCapture: SystemCapture;
  private useOBS: boolean;

  constructor(captureDir: string, useOBS: boolean = true) {
    this.systemCapture = new SystemCapture(captureDir);
    this.useOBS = useOBS;

    if (useOBS) {
      this.obsCapture = new OBSCapture(captureDir);
    }
  }

  /**
   * 初期化（OBSに接続を試みる）
   */
  async initialize(
    obsUrl?: string,
    obsPassword?: string
  ): Promise<void> {
    if (this.useOBS && this.obsCapture) {
      try {
        await this.obsCapture.connect(obsUrl, obsPassword);
      } catch (error) {
        console.warn(
          '⚠️ OBS接続に失敗しました。システムキャプチャを使用します。'
        );
        this.useOBS = false;
      }
    }
  }

  /**
   * スクリーンショットを撮影（OBSまたはシステム）
   */
  async capture(filename?: string): Promise<string> {
    if (this.useOBS && this.obsCapture) {
      return await this.obsCapture.captureScreenshot(filename);
    } else {
      return await this.systemCapture.captureScreenshot(filename);
    }
  }

  /**
   * クリーンアップ
   */
  async cleanup(): Promise<void> {
    if (this.obsCapture) {
      await this.obsCapture.disconnect();
    }
  }
}
