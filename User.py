import re
import sys
import time
import traceback

import utils
from utils import BASE_URL, LoginExpiredError


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

    def _request(self, method: str, url: str, **kwargs):
        """统一请求，包含登录状态检查"""
        res = self.ss.request(method=method, url=url, **kwargs)
        utils.check_session_expired(res.text)
        return res

    def _monitor_loop(self, task_name: str, func, args=(), success_check=None):
        """通用监控循环

        参数：
            task_name: 任务名称
            func: 每次循环执行的函数
            args: 函数参数
            success_check: 判断是否成功的回调函数，接收 func 的返回值
        """
        assert success_check is not None, "必须提供 success_check 回调函数"
        print(f"开始选课: {task_name}")

        while True:
            try:
                # 执行核心逻辑
                result = func(*args)
                print(f"[{utils.get_time()}] {task_name}: {result}")

                # 检查是否成功
                if success_check(result):
                    print(f"课程 {task_name} 已完成。")
                    break

            except LoginExpiredError:
                print("登录过期，尝试重新登录...")
                try:
                    self.ss = self.login(self.username, self.password)
                except Exception as e:
                    print(f"重连失败: {e}")
            except Exception as e:
                print(f"[{utils.get_time()}] {task_name} 发生异常: {e}")
                # 防止 CPU 空转
                time.sleep(1)

            time.sleep(1)

    def query_by_course_code(self, code: str) -> None:
        """按课程代码查询可选课程，返回可选课程的相关信息"""
        query_url = f"{BASE_URL}/vatuu/CourseStudentAction"
        data = {
            "setAction": "studentCourseSysSchedule",
            "viewType": "",
            "jumpPage": 1,
            "selectAction": "CourseCode",
            "key1": code,
            "courseType": "all",
            "key4": "",
            "btn": "执行查询",
        }
        res = self._request("POST", query_url, data=data)
        courses: list[dict[str, str]] = utils.parse_course_table(res.text)

        if courses:
            for course in courses:
                print(f"课程名称：{course['course']}")
                print(f"任课教师：{course['teacher']}")
                print(f"选课状态：{course['selected']}")
                print(f"选课编码：{course['chooseId']}")
                print(f"上课校区：{course['campus']}")
                print(f"上课时间：{course['date']}\n")
        else:
            print("未找到课程信息，请检查课程代码是否正确")

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
        res = self._request("POST", query_url, data=data)
        course = utils.parse_course_table(res.text)
        if course:
            return course[0]
        else:
            return None

    def query_teachIds(self, chooseIds: list[str]) -> None:
        """查询多项课程的 teachId，方便替换"""
        print("teachIds = [")

        for chooseId in chooseIds:
            course = self.query_by_chooseId(chooseId)
            if course:
                teacher: str = course["teacher"]
                course_name: str = course["course"]
                teachId: str = course["teachId"]
                print(f"    ('{teachId}', '{teacher}-{course_name}'),")
            else:
                print(f"    未找到 {chooseId} 信息，请检查选课编码是否正确")

        print("]")

    def select_course(self, teachId) -> str:
        """根据 teachId 选课"""
        url = f"{BASE_URL}/vatuu/CourseStudentAction?setAction=addStudentCourseApply&teachId={teachId}&isBook=1&tt={utils.get_timestamp()}"
        res = self._request("GET", url)

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
        # 删除课程似乎不需要检查 session expired? 原代码里没有检查，保持原样，但在 _request 里会有检查
        # 稳妥起见，统一走 _request
        url = f"{BASE_URL}/vatuu/CourseStudentAction?setAction=delStudentCourseList&listId={listId}&teachId={chooseId}&tt={utils.get_timestamp()}"
        res = self._request("GET", url)
        return res.text

    def del_courses(self, chooseIds: list[str]) -> None:
        """批量删除课程，只查询一次列表"""
        url = f"{BASE_URL}/vatuu/CourseStudentAction?setAction=studentCourseSysList&viewType=delCourse"
        res = self._request("GET", url)

        mapping = utils.parse_delete_list(res.text)

        for chooseId in chooseIds:
            target_listId = mapping.get(chooseId)
            if target_listId:
                self.del_course(chooseId=chooseId, listId=target_listId)
                print(f"尝试删除课程 {chooseId} done.")
            else:
                print(f"未在已选列表中找到课程 {chooseId}")

    def run_select_course(self, chooseId: str):
        """持续尝试选课任务"""
        teachId = self.get_teachId(chooseId)
        if teachId:
            self.run_select_course_with_teachId(teachId, course_name=chooseId)
        else:
            print("未找到 teachId，请检查课程编码是否正确")

    def run_select_course_with_teachId(self, teachId: str, course_name: str):
        """已知 teachId 直接选课任务"""

        def check_success(msg):
            status: list[str] = ["选课成功", "选课申请成功", "冲突"]
            return any(s in msg for s in status)

        self._monitor_loop(
            task_name=f"{course_name}",
            func=self.select_course,
            args=(teachId,),
            success_check=check_success,
        )


if __name__ == "__main__":
    # 使用从 config 导入的配置，避免硬编码密码
    from config import email_config, password, username

    if not username or not password:
        print("请先在 config.py 中配置 username 和 password！")
        sys.exit(1)

    user = User(username, password, email_config)
