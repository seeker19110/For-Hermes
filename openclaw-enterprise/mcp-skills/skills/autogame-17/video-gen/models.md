# Video Generation Models (Best Practices)

When generating videos using the `video-gen` skill, choosing the right model is critical for optimal results.

## Model Selection Guide

| Model Name | Best For | Typical Use Cases |
| :--- | :--- | :--- |
| **kling-v2.5** (Default) | **High Fidelity & Motion** | Cinematic shots, complex motion, realistic textures. Best general-purpose choice. |
| **vidu** | **Consistency** | Use when Reference Image consistency is prioritized over complex motion. Good for character consistency. |
| **minimax** | **Stylized/Artistic** | Better for abstract, stylized, or specific artistic interpretations. |
| **hailuo** | **Fast Prototyping** | Generally faster generation times, good for quick iterations. |

## Parameters

The `skills/video-gen/index.js` script supports the following CLI arguments:

-   **Prompt** (Positional): The text description of the video.
    -   *Example*: `"A cybernetic city with neon rain"`
-   `--model`: Specify the AI model.
    -   *Default*: `kling-v2.5`
    -   *Options*: `kling-v2.5`, `vidu`, `minimax`, `hailuo` (subject to availability)
-   `--resolution`: Output resolution.
    -   *Default*: `1080p`
    -   *Options*: `1080p`, `720p`

## Tips for Better Prompts

1.  **Be Specific**: Instead of "a car", say "a red vintage sports car drifting on a wet asphalt track".
2.  **Lighting**: Mention lighting (e.g., "cinematic lighting", "sunset", "neon lights").
3.  **Motion**: Describe the movement (e.g., "camera pans right", "slow motion", "zoom in").
