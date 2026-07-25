# 环境配置说明

## 1. 文档目的

本说明用于统一“法律 AI 项目”在开发、测试、演示/生产三类环境下的配置方式，降低环境不一致、敏感信息泄漏和启动失败风险。

## 2. 当前项目配置现状

当前项目使用 `backend/app/config.py` 通过 `python-dotenv` 加载 `.env` 文件，并集中读取以下几类配置：

- 应用基础配置
- MiMo API 配置
- 数据库配置
- ChromaDB 配置
- 上传目录配置
- OCR 配置
- 法条数据路径配置

当前做法已经具备“集中读取”的雏形，但仍存在以下问题：

- `.env.example` 不完整，未覆盖 OCR 等新增配置
- 没有明确区分开发 / 测试 / 生产环境
- 默认 `DEBUG=true`
- 默认数据库说明仍偏 SQLite 原型阶段
- 敏感配置管理规则未正式写清

## 3. 环境分层建议

本项目建议至少区分 3 类环境：

### 3.1 开发环境（dev）

适用于本地编码、联调、功能开发。

特征：
- 允许 `DEBUG=true`
- 可使用本地 SQLite 或本地 PostgreSQL
- 可使用本地上传目录
- 可直接连测试用 MiMo Key
- 可放宽部分日志输出

### 3.2 测试环境（test）

适用于接口测试、集成测试、回归测试。

特征：
- `DEBUG=false`
- 使用专用测试数据库
- 上传目录、向量库目录与开发环境隔离
- 尽可能避免调用真实线上 AI Key
- 应支持自动初始化与自动清理

### 3.3 演示 / 生产环境（prod/demo）

适用于最终交付、演示部署和验收。

特征：
- `DEBUG=false`
- 使用 PostgreSQL
- 严格管理 MiMo Key 等敏感配置
- 配置固定的上传目录与持久化目录
- CORS 只允许指定来源
- 日志、健康检查、备份恢复策略明确

## 4. 推荐环境变量清单

### 4.1 应用基础配置

| 变量名 | 是否必需 | 用途 | 当前建议 |
|---|---|---|---|
| `APP_NAME` | 否 | 应用显示名 | 可保留 `法律AI` |
| `DEBUG` | 是 | 调试模式开关 | dev=true，test/prod=false |
| `APP_ENV` | 建议新增 | 环境标识 | `dev` / `test` / `prod` |

### 4.2 AI 配置

| 变量名 | 是否必需 | 用途 | 说明 |
|---|---|---|---|
| `MIMO_API_KEY` | 是 | MiMo 鉴权密钥 | 高敏感，禁止提交仓库 |
| `MIMO_API_URL` | 否 | MiMo 接口地址 | 默认值可保留 |
| `MIMO_MODEL` | 否 | 使用的模型名 | 默认 `mimo-v2.5-pro` |

### 4.3 数据库配置

| 变量名 | 是否必需 | 用途 | 说明 |
|---|---|---|---|
| `DATABASE_URL` | 是 | 数据库连接串 | 第 3 周后应以 PostgreSQL 为主 |

### 4.4 向量库配置

| 变量名 | 是否必需 | 用途 | 说明 |
|---|---|---|---|
| `CHROMA_PERSIST_DIR` | 是 | ChromaDB 持久化目录 | 不同环境应隔离 |

### 4.5 文件上传配置

| 变量名 | 是否必需 | 用途 | 说明 |
|---|---|---|---|
| `UPLOAD_DIR` | 是 | 上传文件目录 | 不同环境应隔离 |
| `MAX_FILE_SIZE` | 是 | 上传大小限制 | 当前为 10MB |

### 4.6 OCR 配置

