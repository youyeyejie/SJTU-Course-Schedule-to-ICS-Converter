import argparse
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path

import icalendar
import pytz

from sjtu_login import fetch_courses

SHANGHAI = pytz.timezone("Asia/Shanghai")
TIME_SLOTS = [
    ((8, 0), (8, 45)), ((8, 55), (9, 40)), ((10, 0), (10, 45)),
    ((10, 55), (11, 40)), ((12, 0), (12, 45)), ((12, 55), (13, 40)),
    ((14, 0), (14, 45)), ((14, 55), (15, 40)), ((16, 0), (16, 45)),
    ((16, 55), (17, 40)), ((18, 0), (18, 45)), ((18, 55), (19, 40)),
    ((19, 50), (20, 20)),
]


WEEK_RANGE = re.compile(r"(\d+)(?:\s*-\s*(\d+))?\s*周?\s*(?:[(（]([单双])周?[)）])?")


def course_weeks(value):
    weeks = set()
    for part in re.split(r"[,，、]", value or ""):
        match = WEEK_RANGE.fullmatch(part.strip())
        if match is None:
            raise ValueError("无法识别上课周次")
        first, last, parity = match.groups()
        start, end = int(first), int(last or first)
        if not 1 <= start <= end <= 53:
            raise ValueError("上课周次超出范围")
        weeks.update(week for week in range(start, end + 1) if not parity or week % 2 == (parity == "单"))
    return sorted(weeks)


def main():
    parser = argparse.ArgumentParser(description="通过交大教务网查询课表并导出 ICS。")
    parser.add_argument("year", nargs="?", help="学年起始年份，例如 2026")
    parser.add_argument("term", nargs="?", type=int, choices=(1, 2, 3), help="学期")
    parser.add_argument("first_monday", nargs="?", type=date.fromisoformat, help="教学第一周周一（YYYY-MM-DD）")
    args = parser.parse_args()
    try:
        year = int((args.year or input("请输入学年：")).split("-")[0])
        term = args.term or int(input("请输入学期[1，2，3]："))
    except ValueError:
        parser.error("请输入有效的学年和学期。")
    if term not in (1, 2, 3):
        parser.error("学期必须为 1、2 或 3。")

    first_monday = args.first_monday
    if first_monday and first_monday.weekday() != 0:
        parser.error("教学第一周日期必须为周一。")
    try:
        lessons = fetch_courses(year, term)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None

    if not lessons:
        raise SystemExit("未找到课程安排。")

    while first_monday is None:
        try:
            candidate = date.fromisoformat(input("请输入教学第一周周一（YYYY-MM-DD）："))
        except ValueError:
            print("请输入有效的日期。")
            continue
        if candidate.weekday() != 0:
            print("教学第一周日期必须为周一。")
            continue
        first_monday = candidate

    calendar = icalendar.Calendar()
    calendar.add("prodid", "-//SJTU Course Schedule//")
    calendar.add("version", "2.0")
    calendar.add("X-WR-TIMEZONE", "Asia/Shanghai")
    for lesson in lessons:
        name = lesson.get("kcmc") or "未命名课程"
        try:
            day = int(lesson["xqj"])
            slots = str(lesson["jcs"]).replace("节", "").split("-", maxsplit=1)
            first_slot, last_slot = int(slots[0]), int(slots[-1])
            if not 1 <= day <= 7 or not 1 <= first_slot <= last_slot <= len(TIME_SLOTS):
                raise ValueError("星期或节次超出范围")
            weeks = course_weeks(lesson.get("zcd"))
        except (KeyError, TypeError, ValueError):
            print(f"课程 {name} 的上课安排尚未公布或无法识别，已跳过。")
            continue

        start_time = time(*TIME_SLOTS[first_slot - 1][0])
        end_time = time(*TIME_SLOTS[last_slot - 1][1])
        for week in weeks:
            lesson_date = first_monday + timedelta(weeks=week - 1, days=day - 1)
            event = icalendar.Event()
            event.add("summary", f"{name} {lesson.get('kch_id') or ''}".strip())
            event.add("location", lesson.get("cdmc") or "")
            event.add("dtstart", SHANGHAI.localize(datetime.combine(lesson_date, start_time)))
            event.add("dtend", SHANGHAI.localize(datetime.combine(lesson_date, end_time)))
            event.add("description", f"教学班：{lesson.get('jxbmc') or ''}\n学分：{lesson.get('xf') or ''}\n教师：{lesson.get('xm') or ''}")
            calendar.add_component(event)

    if not calendar.subcomponents:
        raise SystemExit("未找到可导出的课程安排。")
    directory = Path(__file__).resolve().parent / "data"
    directory.mkdir(exist_ok=True)
    path = directory / f"{year}-{year + 1}-第{term}学期课程安排.ics"
    path.write_bytes(calendar.to_ical())
    print(f"已生成 ICS 文件：{path}")


if __name__ == "__main__":
    main()
