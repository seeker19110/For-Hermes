---
name: Cameras
description: Connect to security cameras, capture snapshots, control photography gear, and process video feeds with protocol support and smart home integration.
---

## Decision Tree

| Task | Reference |
|------|-----------|
| Connect to security cameras (Ring, Nest, IP cams) | Check `security-integration.md` |
| Capture from webcams or USB cameras | Check `capture.md` |
| Control DSLR/mirrorless (tethering, remote shoot) | Check `photography-control.md` |
| Process video (detection, recognition) | Check `processing.md` |
| Choose or compare cameras (buying guide) | Check `buying-guide.md` |

---

## Core Capabilities

**What an agent with this skill can do:**

1. **Capture snapshots** from any connected camera on demand
2. **Record short clips** (10-60s) for review or sending
3. **List available cameras** on the system or network
4. **Receive motion alerts** from security systems
5. **Control photography cameras** (shoot, adjust settings, download)
6. **Describe what the camera sees** (using vision models)

---

## Protocol Quick Reference

| Protocol | Use Case | Access Method |
|----------|----------|---------------|
| **RTSP** | IP cameras, NVRs | `rtsp://user:pass@ip:554/stream` |
| **ONVIF** | Discovery + control | `python-onvif-zeep`, auto-discover |
| **HTTP/MJPEG** | Simple IP cams | `/snapshot.jpg`, `/video.mjpg` |
| **Home Assistant** | Unified access | REST API `/api/camera_proxy/` |
| **Frigate** | Motion events + clips | MQTT + HTTP API |
| **USB/V4L2** | Webcams, capture cards | `ffmpeg`, `opencv`, device index |
| **gPhoto2** | DSLR/mirrorless control | USB PTP protocol |

---

## Common Commands

```
# List cameras
ffmpeg -list_devices true -f avfoundation -i dummy  # macOS
v4l2-ctl --list-devices                              # Linux

# Snapshot from RTSP
ffmpeg -i "rtsp://user:pass@ip/stream" -frames:v 1 snapshot.jpg

# Snapshot from webcam
ffmpeg -f avfoundation -i "0" -frames:v 1 webcam.jpg  # macOS
ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 webcam.jpg  # Linux

# Record 10s clip
ffmpeg -i "rtsp://ip/stream" -t 10 -c copy clip.mp4
```

---

## Integration Patterns

### With Home Assistant
If cameras are already in HA, use the REST API:
```
GET /api/camera_proxy/camera.front_door
→ Returns JPEG snapshot
```

### With Frigate (recommended for security)
Frigate handles detection. Agent just listens:
- MQTT: `frigate/events` for motion alerts
- HTTP: `/api/events/{id}/snapshot.jpg`

### With Vision Models
Capture snapshot → send to vision model for description:
```
1. ffmpeg → snapshot.jpg
2. Vision API → "A person standing at the front door"
3. Return description to user
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera offline | Check network, power, IP hasn't changed |
| RTSP timeout | Try adding `?tcp` or use port 8554 |
| Permission denied | Run with sudo or add user to video group |
| No video, only audio | Wrong stream path, try /stream1, /ch01/main |
| gPhoto2 camera busy | Close other apps using camera, replug USB |
