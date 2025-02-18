# Course Schedule to ICS Converter

**schedule_to_ics**通过`pysjtu`库抓取考试安排，并数据源转换为 ICS 文件，以便导入到日历应用中。

## `schedule_to_ics`使用方法

### 依赖安装

在运行脚本之前，请确保已安装以下依赖项：

```bash
pip install icalender pytz pysjtu
```

### 运行脚本

你可以通过以下两种方式运行脚本：

1. 使用命令行参数指定Jaccount账号、密码和学年、学期

    ```bash
    python schedule_to_ics.py username password year term first_Monday
    ```
    例如：

    ```bash
    python schedule_to_ics.py MyJaccount sjtu1896 2024 2 2025-02-17 
    ```

2. 不使用命令行参数，脚本将提示输入Jaccount账号、密码和学年、学期

    ```bash
    python schedule_to_ics.py
    ```

3. 运行脚本后，将在运行目录下创建一个名为`data`的文件夹，并在其中生成一个名为 `{学年}-{学期}课程安排.ics` 的 ICS 文件，包含所有课程安排。

### 数据格式

脚本假设考试安排信息存储在一个列表中，每个考试信息是一个字典，包含以下字段：

- `name` (str) – literal name of the course.
- `day` (int | None) – in which day(s) of weeks classes are given.
- `week` (Optional[list]) – in which week(s) classes are given.
- `time` (Optional[range]) – at which time of days classes are given.
- `location` (str | None) – the place where classes are given.
- `credit` (float | None) – credits that the course provides.
- `teacher_name` (List[str]) – the teacher who offers this course.
- `class_name` (str) – class name (constant between years).

### 注意事项

- 确保日期和时间格式正确。
- 脚本默认使用 `Asia/Shanghai` 时区。

### 特别鸣谢

- [PySJTU](https://github.com/PhotonQuantum/pysjtu)
- [PySJTU documentation](https://pysjtu.readthedocs.io)