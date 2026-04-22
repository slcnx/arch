import requests
import json
import time
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate videos using various models via bltcy.ai proxy.")
    parser.add_argument("--prompt", required=True, help="Description of the video to generate")
    parser.add_argument("--image_url", default="", help="Optional start frame image URL")
    parser.add_argument("--start_image_url", default="", help="Optional start frame image URL")
    parser.add_argument("--end_image_url", default="", help="Optional end frame image URL")
    parser.add_argument("--aspect_ratio", default="16:9", help="Aspect ratio (e.g., 16:9, 9:16, 1:1)")
    parser.add_argument("--negative_prompt", default="", help="Things to avoid in the video")
    parser.add_argument("--model", default="veo3.1-fast", help="Model ID (e.g., veo3.1-fast, sora-2, kling-v1)")
    
    args = parser.parse_args()

    api_key = "sk-sOAXf4nlZLtXoiW3Cr2RzrkC9vZ6ZQIoF7MO7qJ4TLAchd8d"
    base_url = "https://api.bltcy.ai"
    endpoint = f"{base_url}/v2/videos/generations"
    model = args.model

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "prompt": args.prompt,
        "aspect_ratio": args.aspect_ratio
    }

    # Handle start image
    start_image = args.start_image_url or args.image_url
    if start_image:
        payload["image_url"] = start_image
    
    # Handle end image
    if args.end_image_url:
        payload["end_image_url"] = args.end_image_url
    
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt

    print(f"Submitting video generation task to {endpoint}...")
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        resp_data = response.json()
        
        task_id = resp_data.get("id") or resp_data.get("task_id")
        if not task_id:
            print(f"Error: No task ID received. Response: {resp_data}", file=sys.stderr)
            sys.exit(1)
            
        print(f"Task ID: {task_id}")
    except Exception as e:
        print(f"Failed to submit task: {e}", file=sys.stderr)
        sys.exit(1)

    # Polling
    status_url = f"{base_url}/v2/videos/generations/{task_id}"
    max_retries = 60  # 10 minutes max (10s interval)
    video_url = None

    print("Waiting for video generation...")
    for i in range(max_retries):
        time.sleep(10)
        try:
            status_resp = requests.get(status_url, headers=headers)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            
            status = status_data.get("status", "").upper()
            print(f"Status: {status} (Attempt {i+1}/{max_retries})")

            if status in ["SUCCESS", "COMPLETED"]:
                # Try multiple possible output fields
                data = status_data.get("data", {})
                if isinstance(data, dict):
                    video_url = data.get("output")
                
                if not video_url:
                    video_url = status_data.get("video_url") or status_data.get("url")
                
                if not video_url:
                    video = status_data.get("video", {})
                    if isinstance(video, dict):
                        video_url = video.get("url")
                
                if video_url:
                    print("Video generation SUCCESS!")
                    print(f"URL: {video_url}")
                    break
            elif status in ["FAILED", "ERROR"]:
                error_msg = status_data.get("error", "Unknown error")
                print(f"Video generation failed: {error_msg}", file=sys.stderr)
                sys.exit(1)
                
        except Exception as e:
            print(f"Status check failed: {e}. Retrying...")

    if not video_url:
        print("Error: Timed out waiting for video or could not find URL.", file=sys.stderr)
        sys.exit(1)

    result = {
        "taskId": task_id,
        "videoUrl": video_url,
        "status": "success"
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
