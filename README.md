# 法律AI - 智能法律顾问系统

## 功能特性

- 📖 **法条搜索**: 支持模糊搜索刑法、民法典法条，含司法解释和判例
- 📤 **文档分析**: 上传合同/法律文件，AI自动识别风险并评分
- 🔄 **文档对比**: 两份文档对比，显示修改差异
- 💬 **智能问答**: AI法律顾问，解答法律问题
- 📋 **合同模板**: 常用合同模板库，一键使用

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy (异步)
- ChromaDB (向量搜索)
- MiMo API (AI分析)

### 前端
- HTML5
- CSS3 (暗色主题)
- 原生JavaScript

## 快速开始

### 推荐方式：使用项目虚拟环境

本项目已配置项目级虚拟环境，建议所有 Python 相关操作都通过 `.venv` 执行，避免与全局 Python 包发生版本冲突。

### 1. 创建并安装后端依赖

在项目根目录执行：

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt "numpy<2"
```

如果你的 `.venv` 已经存在，可以跳过创建步骤，只执行安装命令。

### 2. 配置环境变量

编辑 `backend/.env` 文件，填入你的 MiMo API Key：

```
MIMO_API_KEY=your_api_key_here
```

### 3. 启动后端服务

推荐在项目根目录执行：

```bash
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

或者进入 `backend` 目录后执行：

```bash
..\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 使用启动脚本

也可以直接在项目根目录运行：

```bash
start.bat
```

当前 `start.bat` 已默认使用项目虚拟环境 `.venv` 启动后端。

### 5. 打开应用

启动后请在浏览器访问：`http://127.0.0.1:8000/`。

请不要直接双击打开 `frontend/index.html`，因为当前前端依赖后端 API，由 FastAPI 统一提供页面和接口。

### 6. 可选：启用商业级图片 OCR

当前图片 OCR 采用“双引擎”方案：

- 主引擎：`PaddleOCR`（更适合中文合同、扫描件、中英混排）
- 回退引擎：`Tesseract OCR`
- 默认 CPU 可运行，可通过环境变量切换未来 GPU 模式

#### 安装建议

推荐直接安装后端依赖：

```bash
.\\.venv\\Scripts\\python -m pip install -r backend\\requirements.txt "numpy<2"
```

#### Windows

- 建议额外安装 `Tesseract OCR`
- 如未自动识别安装路径，可配置 `TESSERACT_CMD`
- 常见安装路径：`C:\\Program Files\\Tesseract-OCR\\tesseract.exe`

#### Docker / Linux

- 需要准备 Paddle 运行时依赖
- 若要保留回退能力，请确保镜像内可执行 `tesseract`
- CPU 镜像默认保持 `OCR_ENABLE_GPU=false`

#### 推荐环境变量

```bash
OCR_PRIMARY_ENGINE=paddle
OCR_FALLBACK_ENGINE=tesseract
OCR_ENABLE_GPU=false
OCR_LANG=ch
OCR_PADDLE_USE_ANGLE_CLS=true
OCR_PADDLE_DET_LIMIT_SIDE_LEN=1920
TESSERACT_LANG=chi_sim+eng
TESSERACT_CONFIG=--oem 1 --psm 4
```

更完整的部署说明见 `backend/OCR_DEPLOYMENT.md`。

#### 未安装完整依赖时的影响

- `txt`、`docx`、`pdf` 文档分析仍可使用
- 图片类文件（`jpg`、`jpeg`、`png`）会优先尝试 PaddleOCR
- Paddle 不可用时会自动回退到 Tesseract
- 两者都不可用时，系统会返回明确错误信息

## 项目结构

```
legal-ai/
├── backend/
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── search.py   # 法条搜索
│   │   │   ├── document.py # 文档分析
│   │   │   ├── chat.py     # AI问答
│   │   │   └── user.py     # 用户管理
│   │   ├── core/           # 核心功能
│   │   │   ├── legal_db.py       # 法条数据库
│   │   │   ├── vector_store.py   # 向量搜索
│   │   │   ├── document_parser.py # 文档解析
│   │   │   ├── document_service.py # OCR装配入口
│   │   │   ├── ocr.py            # OCR公共导出
│   │   │   ├── ocr_base.py       # OCR引擎接口
│   │   │   ├── ocr_paddle.py     # PaddleOCR主引擎
│   │   │   ├── ocr_tesseract.py  # Tesseract回退引擎
│   │   │   ├── ocr_router.py     # 主备路由
│   │   │   ├── ocr_quality.py    # 质量门槛检查
│   │   │   └── ai_analyzer.py    # AI分析器
│   │   ├── models/         # 数据模型
│   │   │   ├── schemas.py  # Pydantic模型
│   │   │   └── database.py # 数据库模型
│   │   ├── config.py       # 配置文件
│   │   └── main.py         # 应用入口
│   ├── data/               # 法条数据
│   │   ├── criminal_law.json
│   │   └── civil_law.json
│   ├── uploads/            # 上传文件目录
│   ├── OCR_DEPLOYMENT.md   # OCR部署说明
│   └── requirements.txt
├── frontend/
│   ├── css/
│   │   └── style.css       # 样式文件
│   ├── js/
│   │   └── app.js          # 前端逻辑
│   └── index.html          # 主页面
├── .venv/
├── start.bat
└── README.md
```

## API 接口

### 法条搜索
- `GET /api/search/law?q={keyword}` - 搜索法条
- `GET /api/search/law/{article_id}` - 获取法条详情

### 文档分析
- `POST /api/document/analyze` - 上传并分析文档
- `POST /api/document/compare` - 对比两份文档
- `GET /api/document/analysis/{id}` - 获取分析结果

### AI问答
- `POST /api/chat/sessions` - 创建会话
- `GET /api/chat/sessions` - 获取会话列表
- `POST /api/chat/sessions/{id}/messages` - 发送消息

### 用户
- `POST /api/user/login` - 用户登录
- `POST /api/user/favorites` - 添加收藏
- `GET /api/user/favorites/{user_id}` - 获取收藏列表

## 注意事项

1. 首次运行会自动创建数据库
2. 法条数据在 `data/` 目录下，可自行扩充
3. MiMo API Key 需要自行申请
4. 上传文件大小限制为 10MB
5. 建议不要使用全局 Python 直接启动后端，优先使用 `.venv`
