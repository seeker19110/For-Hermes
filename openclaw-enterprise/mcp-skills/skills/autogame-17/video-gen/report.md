✅ **Video Generation Integrated**

The system is now capable of generating AI videos using Tencent Cloud VOD.

**Supported Models:**
*   **Kling 2.5** (Default): Best for high fidelity and complex motion.
*   **Vidu**: Good for reference consistency.
*   **Hailuo**: Faster generation.

**Usage:**
```bash
node skills/video-gen/index.js "A cybernetic city" --model=kling-v2.5
```
**Output:**
Returns `MEDIA_URL` and `COVER_URL` for downstream use.
