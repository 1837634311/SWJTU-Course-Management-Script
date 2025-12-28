import json
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText

import ddddocr
import requests
from lxml import etree  # type: ignore

from config import USE_NEW_SYSTEM

if USE_NEW_SYSTEM:
    BASE_URL = "https://jiaowu.swjtu.edu.cn/TMS"
else:
    BASE_URL = "http://jwc.swjtu.edu.cn"

LOGIN_PAGE = BASE_URL + "/service/login.html"


ocr = ddddocr.DdddOcr(show_ad=False)

HEADERS = {
    "Referer": LOGIN_PAGE,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


class LoginExpiredError(Exception):
    """自定义异常：登录过期或未授权"""

    pass


def login(username: str, password: str) -> requests.Session:
    ss = requests.Session()
    ss.headers.update(HEADERS)

    # 访问登录页获取 Cookie
    ss.get(LOGIN_PAGE)

    # 获取验证码
    time.sleep(1)
    if USE_NEW_SYSTEM:
        # TMS 系统需要时间戳
        img_url = f"{BASE_URL}/vatuu/GetRandomNumberToJPEG?test={get_timestamp()}"
    else:
        img_url = f"{BASE_URL}/vatuu/GetRandomNumberToJPEG"

    img = ss.get(img_url)
    time.sleep(3)

    # 识别验证码
    ranstring = ocr.classification(img.content)

    login_action_url = f"{BASE_URL}/vatuu/UserLoginAction"

    data = {
        "username": username,
        "password": password,
        "url": "",
        "returnType": "",
        "returnUrl": "",
        "area": "",
        "ranstring": ranstring,
    }

    res = ss.post(url=login_action_url, data=data)
    try:
        res_json = json.loads(res.text)
    except json.JSONDecodeError:
        raise ValueError(f"登录响应解析失败: {res.text}")

    if res_json.get("loginStatus") == "1":
        print(f"【{get_time()}】登录成功！")
    elif res_json.get("loginStatus") == "-2":
        raise ValueError(
            "登录失败：验证码识别错误\n" + f"具体原因：\n{res_json.get('loginMsg')}",
        )
    elif res_json.get("loginStatus") == "5":
        raise ValueError(
            "登录失败：密码错误，请检查是否是教务网密码，或者填写错误\n"
            + f"具体原因：\n{res_json.get('loginMsg')}",
        )
    elif res_json.get("loginStatus") == "-9":
        raise ValueError(
            "登录失败：密码过于简单，或者未填写密码\n"
            + f"具体原因：\n{res_json.get('loginMsg')}",
        )
    else:
        raise ValueError(f"登录失败: {res_json}")

    # 更新 Referer 并加载用户信息
    ss.headers.update({"Referer": login_action_url})
    data = {
        "url": login_action_url,
        "returnType": "",
        "returnUrl": "",
        "loginMsg": res_json.get("loginMsg"),
    }
    ss.post(url=f"{BASE_URL}/vatuu/UserLoadingAction", data=data)

    return ss


def send(config, subject, text):
    """发送邮件"""
    msg = MIMEText(text, "html", "utf-8")
    msg["From"] = config["from"]
    msg["To"] = ",".join(config["to"])
    msg["Subject"] = subject

    try:
        with smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"]) as smtp:
            smtp.login(config["from"], config["pwd"])
            smtp.send_message(msg)
    except Exception as e:
        print(f"邮件发送失败: {e}")


def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp() -> int:
    """返回时间戳"""
    return int(time.time() * 1000)


def check_session_expired(res_text: str) -> None:
    """检查响应是否包含登录过期信息"""
    if "未登陆" in res_text or "未登录" in res_text or "没有操作权限" in res_text:
        raise LoginExpiredError("登录过期")


def parse_course_table(html_text: str) -> list[dict]:
    """解析课程表格 HTML 并返回结果列表"""
    html = etree.HTML(html_text)
    rows = html.xpath('//*[@id="table3"]/tr')

    if not rows or len(rows) < 2:
        return []

    data_rows = rows[1:-1]
    ret = []
    for item in data_rows:
        try:
            # 处理多行的情况（通过 <br> 分隔）
            text_nodes = item.xpath("td[9]//text()")
            teachers = " ".join([t.strip() for t in text_nodes if t.strip()])

            # 原本的处理办法，
            # date_text = item.xpath("string(td[11])")
            # date = re.sub(r"\s+", " ", date_text.strip()).strip()
            date_nodes = item.xpath("td[11]//text()")
            date = ", ".join([t.strip() for t in date_nodes if t.strip()])

            dic = {
                "teacher": teachers,
                "date": date,
                "course": item.xpath("td[4]/a/span/text()")[0].strip(),
                "course_code": item.xpath("td[3]/a/span/text()")[0].strip(),
                "selected": item.xpath("td[13]/text()")[0].strip(),
                "chooseId": item.xpath("td[2]/span[2]/text()")[0].strip(),
                "teachId": item.xpath("td[2]/span/text()")[0].strip(),
                "campus": item.xpath("td[15]/a/span/text()")[0].strip(),
            }
            ret.append(dic)
        except IndexError:
            continue
    return ret


def parse_delete_list(html_text: str) -> dict[str, str]:
    """解析已选课程列表 HTML，提取 chooseId 到 listId 的映射"""
    html = etree.HTML(html_text)
    elements = html.xpath('//*[@id="table3"]/tr')[1:-1]

    mapping = {}
    for element in elements:
        try:
            current_chooseId = element.xpath("td[3]/text()")[0].strip()
            onclick_attr = element.xpath("td[12]/input/@onclick")[0]
            # 解析如: onclick="...delCourse('...','LIST_ID',...)"
            list_id = onclick_attr.strip().split(",")[-2].strip("'\"")
            mapping[current_chooseId] = list_id
        except IndexError:
            continue
    return mapping


if __name__ == "__main__":
    # 测试代码：请确保 config.py 中有正确的配置
    from config import password, username

    try:
        print("尝试登录...")
        ss = login(username, password)
    except Exception as e:
        print(f"{e}")
