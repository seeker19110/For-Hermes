# 重组频道流程

## 场景

- 合并多个频道
- 调整分类结构
- 迁移频道到新分类

## 合并频道

### 1. 在目标频道创建子区
为原频道的内容创建对应子区

### 2. 创建索引摘要
在新子区置顶消息中链接原频道重要消息

### 3. 移动原频道到归档
```
message action=channel-move \
  channel=discord \
  channelId=<原频道ID> \
  parentId=<归档分类ID>
```

### 4. 重命名原频道（可选）
加前缀表示已归档：
```
[归档] 原频道名
```

## 移动频道到新分类

```
message action=channel-move \
  channel=discord \
  channelId=<频道ID> \
  parentId=<目标分类ID>
```

## 创建新分类

```
message action=category-create \
  channel=discord \
  guildId=<your-guild-id> \
  name="emoji 分类名称"
```

## 注意事项

- 移动前确认频道内重要消息已记录
- 子区会跟随频道一起移动
- 归档分类 ID：（填入你的归档分类 ID）
