# VOD AIGC 视频生成 API 集成规范
> 腾讯云 VOD AIGC 视频生成接口封装，用于 AI 快速复刻。

---

## 1. API 配置

```
Endpoint: vod.ap-guangzhou.tencentcloudapi.com
Region: ap-guangzhou
Version: 2018-07-17
```

环境变量:
```bash
VITE_VOD_SECRET_ID=xxx
VITE_VOD_SECRET_KEY=xxx
VITE_VOD_SUB_APP_ID=1500044236
```

---

## 2. 接口定义

### CreateAigcVideoTask

```json
{
    "SubAppId": 1500044236,
    "ModelName": "Kling",
    "ModelVersion": "2.1",
    "Prompt": "一只熊猫在竹林中玩耍",
    "EnhancePrompt": "Enabled",
    "FileInfos": [{
        "Type": "Url",
        "Url": "https://xxx/image.jpg"
    }],
    "LastFrameUrl": "https://xxx/last.jpg",
    "SceneType": "motion_control",
    "OutputConfig": {
        "StorageMode": "Temporary",
        "Resolution": "1080P",
        "AspectRatio": "16:9",
        "EnhanceSwitch": "Disabled"
    }
}
```

| 参数 | 必填 | 说明 |
|------|------|------|
| SubAppId | 是 | VOD 子应用 ID |
| ModelName | 是 | Hailuo/Kling/Vidu/Jimeng/Seedance/GV/OS |
| ModelVersion | 是 | 见模型表 |
| Prompt | 是 | 提示词 |
| EnhancePrompt | 否 | Enabled/Disabled |
| FileInfos | 否 | 图生视频输入图片 |
| LastFrameUrl | 否 | 尾帧图片(部分模型支持) |
| SceneType | 否 | Kling专用: motion_control |
| OutputConfig.StorageMode | 是 | Temporary/Permanent |
| OutputConfig.Resolution | 否 | 720P/1080P/2K/4K |
| OutputConfig.AspectRatio | 否 | 16:9/9:16/1:1 |

响应:
```json
{
    "Response": {
        "TaskId": "xxx",
        "RequestId": "xxx"
    }
}
```

### DescribeTaskDetail

```json
{
    "TaskId": "xxx",
    "SubAppId": 1500044236
}
```

响应:
```json
{
    "Response": {
        "AigcVideoTask": {
            "Status": "FINISH",
            "Progress": 100,
            "ErrCode": 0,
            "Output": {
                "FileInfos": [{
                    "FileUrl": "https://xxx.mp4",
                    "MetaData": {
                        "Duration": 5,
                        "Width": 1920,
                        "Height": 1080,
                        "CoverUrl": "https://xxx.jpg"
                    }
                }]
            }
        }
    }
}
```

状态: `PROCESSING` | `FINISH` | `FAIL`

---

## 3. 模型列表

| ModelName | ModelVersion | T2V | I2V | 最大图片 | 首尾帧 | 分辨率 |
|-----------|--------------|-----|-----|----------|--------|--------|
| Hailuo    | 02           | ✓   | ✓   | 1        | ✗      | 720P,1080P |
| Hailuo    | 2.3          | ✓   | ✓   | 1        | ✗      | 720P,1080P |
| Hailuo    | 2.3-fast     | ✗   | ✓   | 1        | ✗      | 720P,1080P |
| Kling     | 1.6          | ✓   | ✓   | 1        | ✗      | 720P,1080P |
| Kling     | 2.0          | ✓   | ✓   | 1        | ✗      | 720P,1080P,2K |
| Kling     | 2.1          | ✓   | ✓   | 1        | ✓*     | 720P,1080P,2K |
| Kling     | 2.5          | ✓   | ✓   | 1        | ✗      | 720P,1080P,2K,4K |
| Kling     | o1           | ✓   | ✓   | 1        | ✗      | 720P,1080P,2K,4K |
| Kling     | 2.6          | ✓   | ✓   | 1        | ✗      | 720P,1080P,2K,4K |
| Vidu      | q2           | ✓   | ✓   | 7        | ✗      | 720P,1080P |
| Vidu      | q2-turbo     | ✓   | ✓   | 7        | ✓      | 720P,1080P |
| Vidu      | q2-pro       | ✓   | ✓   | 7        | ✓      | 720P,1080P,2K |
| Jimeng    | 3.0pro       | ✓   | ✓   | 1        | ✗      | 720P,1080P,2K |
| Seedance  | 1.0-pro      | ✓   | ✓   | 1        | ✗      | 720P,1080P |
| Seedance  | 1.0-lite-i2v | ✗   | ✓   | 1        | ✗      | 720P,1080P |
| Seedance  | 1.0-pro-fast | ✓   | ✓   | 1        | ✗      | 720P,1080P |
| Seedance  | 1.5-pro      | ✓   | ✓   | 1        | ✗      | 720P,1080P,2K |
| GV        | 3.1          | ✓   | ✓   | 3        | ✓**    | 720P,1080P |
| GV        | 3.1-fast     | ✓   | ✓   | 3        | ✓**    | 720P,1080P |
| OS        | 2.0          | ✓   | ✗   | 0        | ✗      | 720P,1080P |

> *Kling 2.1 首尾帧仅1080P
> **GV多图时不可用首尾帧

---

## 4. TC3 签名

(See original message for implementation details)

---

## 9. 错误码

| Code | 说明 |
|------|------|
| AuthFailure | 密钥错误 |
| InvalidParameter | 参数错误 |
| LimitExceeded | 限流 |
| ContentRiskDetected | 内容审核 |
| InternalError | 内部错误 |

---
## 参考
- https://cloud.tencent.com/document/product/266/126239
- https://cloud.tencent.com/document/product/266/33431
