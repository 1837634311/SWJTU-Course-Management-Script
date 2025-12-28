# 西南交通大学选课脚本

一个基于 Python 的西南交通大学教务系统选课脚本，支持自动登录、多线程选课、课程查询及批量删课等功能。

## ✨ 主要功能

- **自动登录**：自动登录教务系统，支持失败重试。
- **双系统支持**：兼容日常教务系统和选课系统（通过配置切换）。
- **多方式选课**：提供快速和便捷两种选课方式，更加灵活。
- **课程管理**：
  - 查询某课程所有开课信息（教师、时间、余量）。
  - 快捷退课：支持一次性删除多门课程。
- **交互式操作**：基于 `marimo` 提供友好的交互式界面以及登录状态管理。
- **邮件通知**：选课成功后发送邮件提醒。

## 🛠️ 安装说明

1. **克隆或下载项目**

    ```bash
    git clone https://github.com/1837634311/SWJTU-course-selection-script.git
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
# 用户信息
username = "你的学号"
password = "你的密码"

# 邮件配置（可选，用于选课成功通知）
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
USE_NEW_SYSTEM = False 
```

## 🚀 使用方法

本项目推荐使用 `marimo` 进行交互式操作，方便随时调整策略而不必重新登录。

### 1. 启动 Marimo

在终端运行：

```bash
marimo edit main.py
```

会自动跳转到浏览器。

### 2. 操作流程

在打开的 Notebook 页面中，你可以按顺序执行 Cell：

1. **登录**：运行第一个 Cell 进行登录。
2. **查询课程**：
    - 使用 `query_by_course_code` 查询课程的详细信息（包括 `teachId`）。
    - 使用 `query_teachIds` 批量查询待选课程的 `teachId`。
3. **开始抢课**：
    - 将查询到的 `teachId` 填入 `run_select_course_with_teachId` 相关的 Cell 中，启动多线程抢课。
    - 或者直接使用选课编号（如 B0894）进行抢课。
4. **退课**：
    - 如果需要退课，将选课编号填入 `del_courses` 列表，运行即可。

> [!NOTE]
> 选课前，先分析好第二次选课要选的课程，避免冲突。
>
> 建议第一次选课时，先测试脚本是否正常

## 🙏 感谢

faf4r/SWJTU-course-selection-script：本项目基于 faf4r 的脚本进行修改，感谢 faf4r 的贡献。

## ⚠️ 免责声明

本项目仅供学习交流使用，请勿用于非法用途或对教务系统造成攻击。使用本脚本产生的任何后果由使用者自行承担。项目中提到的老师、课程，仅作为代码示范，与本项目没有任何关系。
