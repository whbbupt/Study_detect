# 基于 YOLOv8 的学习状态视觉识别系统

这是一个基于 Python、Tkinter、SQLite、OpenCV 和 YOLOv8 的学习状态检测应用。系统支持用户登录注册、图片检测、摄像头/视频检测、检测记录保存、操作日志和告警统计图导出。

当前模型识别三类学习场景异常行为：

- `phone`：玩手机
- `sleep`：睡觉
- `eat`：吃东西

## 功能概览

- Tkinter 图形界面
- 用户注册、登录、修改密码和管理员用户管理
- SQLite 保存用户、日志和检测记录
- YOLOv8 推理封装
- SmartDetect 后处理规则，减少单帧误报
- 图片检测、摄像头/视频检测
- 检测告警统计图导出
- URL 可达性检测和网络异常处理

## 项目结构

```text
study-behavior-monitor/
  app.py
  ui.py
  ai_core.py
  auth.py
  db.py
  network_utils.py
  visualization.py
  requirements.txt
  data.yaml
  LICENSE
  .gitignore
  models/
    best.pt
  examples/
```

## 环境要求

- Python 3.9 或更高版本
- Windows、macOS 或 Linux
- 摄像头检测需要本机有可用摄像头

## 本地运行

```bash
git clone https://github.com/your-name/study-behavior-monitor.git
cd study-behavior-monitor

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python app.py
```

macOS/Linux 激活虚拟环境时使用：

```bash
source .venv/bin/activate
```

## 模型文件

应用默认读取：

```text
models/best.pt
```

如果运行时报模型不存在，请把训练好的 YOLOv8 权重文件放到 `models/best.pt`。

## 默认账号

首次启动时会自动创建默认管理员账号：

```text
用户名：admin
密码：admin123
```

首次登录后建议立即修改默认密码。

## 训练数据

`data.yaml` 使用相对路径：

```yaml
path: .
train: train/images
val: val/images
```

如果需要重新训练，请自行准备 `train/images`、`train/labels`、`val/images`、`val/labels` 数据集目录。训练数据默认不纳入 Git 仓库，避免仓库过大或引入版权/隐私问题。

## 主要模块

| 文件 | 功能 |
| --- | --- |
| `app.py` | 程序入口 |
| `ui.py` | Tkinter 图形界面和交互流程 |
| `ai_core.py` | YOLOv8 推理与 SmartDetect 后处理 |
| `auth.py` | 登录、注册、密码修改和权限判断 |
| `db.py` | SQLite 数据库表设计和 CRUD |
| `network_utils.py` | URL 检测和下载异常处理 |
| `visualization.py` | 检测告警统计图导出 |
| `data.yaml` | YOLOv8 数据集配置 |

## 协作流程建议

```bash
git checkout -b feature/your-task
git add .
git commit -m "Describe your change"
git push origin feature/your-task
```

然后在 GitHub 上提交 Pull Request，由其他协作者 review 后合并到 `main` 分支。
