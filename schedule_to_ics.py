from datetime import datetime, time, timedelta
import icalendar
import os
import sys
import pytz
import pysjtu

# 获取当前执行脚本的终端路径
running_path = os.getcwd()

# 登录教务系统
if len(sys.argv) > 2:
    username = sys.argv[1]
    password = sys.argv[2]
    print("jaccount账号：", username)
    print("jaccount密码：", password)
else:
    username = input("请输入jaccount账号：")
    password = input("请输入jaccount密码：")

print("正在登录教务系统...")
try:
    client = pysjtu.create_client(username, password)
except Exception as e:
    print("登录失败，请检查账号密码是否正确。")
    sys.exit(1)
print("登录成功。")

# 获取课程安排信息
if len(sys.argv) > 5:
    year = sys.argv[3]
    term = sys.argv[4]
    start_monday_str = sys.argv[5]
    print("学年：", year)
    print("学期：", term)
    print("开学第一天日期：", start_monday_str)
else:
    year = input("请输入学年：")
    term = input("请输入学期[1，2，3]：")
    start_monday_str = input("请输入开学第一天日期（格式：YYYY-MM-DD）：")

year = int(year.split('-')[0])
term = int(term) - 1
start_monday = datetime.strptime(start_monday_str, "%Y-%m-%d")
while start_monday.weekday() != 0:
    start_monday_str = input("输入的日期不是周一，请重新输入：")
    start_monday = datetime.strptime(start_monday_str, "%Y-%m-%d")

schedule = client.schedule(year, term)
if not schedule:
    print("未找到课程安排信息。")
    sys.exit(1)
else:
    print("成功获取课程安排信息。")
    print("正在生成ICS文件...")

# 生成ICS文件保存路径
ics_name = f"{year}-{year + 1}-第{term + 1}学期课程安排.ics"
directory = os.path.join(running_path, "data")
if not os.path.exists(directory):
    os.makedirs(directory)
ics_path = os.path.join(directory, ics_name)

# 创建日历对象
c = icalendar.Calendar()

# 设置日历的默认时区
c.add('timezone', pytz.timezone('Asia/Shanghai'))
c.add('prodid', '-//Jiao Wu Schedule//pysjtu//')
c.add('version', '2.0')
c.add('X-WR-TIMEZONE', 'Asia/Shanghai')
beijing_tz = pytz.timezone('Asia/Shanghai')

# 定义节次时间映射表（以上海交通大学为例）
time_slots = {
    1: (time(8, 00), time(8, 45)),
    2: (time(8, 55), time(9, 40)),
    3: (time(10, 00), time(10, 45)),
    4: (time(10, 55), time(11, 40)),
    5: (time(12, 00), time(12, 45)),
    6: (time(12, 55), time(13, 40)),
    7: (time(14, 00), time(14, 45)),
    8: (time(14, 55), time(15, 40)),
    9: (time(16, 00), time(16, 45)),
    10: (time(16, 55), time(17, 40)),
    11: (time(18, 00), time(18, 45)),
    12: (time(18, 55), time(19, 40)),
    13: (time(19, 50), time(20, 20)),
}

# 遍历课程安排信息来构建事件并添加到日历中
for course in schedule:
    course_name = course.name
    class_name = course.class_name
    day = course.day
    weeks = course.week
    time_range = course.time
    location = course.location
    credit = course.credit
    teacher_name = ', '.join(course.teacher_name)

    # 从 class_name 中提取课号（假设格式为 '(2024-2025-2)-NIS2337-01'，提取 NIS2337）
    parts = class_name.split('-')
    if len(parts) >= 5:
        course_number = parts[3]
    else:
        course_number = ""

    description = f"课号：{class_name}\n 学分：{credit}\n 教师：{teacher_name}" 
    
    # 解析周数
    parsed_weeks = []
    for w in weeks:
        if isinstance(w, range):
            parsed_weeks.extend(list(w))
        elif isinstance(w, int):
            parsed_weeks.append(w)
    parsed_weeks = sorted(list(set(parsed_weeks)))

    # 解析时间
    try:
        start_slot = time_range.start
        end_slot = time_range.stop
        start_time = time_slots[start_slot][0]
        end_time = time_slots[end_slot - 1][1]
    except KeyError:
        print(f"课程{course_name}的节次配置有误，跳过。")
        continue

    # 生成事件
    for week in parsed_weeks:
        try:
            delta_days = (week - 1) * 7 + (day - 1)
            course_date = start_monday + timedelta(days=delta_days)
        except OverflowError:
            continue

        start_datetime = beijing_tz.localize(datetime.combine(course_date, start_time))
        end_datetime = beijing_tz.localize(datetime.combine(course_date, end_time))

        event = icalendar.Event()
        event.add('summary', f"{course_name} {course_number}")
        event.add('location', location)
        event.add('dtstart', start_datetime)
        event.add('dtend', end_datetime)
        event.add('description', description)
        c.add_component(event)



# 将日历对象转换为.ics文件内容并写入文件
with open(ics_path, "wb") as f:
    icalendar_with_seperate_lines = c.to_ical().replace(b"END:VEVENT", b"END:VEVENT\n")
    f.write(icalendar_with_seperate_lines)

print(f"已生成ICS文件：{ics_path}")