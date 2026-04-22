param (
    [Parameter(Mandatory=$true)]
    [string]$prompt,
    [string]$image_url = "",
    [string]$aspect_ratio = "16:9",
    [string]$negative_prompt = ""
)

$ApiKey = "sk-sOAXf4nlZLtXoiW3Cr2RzrkC9vZ6ZQIoF7MO7qJ4TLAchd8d"
$BaseUrl = "https://api.bltcy.ai"
$Endpoint = "$BaseUrl/v2/videos/generations"
$Model = "veo3.1-fast"

$headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type"  = "application/json"
}

$body = @{
    "model"          = $Model
    "prompt"         = $prompt
    "aspect_ratio"   = $aspect_ratio
}

if ($image_url -ne "") {
    $body["image_url"] = $image_url
}

if ($negative_prompt -ne "") {
    $body["negative_prompt"] = $negative_prompt
}

$jsonBody = $body | ConvertTo-Json

Write-Host "Submitting video generation task to $Endpoint..."
try {
    $response = Invoke-RestMethod -Uri $Endpoint -Method Post -Headers $headers -Body $jsonBody
    $taskId = $response.id
    if (-not $taskId) {
        $taskId = $response.task_id
    }
} catch {
    Write-Error "Failed to submit task: $_"
    exit 1
}

if (-not $taskId) {
    Write-Error "No task ID received from API."
    Write-Host "Response: $response"
    exit 1
}

Write-Host "Task ID: $taskId"
Write-Host "Waiting for video generation..."

$statusUrl = "$BaseUrl/v2/videos/generations/$taskId"
$maxRetries = 60 # 10 minutes max (10s interval)
$retryCount = 0
$videoUrl = $null

while ($retryCount -lt $maxRetries) {
    Start-Sleep -Seconds 10
    $retryCount++
    
    try {
        $statusResponse = Invoke-RestMethod -Uri $statusUrl -Method Get -Headers $headers
        $status = $statusResponse.status
        Write-Host "Status: $status (Attempt $retryCount/$maxRetries)"
        
        if ($status -eq "SUCCESS" -or $status -eq "COMPLETED" -or $status -eq "completed") {
            # Check for video URL in common fields
            if ($statusResponse.data -and $statusResponse.data.output) {
                $videoUrl = $statusResponse.data.output
            } elseif ($statusResponse.video -and $statusResponse.video.url) {
                $videoUrl = $statusResponse.video.url
            } elseif ($statusResponse.result -and $statusResponse.result.video_url) {
                $videoUrl = $statusResponse.result.video_url
            } elseif ($statusResponse.video_url) {
                $videoUrl = $statusResponse.video_url
            }
            
            if ($videoUrl) {
                Write-Host "Video generation SUCCESS!"
                Write-Host "URL: $videoUrl"
                break
            }
        } elseif ($status -eq "FAILED" -or $status -eq "failed" -or $status -eq "error") {
            Write-Error "Video generation failed: $($statusResponse.error)"
            exit 1
        }
    } catch {
        Write-Warning "Status check failed: $_. Retrying..."
    }
}

if (-not $videoUrl) {
    Write-Error "Timed out waiting for video or could not find URL."
    exit 1
}

# Output the final result in a way that the agent can read
$output = @{
    "taskId" = $taskId
    "videoUrl" = $videoUrl
    "status" = "success"
} | ConvertTo-Json
Write-Output $output
