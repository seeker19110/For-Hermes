import sharp from 'sharp';
import fs from 'fs/promises';

/**
 * ページめくり検知クラス
 *
 * 画像の差分を計算して、ページが変わったかを判定します。
 * Factor 8: Own your control flow - ページ変更検知のロジックを制御
 */
export class PageDetector {
  private previousImageHash: string | null = null;
  private similarityThreshold: number;
  private changeThreshold: number;

  constructor(
    similarityThreshold: number = 0.85,
    changeThreshold: number = 0.15
  ) {
    this.similarityThreshold = similarityThreshold;
    this.changeThreshold = changeThreshold;
  }

  /**
   * 画像のハッシュを計算（perceptual hash）
   */
  private async calculateImageHash(imagePath: string): Promise<string> {
    try {
      // 画像を小さくリサイズして比較用のハッシュを作成
      const resized = await sharp(imagePath)
        .resize(32, 32, { fit: 'fill' })
        .grayscale()
        .raw()
        .toBuffer();

      // 簡易的なハッシュ（実際のperceptual hashはもっと複雑）
      let hash = '';
      const pixels = new Uint8Array(resized);
      const avg = pixels.reduce((a, b) => a + b, 0) / pixels.length;

      for (let i = 0; i < pixels.length; i++) {
        hash += pixels[i] > avg ? '1' : '0';
      }

      return hash;
    } catch (error) {
      console.error('画像ハッシュ計算エラー:', error);
      throw error;
    }
  }

  /**
   * ハミング距離を計算（2つのハッシュ間の違い）
   */
  private hammingDistance(hash1: string, hash2: string): number {
    if (hash1.length !== hash2.length) {
      throw new Error('ハッシュの長さが一致しません');
    }

    let distance = 0;
    for (let i = 0; i < hash1.length; i++) {
      if (hash1[i] !== hash2[i]) {
        distance++;
      }
    }

    return distance;
  }

  /**
   * 2つの画像の類似度を計算（0-1、1が完全一致）
   */
  async calculateSimilarity(
    imagePath1: string,
    imagePath2: string
  ): Promise<number> {
    const hash1 = await this.calculateImageHash(imagePath1);
    const hash2 = await this.calculateImageHash(imagePath2);

    const distance = this.hammingDistance(hash1, hash2);
    const maxDistance = hash1.length;
    const similarity = 1 - distance / maxDistance;

    return similarity;
  }

  /**
   * 新しい画像がページめくりを示すかを判定
   *
   * @returns true: ページが変わった, false: 同じページ
   */
  async detectPageChange(imagePath: string): Promise<boolean> {
    const currentHash = await this.calculateImageHash(imagePath);

    // 初回の画像
    if (this.previousImageHash === null) {
      this.previousImageHash = currentHash;
      return true; // 最初のページとして扱う
    }

    // ハミング距離を計算
    const distance = this.hammingDistance(
      this.previousImageHash,
      currentHash
    );
    const maxDistance = currentHash.length;
    const similarity = 1 - distance / maxDistance;

    console.log(
      `📊 画像類似度: ${(similarity * 100).toFixed(2)}% (閾値: ${(this.similarityThreshold * 100).toFixed(2)}%)`
    );

    // 類似度が閾値以下ならページが変わったと判定
    const isPageChanged = similarity < this.similarityThreshold;

    if (isPageChanged) {
      console.log('✅ ページめくりを検知しました！');
      this.previousImageHash = currentHash;
    } else {
      console.log('⏸️  同じページです（スキップ）');
    }

    return isPageChanged;
  }

  /**
   * より高度な差分検出（エッジ検出ベース）
   */
  async detectPageChangeAdvanced(imagePath: string): Promise<boolean> {
    try {
      // エッジ検出で輪郭を抽出
      const edges = await sharp(imagePath)
        .resize(256, 256)
        .grayscale()
        .convolve({
          width: 3,
          height: 3,
          kernel: [-1, -1, -1, -1, 8, -1, -1, -1, -1], // Laplacian filter
        })
        .raw()
        .toBuffer();

      // エッジの特徴量を計算
      const edgeHash = this.calculateBufferHash(edges);

      if (this.previousImageHash === null) {
        this.previousImageHash = edgeHash;
        return true;
      }

      const distance = this.hammingDistance(this.previousImageHash, edgeHash);
      const similarity = 1 - distance / edgeHash.length;

      console.log(
        `📊 エッジベース類似度: ${(similarity * 100).toFixed(2)}%`
      );

      const isPageChanged = similarity < this.similarityThreshold;

      if (isPageChanged) {
        this.previousImageHash = edgeHash;
      }

      return isPageChanged;
    } catch (error) {
      console.error('高度な差分検出エラー:', error);
      // フォールバック: 基本的な検出を使用
      return this.detectPageChange(imagePath);
    }
  }

  /**
   * バッファからハッシュを計算
   */
  private calculateBufferHash(buffer: Buffer): string {
    const pixels = new Uint8Array(buffer);
    const avg = pixels.reduce((a, b) => a + b, 0) / pixels.length;

    let hash = '';
    for (let i = 0; i < pixels.length; i++) {
      hash += pixels[i] > avg ? '1' : '0';
    }

    return hash;
  }

  /**
   * 検出器をリセット
   */
  reset(): void {
    this.previousImageHash = null;
    console.log('🔄 ページ検出器をリセットしました');
  }
}

/**
 * モーション検出ベースのページめくり検知（オプション）
 *
 * より正確だが処理が重い方式
 */
export class MotionBasedPageDetector {
  private previousImage: Buffer | null = null;
  private motionThreshold: number;

  constructor(motionThreshold: number = 0.2) {
    this.motionThreshold = motionThreshold;
  }

  /**
   * フレーム間の差分を計算
   */
  async detectMotion(imagePath: string): Promise<number> {
    const currentImage = await sharp(imagePath)
      .resize(640, 480)
      .grayscale()
      .raw()
      .toBuffer();

    if (this.previousImage === null) {
      this.previousImage = currentImage;
      return 1.0; // 初回は動きありとする
    }

    // ピクセルごとの差分を計算
    let totalDiff = 0;
    for (let i = 0; i < currentImage.length; i++) {
      totalDiff += Math.abs(currentImage[i] - this.previousImage[i]);
    }

    const avgDiff = totalDiff / currentImage.length / 255; // 0-1に正規化

    this.previousImage = currentImage;

    return avgDiff;
  }

  /**
   * モーションがページめくりかを判定
   */
  async detectPageChange(imagePath: string): Promise<boolean> {
    const motion = await this.detectMotion(imagePath);

    console.log(
      `🎬 モーション検出: ${(motion * 100).toFixed(2)}% (閾値: ${(this.motionThreshold * 100).toFixed(2)}%)`
    );

    return motion > this.motionThreshold;
  }

  reset(): void {
    this.previousImage = null;
  }
}