| 变量名 | 是否必需 | 用途 | 说明 |
|---|---|---|---|
| `OCR_PRIMARY_ENGINE` | 否 | 主 OCR 引擎 | 当前默认 `paddle` |
| `OCR_FALLBACK_ENGINE` | 否 | 回退 OCR 引擎 | 当前默认 `tesseract` |
| `OCR_ENABLE_GPU` | 否 | 是否启用 GPU | 默认 false |
| `OCR_LANG` | 否 | OCR 语言配置 | 默认 `ch` |
| `OCR_MIN_WIDTH` | 否 | 图片最小宽度策略 | OCR 质量控制项 |
| `OCR_BINARIZE_THRESHOLD` | 否 | 图像二值化阈值 | OCR 质量控制项 |
| `OCR_AUTO_CONTRAST_CUTOFF` | 否 | 自动对比度阈值 | OCR 质量控制项 |
| `OCR_SHARPEN_FACTOR` | 否 | 锐化系数 | OCR 质量控制项 |
| `OCR_CONTRAST_FACTOR` | 否 | 对比度系数 | OCR 质量控制项 |
| `OCR_JOIN_CJK_SPACES` | 否 | 中文空格拼接策略 | OCR 清洗项 |
| `OCR_PADDLE_USE_ANGLE_CLS` | 否 | Paddle 角度分类 | 主引擎选项 |
| `OCR_PADDLE_DET_LIMIT_SIDE_LEN` | 否 | Paddle 检测边长限制 | 主引擎选项 |
| `OCR_PADDLE_SHOW_LOG` | 否 | Paddle 日志开关 | 正式环境建议 false |
| `TESSERACT_CMD` | 否 | Tesseract 安装路径 | Windows 常见需要 |
| `TESSERACT_LANG` | 否 | Tesseract 语言 | 默认 `chi_sim+eng` |
| `TESSERACT_CONFIG` | 否 | Tesseract 参数 | 可按场景微调 |

## 5. 推荐 `.env.example` 结构

建议后续将 `backend/.env.example` 扩充为以下结构：

```env
# 应用基础配置
APP_NAME=法律AI
APP_ENV=dev
DEBUG=true

# MiMo API 配置
MIMO_API_KEY=your_mimo_api_key_here
MIMO_API_URL=https://token-plan-cn.xiaomimimo.com/v1/chat/completions
MIMO_MODEL=mimo-v2.5-pro

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./homework.db

# ChromaDB 配置
CHROMA_PERSIST_DIR=./data/vector_db

# 上传文件配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# OCR 配置
OCR_PRIMARY_ENGINE=paddle
OCR_FALLBACK_ENGINE=tesseract
OCR_ENABLE_GPU=false
OCR_LANG=ch
OCR_MIN_WIDTH=2200
OCR_BINARIZE_THRESHOLD=0
OCR_AUTO_CONTRAST_CUTOFF=2
OCR_SHARPEN_FACTOR=1.6
OCR_CONTRAST_FACTOR=1.2
OCR_JOIN_CJK_SPACES=true
OCR_PADDLE_USE_ANGLE_CLS=true
OCR_PADDLE_DET_LIMIT_SIDE_LEN=1920
OCR_PADDLE_SHOW_LOG=false
TESSERACT_CMD=
TESSERACT_LANG=chi_sim+eng
TESSERACT_CONFIG=--oem 1 --psm 6
```

## 6. 敏感配置管理规则

### 必须遵守

1. `MIMO_API_KEY` 不允许写死在代码里
2. 真正使用的 `.env` 文件不允许提交到仓库
3. 只能提交 `.env.example` 作为模板
4. 演示 / 生产环境密钥只能放在目标环境变量或部署平台密钥管理中
5. 不允许把数据库真实密码写进 README、文档截图或聊天记录

### 建议遵守

1. 本地开发、测试、生产使用不同 Key
2. 数据库连接串使用独立账户
3. 对 OCR 路径、上传目录、向量库目录按环境区分
4. 后续若引入 Docker / CI，应通过 secrets 注入敏感配置

## 7. 启动方式统一建议

当前项目已有多种启动表述，但后续应统一为以下原则：

### 标准开发启动方式

在项目根目录执行：

```bash
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

### 原则说明

- 所有 Python 命令优先通过项目级 `.venv` 执行
- 后端统一使用 `uvicorn app.main:app`
- 根目录启动时统一指定 `--app-dir backend`
- 不鼓励每个人在不同目录下使用不同方式随意启动

## 8. 当前第 2 周应完成的配置治理动作

1. 扩充 `backend/.env.example`
2. 在 README 中补明确的环境配置说明
3. 形成 `dev/test/prod` 差异说明
4. 明确默认推荐启动命令
5. 为第 3 周 PostgreSQL 迁移预留配置位

## 9. 本周输出结论

本项目当前已经具备基础配置集中化能力，但还缺少“正式交付级别的环境治理”。

第 2 周的重点不是引入复杂配置框架，而是：
- 把变量补全
- 把环境边界讲清
- 把敏感信息规则写清
- 把启动方式统一

这样才能为第 3 周数据库升级与后续部署建设打下稳定基础。
