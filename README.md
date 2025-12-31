# 西南交通大学课程管理脚本

一个基于 Python 的西南交通大学教务系统课程管理脚本，支持自动登录、选课、课程查询及退课等功能。

## ✨ 主要功能

- **自动登录**：自动登录教务系统，支持失败重试。
- **双系统支持**：兼容日常教务系统和选课系统（通过配置切换）。
- **课程管理**：
  - 支持选课，并提供快速和便捷两种选课方式。
  - 查询某课程所有开课信息（教师、时间、余量）。
  - 支持退课：支持一次性删除多门课程。
- **交互式操作**：基于 `marimo` 提供友好的交互式界面以及登录状态管理。
- **邮件通知**（可选）：任务成功后发送邮件提醒。

## 🛠️ 安装说明

1. **克隆或下载项目**

    ```bash
    git clone https://github.com/1837634311/SWJTU-Course-Management-Script.git
    cd SWJTU-Course-Management-Script
    ```

2. **安装依赖**

    1. 建议使用 [uv](https://github.com/astral-sh/uv) 管理项目：

        1. 安装 uv

            ```bash
            # On Windows.
            powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
            ```

            ```bash
            # On macOS and Linux.
            curl -LsSf https://astral.sh/uv/install.sh | sh
            ```

        2. 安装依赖：

            ```bash
            uv sync --locked
            ```

    2. 或者使用 `pip`:

        ```bash
        pip install -r requirements.txt
        ```

## ⚙️ 配置指南

修改 `config.py` 文件，需要包含以下信息：

```python
username = "你的学号"
password = "你的密码"

# 邮件配置（可选，例如用于选课成功通知）
email_config = {
    "smtp_server": "smtp.qq.com",  # 例如 QQ 邮箱
    "smtp_port": 465,              # 请按照邮件服务提供商的说明填写
    "from": "你的邮箱@qq.com",
    "pwd": "你的邮箱授权码",       # 注意是应用密码不是账号主密码
    "to": ["接收通知的邮箱"]       # 可以为发送的邮箱
}

# 系统选择
# True: 使用选课系统（只在选课期间开放）
# False: 使用原本的教务系统（日常使用的）
USE_NEW_SYSTEM = True
```

## 🚀 使用方法

本项目推荐使用 `marimo` 进行交互式操作，方便随时调整策略而不必重新登录。

### 1. 启动 Marimo

在终端运行：

```bash
.venv/Scripts/Activate
marimo edit main.py
```

会自动跳转到浏览器。

### 2. 操作流程

在打开的 Notebook 页面中，有如下几个 Cell，分别对应不同的功能：

-  **登录**：运行第二个 Cell 进行登录。
-  **查询课程**：
    1. `query_by_course_code`：查询某课程代码下，所有课程的详细信息，包括教师、时间、余量、课程编码、校区等。
    2. `query_teachIds`：根据课程编码，批量查询课程的 `teachId`。
-  **选课**：
    1. `run_select_course_with_teachId`：根据 `teachId`，批量选课。
    2. `run_select_course_with_course_code`：根据课程编码，批量选课。
    3. `interval`：选课间隔，单位为秒。
       建议只在高峰期设置较短间隔，如果是为了挂着等选修，可以设置长一点。
    4. `send_mail`：若设置为 `True`，则可以在选课成功时发送邮件通知。
-  **退课**：
    1. `del_courses`：根据课程编号，批量退课。

> [!NOTE]
> 如果需要选课，建议先分析好第二次选课要选的课程，避免冲突。
>
> 建议第一次选课时，先测试脚本是否正常

> [!WARNING]
> 只有返回选课成功才退出线程，否则会持续循环选课。因此退出需要重启内核。

## 🙏 感谢

[faf4r/SWJTU-course-selection-script](https://github.com/faf4r/SWJTU-course-selection-script)：基于此项目进行修改，感谢 faf4r 的贡献。

## ⚠️ 免责声明

本项目仅供学习交流使用，请勿用于非法用途或对教务系统造成攻击。使用本脚本产生的任何后果由使用者自行承担。项目中提及的老师、课程等，仅作为示例，与本项目没有任何关系。
