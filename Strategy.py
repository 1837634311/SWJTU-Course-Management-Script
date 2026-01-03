import threading
import time

import utils
from User import User
from utils import BASE_URL, LoginExpiredError


def monitor_loop(
    user: User, task_name: str, func, interval, args=(), check=None, send_email=False
):
    """通用监控循环

    参数:
        user: User 对象实例
        task_name: 任务名称
        func: 每次循环执行的函数
        interval: 循环间隔
        args: 函数参数
        check: 判断是否完成的回调函数，接收 func 的返回值
        send_email: 是否发送邮件
    """

    def check_completed(msg: str) -> bool:
        status: list[str] = ["选课成功", "选课申请成功", "冲突"]
        return any(s in msg for s in status)

    if check is None:
        check = check_completed

    print(f"开始选课: {task_name}")

    while True:
        try:
            # 执行核心逻辑
            result: str = func(*args)
            print(f"[{utils.get_time()}] {task_name} : {result}")

            # 检查是否成功
            if check(result):
                print(f"课程 {task_name} 已完成。")
                if "成功" in result and send_email:
                    user.send(f"选课完成: {task_name}", result)
                break

        except LoginExpiredError:
            print("登录过期，尝试重新登录...")
            try:
                user.ss = user.login(user.username, user.password)
            except Exception as e:
                print(f"重连失败: {e}")
        except Exception as e:
            print(f"[{utils.get_time()}] {task_name} 发生异常: {e}")

        time.sleep(interval)


def query_by_course_code(user: User, code: str) -> None:
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
    res = user.request("POST", query_url, data=data)
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


def query_teachIds(user: User, chooseIds: list[str]) -> None:
    """查询多项课程的 teachId，方便替换"""
    print("teachIds = [")

    for chooseId in chooseIds:
        course = user.query_by_chooseId(chooseId)
        if course:
            teacher: str = course["teacher"]
            course_name: str = course["course"]
            teachId: str = course["teachId"]
            print(f"    ('{teachId}', '{teacher}-{course_name}'),")
        else:
            print(f"    未找到 {chooseId} 信息，请检查选课编码是否正确")

    print("]")


def del_courses(user: User, chooseIds: list[str]) -> None:
    """批量删除课程，只查询一次列表

    参数：
        user: 用户实例
        chooseIds: 选课编号列表
    """
    mapping = user.query_selected_courses()

    for chooseId in chooseIds:
        target_listId = mapping.get(chooseId)
        if target_listId:
            user.del_course(chooseId=chooseId, listId=target_listId)
            print(f"尝试删除课程 {chooseId} done.")
        else:
            print(f"未在已选列表中找到课程 {chooseId}")


def run_select_courses_with_teachIds(
    user: User, teachIds: list[tuple[str, str]], interval=0.5, send_email=False
):
    """已知 teachId 直接选课任务（多线程）"""
    threads: list[threading.Thread] = []
    for tid, name in teachIds:
        thread = threading.Thread(
            target=monitor_loop,
            kwargs={
                "user": user,
                "task_name": name,
                "interval": interval,
                "func": user.select_course,
                "args": (tid,),
                "send_email": send_email,
            },
        )
        threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def run_select_courses(
    user: User, chooseIds: list[str], interval=0.5, send_email=False
):
    """根据选课编号持续尝试选课任务（多线程）"""
    tasks: list[tuple[str, str]] = []
    for cid in chooseIds:
        tid = user.get_teachId(cid)
        if tid:
            tasks.append((tid, cid))
        else:
            print(f"[{utils.get_time()}] : 编号 {cid} 无效，自动跳过")

    if tasks:
        run_select_courses_with_teachIds(user, tasks, interval, send_email)
    else:
        print(f"[{utils.get_time()}] : 无可执行任务")
