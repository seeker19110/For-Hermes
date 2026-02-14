# Camera Buying Guide

Reference for choosing cameras. Main skill focus is integration, not purchasing.

## Photography Cameras

### Types
| Type | Best For | Budget Entry |
|------|----------|--------------|
| Mirrorless | Most users, lighter | €500-800 |
| DSLR | Mature ecosystems | €400-600 used |
| Compact | Travel, convenience | €300-500 |

### Brands for Agent Control
| Brand | gPhoto2 Support | SDK Available |
|-------|-----------------|---------------|
| Canon | Excellent | Yes (EDSDK) |
| Nikon | Good | Yes |
| Sony | Good | Yes (Remote) |
| Fuji | Good | Partial |

## Security Cameras

### For Integration Priority
| Feature | Why It Matters |
|---------|----------------|
| RTSP support | Standard protocol, works everywhere |
| ONVIF | Discovery and unified control |
| Local storage | No cloud dependency |
| PoE | Single cable, reliable |

### Recommended for Agents
| Brand | Pros | Cons |
|-------|------|------|
| Reolink | RTSP, good value, local NVR | Some models cloud-only |
| Hikvision | Professional, ONVIF | Security concerns for some |
| Ubiquiti | Excellent local API | Expensive ecosystem |
| Eufy | No subscription | API unstable |

### Avoid for Integration
- Ring (no official API, blocks access)
- Nest (expensive API, cloud-only)
- Blink (no local access)

## Webcams

### For Agent Capture
Any USB webcam works via V4L2/AVFoundation. Higher quality:

| Model | Resolution | Notes |
|-------|------------|-------|
| Logitech C920 | 1080p | Reliable, widespread |
| Logitech Brio | 4K | Best quality |
| Elgato Facecam | 1080p | No compression |

## Security System Recommendations

### Home (DIY)
1. **Frigate** on RPi/mini PC (handles detection)
2. **Reolink cameras** (RTSP, affordable)
3. **Home Assistant** (unified control)

### Small Business
1. **UniFi Protect** (NVR + cameras)
2. Local storage, no subscriptions
3. Clean API for agent integration

## What to Check Before Buying

For agent compatibility:
- [ ] RTSP stream available?
- [ ] ONVIF support?
- [ ] Local API or cloud-only?
- [ ] Works without internet?
- [ ] Subscription required?
