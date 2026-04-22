---
name: veo-video-gen
description: Generate videos using Google Veo 3.1 Fast model via api.bltcy.ai proxy.
---

# Veo Video Generation Skill

This skill allows the agent to generate short videos (5-10 seconds) from a text prompt using the **veo3.1-fast** model via the `api.bltcy.ai` gateway.

## Usage

1. Call the `scripts/veo_gen.py` script with a prompt.
2. The script will:
   - Submit the generation task.
   - Wait (loop) until the video is ready.
   - Return the final video URL.

### Parameters
- `--prompt`: (Required) String. Description of the video to generate.
- `--image_url`: (Optional) String. URL of the reference image for Image-to-Video generation.
- `--start_image_url`: (Optional) String. URL of the start frame.
- `--end_image_url`: (Optional) String. URL of the end frame.
- `--aspect_ratio`: (Optional) String. Default is `16:9`. Supports `9:16`, `1:1`, etc.
- `--negative_prompt`: (Optional) String. Things to avoid in the video.
- `--model`: (Optional) String. Model ID. Default is `veo3.1-fast`. Supports `sora-2`, `kling-v1`, etc.

## Example Command
```bash
python e:\vscode_projects\arch\_agent\skills\veo-video-gen\scripts\veo_gen.py --prompt "A sunset over a calm ocean" --model "sora-2"
```

## Response Format
The script outputs a JSON object:
```json
{
  "taskId": "task_id_here",
  "videoUrl": "https://video_url_here",
  "status": "success"
}
```
