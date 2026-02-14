#!/bin/bash
# 远程发布文章到微信公众号
# 基于 wenyan-mcp HTTP Stateless 模式

# 读取文章路径
FILE_PATH="$1"
THEME_ID="${2:-default}"

if [ -z "$FILE_PATH" ]; then
  echo "Usage: ./publish-remote.sh <path/to/article.md> [theme_id]"
  echo "Example: ./publish-remote.sh ./my-post.md lapis"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File '$FILE_PATH' not found."
  exit 1
fi

# 检查环境变量
if [ -z "$WECHAT_APP_ID" ] || [ -z "$WECHAT_APP_SECRET" ]; then
  echo "Error: WECHAT_APP_ID or WECHAT_APP_SECRET not set."
  echo "Please set them in your environment or TOOLS.md."
  exit 1
fi

# 上传文件
echo "🚀 Uploading file to wenyan-mcp..."
FILENAME=$(basename "$FILE_PATH")
CONTENT=$(cat "$FILE_PATH")

# 构造 upload_file 的 args JSON (这里是关键：mcporter 必须正确构造 JSON 字符串)
# 使用 jq 确保 JSON 转义正确
UPLOAD_ARGS=$(jq -n --arg content "$CONTENT" --arg filename "$FILENAME" '{content: $content, filename: $filename}')

UPLOAD_RES=$(mcporter call wenyan-mcp.upload_file --config /root/.openclaw/mcp.json --args "$UPLOAD_ARGS")

# 解析 upload 结果
FILE_ID=$(echo "$UPLOAD_RES" | jq -r '.file_id // empty')
ERROR_MSG=$(echo "$UPLOAD_RES" | jq -r '.error // empty')

if [ -n "$ERROR_MSG" ]; then
  echo "❌ Upload failed: $ERROR_MSG"
  exit 1
fi

if [ -z "$FILE_ID" ] || [ "$FILE_ID" == "null" ]; then
  echo "❌ Upload failed: Could not parse file_id from response."
  echo "Response: $UPLOAD_RES"
  exit 1
fi

echo "✅ File uploaded! ID: $FILE_ID"
echo "⏳ Publishing to WeChat draft box..."

# 构造 publish_article 的 args JSON
PUBLISH_ARGS=$(jq -n \
  --arg file_id "$FILE_ID" \
  --arg theme_id "$THEME_ID" \
  --arg app_id "$WECHAT_APP_ID" \
  --arg app_secret "$WECHAT_APP_SECRET" \
  '{file_id: $file_id, theme_id: $theme_id, wechat_app_id: $app_id, wechat_app_secret: $app_secret}')

PUBLISH_RES=$(mcporter call wenyan-mcp.publish_article --config /root/.openclaw/mcp.json --args "$PUBLISH_ARGS")

# 解析 publish 结果
MEDIA_ID=$(echo "$PUBLISH_RES" | jq -r '.media_id // empty')
PUBLISH_ERR=$(echo "$PUBLISH_RES" | jq -r '.error // empty')

if [ -n "$PUBLISH_ERR" ]; then
  echo "❌ Publish failed: $PUBLISH_ERR"
  echo "Tip: Check if remote server IP is whitelisted in WeChat MP backend."
  exit 1
fi

if [ -z "$MEDIA_ID" ] || [ "$MEDIA_ID" == "null" ]; then
  echo "❌ Publish failed: Unknown response."
  echo "Response: $PUBLISH_RES"
  exit 1
fi

echo "🎉 Success! Media ID: $MEDIA_ID"
echo "Please check your WeChat Official Account draft box."
