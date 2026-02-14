# 新建子区流程

## 步骤

### 1. 确定位置
选择对应的频道（根据项目/领域）

### 2. 创建子区
```
message action=thread-create \
  channel=discord \
  channelId=<频道ID> \
  threadName="[类型] 简短描述"
```

### 3. 发送置顶摘要
使用 `templates/pinned-summary.md` 模板

### 4. 置顶消息
```
message action=pin \
  channel=discord \
  channelId=<子区ID> \
  messageId=<摘要消息ID>
```

### 5. 更新频道简介（可选）
如果是重要子区，在频道简介的「活跃子区」部分添加

## 命名规范

```
[类型] 简短描述
```

类型：`[讨论]` `[任务]` `[Bug]` `[PR]` `[文章]` `[调研]`

## 示例

```bash
# 创建文章讨论子区
message action=thread-create \
  channel=discord \
  channelId=<your-channel-id> \
  threadName="[文章] Skill 生态的演进之路"
```
