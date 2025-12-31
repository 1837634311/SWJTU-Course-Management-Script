import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import threading

    from config import email_config, password, username
    from User import User
    import marimo as mo
    return User, email_config, mo, password, threading, username


@app.cell
def _(User, email_config, password, username):
    # 先创建用户并登录，用 marimo 就是为了这里登录后，下面有问题可以快速调整，不重新登陆
    user = User(username, password, email_config)
    # 登录成功会显示「【{时间}】登录成功！」
    return (user,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## marimo 不允许在多个单元格重复定义相同的变量名

    所以修改时请注意。也不推荐两种选课方法混用。

    ## 两种选课方法的区别：

    1. chooseId：先根据选课编码查询 teachId，再选课
    2. teachId：直接选课

    ## 推荐使用方法

    1. 先确定要选的课，避免冲突
    2. 在第一次选课时，在「根据选课编码查询 teachId」一节查询待选课程的 teachId
    3. 替换掉下节中的 `teachIds`
    4. 第二次选课前，提前 5~10 分钟登录（开抢后很难再进去了）
    5. 挂起程序，开始选课
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 使用 teachId 选课
    """)
    return


@app.cell
def _(threading, user):
    # 待选课程 teachId
    teachIds = [
        ('B376082258DAC2D9', '张健-地球物理勘探'),
        ('C8807086D60F0EF0', '雷治红-岩体力学'),
    ]

    send_mail = True

    threads = []
    for teachId, course in teachIds:
        thread = threading.Thread(
            target=user.run_select_course_with_teachId,
            args=(teachId, course, send_mail),
        )
        threads.append(thread)
    # 启动线程
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 使用课程编号选课
    """)
    return


@app.cell
def _(threading, user):
    chooseIds = ["B0894"]

    send_email = True

    threads2 = []
    for chooseId in chooseIds:
        thread2 = threading.Thread(
            target=user.run_select_course, args=(chooseId, send_email)
        )
        threads2.append(thread2)

    # 启动线程
    for thread2 in threads2:
        thread2.start()
    for thread2 in threads2:
        thread2.join()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 根据选课编码查询 teachId

    查询课程编码对应的 teachId，然后复制到上面去。

    输出样例：

    ```
    teachIds = [
        ('B376082258DAC2D9', '张健-地球物理勘探'),
        ('C8807086D60F0EF0', '雷治红-岩体力学'),
    ]
    ```
    """)
    return


@app.cell
def _(user):
    chooseId_list = ["B0870", "B0878"]
    user.query_teachIds(chooseId_list)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 根据课程代码查询 teachId 和备注

    可以一次性查询一门课所有的开课信息，方便筛选。

    输出样例：

    ```
    课程名称：岩石学
    任课教师：甘保平 芦飞凡 刘园园
    选课状态：38/55
    选课编码：B0866
    上课校区：犀浦
    上课时间：1-17周 星期一 3-4节, 1-17周 星期二 1-2节
    ```
    """)
    return


@app.cell
def _(user):
    course_code = "SoAD038615"
    user.query_by_course_code(course_code)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 删除课程

    另外，在第一次选课中，实际上只是申请选课，并不是选上了，所以无法使用下面的办法删除选课，还需要到教务系统手动操作。
    """)
    return


@app.cell
def _(user):
    delete_courses = ["B0866"]
    user.del_courses(delete_courses)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Todo

    - [ ] 卡课

    众所周知，当课程容量仅剩余 1 时，两个账号同时申请，有概率能同时申请上。

    关键在于**同时**，而往往存在以下干扰：

    1. **人类**（碳基生物的生理局限）
       - 神经反射弧：信号从大脑传导至指尖存在 100ms+ 的随机波动，所谓的“默契”在服务器看来全是误差。
       - 肌群发达程度：每个手指爆发力不同，按压键程的“物理旅行”时间差异足以让同步宣告失败。

    2. **硬件**（电子元件的“众生平等”）
       - 处理速度：CPU 本身的处理速度差距，本就是一道难以逾越的鸿沟
       - 网卡性能：不同设备的网卡吞吐效率不一，发包时间不同，又是一道先来后到的鸿沟。

    3. **网络**（最后几厘米的玄学）
       - 无线干扰：WiFi 信号在房间内被墙壁、家具反复横跳，谁离信号源近那几厘米，谁就掌握了优先权。
       - 路由器的心情：路由器的排队机制（FIFO）极其冷酷，哪怕包只差微秒，它也会根据“心情”选一个先踢向外网。

    **脚本方案**：抹除一切“人情味”误差，强制对齐微秒级的冷酷同步。
    """)
    return


@app.cell
def _(User):
    username2 = ""
    password2 = ""
    choose_id = ""

    user2 = User(username2, password2)
    return choose_id, user2


@app.cell
def _(choose_id, user, user2, 抢课):
    抢课(user, user2, choose_id)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
