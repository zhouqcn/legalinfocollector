# LegalInfoCollector (简化版)

从网页提取法律文档信息并存储到本地数据库的命令行应用程序。

## 功能特性

- ✅ 网页文本内容提取
- ✅ 本地SQLite数据库存储
- ✅ 命令行界面操作
- ✅ 支持内容预览

## 技术栈

- **语言**: Python 2.7+ / 3.x 兼容
- **数据库**: SQLite
- **依赖**: 仅标准库 (无需额外安装)

## 运行方法

```bash
# Python 2.7
python simple_app.py

# Python 3.x  
python3 simple_app.py
```

## 使用说明

1. 运行程序
2. 输入要提取的法律文档URL (以 http:// 或 https:// 开头)
3. 输入 'list' 查看已保存的文档列表
4. 输入 'quit' 退出程序

## 示例

```
请输入URL或命令: https://example-legal-site.com/document
正在提取: https://example-legal-site.com/document
✅ 提取成功!
标题: 示例法律文档
来源: example-legal-site.com
内容预览: 这是一份示例法律文档的内容摘要...

请输入URL或命令: list

=== 已保存的法律文档 ===
ID: 1
URL: https://example-legal-site.com/document
标题: 示例法律文档
来源: example-legal-site.com
提取时间: 2024-01-01 12:00:00
--------------------------------------------------
```

## 注意事项

- 支持大部分文本类网站
- 内容自动清理和截断
- 数据库文件 (legal_data.db) 自动创建
- 无需网络依赖，使用Python标准库