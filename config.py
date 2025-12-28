username = "2022112275"
password = "2023114566"


# system config
# True: 使用选课系统（只在选课期间开放）
# False: 使用原本的教务系统（日常使用的）
USE_NEW_SYSTEM = True

# email config
email_config = {
    "smtp_server": "smtp.qq.com",  # QQ 邮箱
    # "smtp_server": "smtp.my.swjtu.edu.cn",  # SWJTU 邮箱
    # "smtp_server": "smtp.163.com",  # 163 邮箱
    "smtp_port": 465,
    "from": "",
    "pwd": "",
    "to": [""],
}
