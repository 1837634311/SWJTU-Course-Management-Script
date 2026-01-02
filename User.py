import re
import sys
import time
import traceback

import utils
from utils import BASE_URL


class User:
    def __init__(self, username, password, email_config):
        self.username = username
        self.password = password
        self.email_config = email_config
        self.ss = self.login(username, password)

    @staticmethod
    def login(username, password):
        """登录并返回 session，包含重试机制"""
        while True:
            try:
                ss = utils.login(username, password)
                return ss
            except ValueError as msg:
                print(f"【{utils.get_time()}】:{msg}")
                # 很多时候是验证码错误，重试即可
                time.sleep(2)
            except Exception:
                print("*" * 8 + f"\n意外报错： {utils.get_time()}\n")
                print(traceback.format_exc())
                # 严重错误退出，避免死循环消耗资源
                sys.exit(1)

    def send(self, subject, text="") -> None:
        utils.send(self.email_config, subject, text)

    def request(self, method: str, url: str, **kwargs):
        """统一请求，包含登录状态检查"""
        res = self.ss.request(method=method, url=url, **kwargs)
        utils.check_session_expired(res.text)
        return res

    def query_by_chooseId(self, chooseId: str) -> dict[str, str] | None:
        """根据选课编号查询课程信息"""
        query_url = f"{BASE_URL}/vatuu/CourseStudentAction"
        data = {
            "setAction": "studentCourseSysSchedule",
            "viewType": "",
            "jumpPage": 1,
            "key1": chooseId,
            "selectAction": "TeachID",
            "courseType": "all",
            "key4": "",
            "btn": "执行查询",
        }
        res = self.request("POST", query_url, data=data)
        course = utils.parse_course_table(res.text)
        if course:
            return course[0]
        else:
            return None

    def select_course(self, teachId) -> str:
        """根据 teachId 选课"""
        url = f"{BASE_URL}/vatuu/CourseStudentAction?setAction=addStudentCourseApply&teachId={teachId}&isBook=1&tt={utils.get_timestamp()}"
        res = self.request("GET", url)

        matches = re.findall("<message>(.*?)</message>", res.text)
        if matches:
            return matches[0]
        else:
            # 从系统还未开放就选课，所以返回信息而非错误
            return "选课系统未开放"

    def get_teachId(self, chooseId: str) -> str | None:
        """根据选课编号查询 teachId"""
        res = self.query_by_chooseId(chooseId)
        if res:
            return res.get("teachId")
        return None

    def del_course(self, listId, chooseId) -> str:
        """删除课程"""
        # 删除课程似乎不需要检查 session expired? 原代码里没有检查，保持原样，但在 request 里会有检查
        # 稳妥起见，统一走 request
        url = f"{BASE_URL}/vatuu/CourseStudentAction?setAction=delStudentCourseList&listId={listId}&teachId={chooseId}&tt={utils.get_timestamp()}"
        res = self.request("GET", url)
        return res.text


if __name__ == "__main__":
    # 使用从 config 导入的配置，避免硬编码密码
    from config import email_config, password, username

    if not username or not password:
        print("请先在 config.py 中配置 username 和 password！")
        sys.exit(1)

    user = User(username, password, email_config)
