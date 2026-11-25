# Course Schedule to ICS Converter

在 Chromium 中完成交大 jAccount 登录后，从教学信息服务网查询个人课表并导出 ICS。

## 安装

使用 Python 3.9 或更新版本。在项目目录执行：

```bash
python -m pip install icalendar pytz playwright
python -m playwright install chromium
```

## 导出课表

```bash
python schedule_to_ics.py 2026 1
```

`2026 1` 表示 2026–2027 学年第一学期。浏览器打开后，在交大官方页面登录，例如使用「交我办」扫码。脚本会询问教学第一周周一的日期，也可在命令中直接传入：

```bash
python schedule_to_ics.py 2026 1 2026-09-07
```

请按校历填写日期。也可以不传任何参数，按脚本提示填写学年、学期和日期。

生成的 ICS 位于脚本目录下的 `data/`。登录凭据和会话无需写入配置文件。
