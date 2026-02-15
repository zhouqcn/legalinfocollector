# LegalInfoCollector

从网页提取法律文档信息并存储到本地数据库的应用程序。

## 功能特性

- ✅ 网页文本内容提取
- ✅ 本地SQLite数据库存储
- ✅ Web界面操作
- ✅ 支持批量URL处理
- ✅ 内容预览和搜索

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML/CSS/JavaScript
- **数据库**: SQLite
- **网页解析**: BeautifulSoup4 + lxml
- **网络请求**: requests

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python run.py
```

3. 打开浏览器访问：`http://localhost:5000`

## 使用说明

1. 在网页输入框中输入要提取的法律文档URL
2. 点击"提取内容"按钮
3. 系统会自动提取网页正文内容并保存到数据库
4. 可以在下方查看已保存的文档列表

## API接口

- `POST /extract` - 提取网页内容
- `GET /documents` - 获取文档列表
- `GET /document/<id>` - 获取特定文档详情

## 项目结构

```
legalinfocollector/
├── app.py              # 主应用文件
├── run.py              # 启动脚本
├── config.py           # 配置文件
├── requirements.txt    # 依赖文件
├── legal_data.db       # 数据库文件（自动创建）
└── templates/
    └── index.html      # 前端页面
```

## 注意事项

- 请确保目标网站允许爬取内容
- 支持大部分新闻、博客、文档类网站
- 内容提取长度限制为10000字符
- 数据库文件会自动在当前目录创建