# 三角洲今日密码查询插件

一个用于查询《三角洲行动》游戏每日密码的 NekroAgent 插件。

## 功能特点

- 查询《三角洲行动》游戏的今日密码

## 配置说明

插件支持以下配置项（可选）：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| API_URL | str | `https://www.tmini.net/api/sjzmm?ckey=&type=` | 三角洲今日密码API地址 |
| TIMEOUT | int | `10` | API请求超时时间(秒) |

## 使用方法

### 在 NekroAgent 中使用

插件提供了一个"get_delta_password()"的沙盒方法，可以通过以下方式手动调用：

```python
/exec get_delta_password()
```

## 注意事项

1. **网络要求**：插件需要访问外部 API，请确保网络连接正常
2. **API 限制**：请遵守 API 提供方的使用条款，不要频繁请求
3. **数据准确性**：密码信息由第三方 API 提供，准确性以游戏实际情况为准
4. **错误处理**：如遇网络问题或 API 服务异常，插件会返回友好的错误提示

## 更新日志

### v1.0.0 (2025-10-27)
-  初始版本发布
-  实现基础密码查询功能

## 技术支持

如遇到问题，请：
1. 检查网络连接是否正常
2. 确认 API 服务是否可用
3. 查看 NekroAgent 日志获取详细错误信息

## 许可证

本项目基于 MIT 许可证开源。
---

**tooplick** - GitHub: [@tooplick](https://github.com/tooplick)

项目链接: [https://github.com/tooplick/nekro_delta_password](https://github.com/tooplick/nekro_delta_password)
Nekro Agent 文档: [https://doc.nekro.ai/](https://doc.nekro.ai/)