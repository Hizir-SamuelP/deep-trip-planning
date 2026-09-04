#!/usr/bin/env python3
"""Verify a trip calendar against network time before planning around it."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

TIME_HOSTS = (
    "https://www.cloudflare.com",
    "https://www.google.com",
    "https://api.github.com",
)
MAX_CLOCK_SKEW_SECONDS = 60


@dataclass(frozen=True)
class Day:
    date: str
    weekday: str
    is_weekend: bool
    is_public_holiday: bool
    holiday_name: str | None
    in_long_weekend: bool
    long_weekend_range: str | None


def process_clock() -> datetime:
    return datetime.now(timezone.utc)


def shell_clock() -> datetime | None:
    try:
        result = subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%S"],
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
        )
        return datetime.fromisoformat(result.stdout.strip()).replace(
            tzinfo=timezone.utc,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def network_clock() -> tuple[datetime | None, str]:
    for host in TIME_HOSTS:
        try:
            request = urllib.request.Request(
                host,
                method="HEAD",
                headers={"User-Agent": "deep-trip-planning/1.0"},
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                header = response.headers.get("Date")
            if header:
                return parsedate_to_datetime(header).astimezone(timezone.utc), host
        except Exception:
            continue
    return None, ""


def verify_clock() -> tuple[bool, str]:
    process = process_clock()
    shell = shell_clock()
    network, source = network_clock()
    if network is None:
        return False, "无法取得网络时间，拒绝计算日期；请联网后重试。"

    readings = {"进程时钟": process, "网络时间": network}
    if shell is not None:
        readings["系统 date 命令"] = shell
    skew = max(
        abs((reading - network).total_seconds()) for reading in readings.values()
    )
    if skew > MAX_CLOCK_SKEW_SECONDS:
        return (
            False,
            "时钟偏差超过 60 秒，拒绝计算日期；请校正系统时钟后重试。"
            f"（网络来源：{source}；最大偏差：{skew:.1f} 秒）",
        )
    return True, source


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("日期必须是 YYYY-MM-DD") from error


def load_holidays(country: str, start: date, end: date):
    try:
        import holidays
    except ModuleNotFoundError:
        print("缺少 holidays 库。请先运行：pip install holidays", file=sys.stderr)
        raise SystemExit(2)

    country = country.upper()
    try:
        supported = holidays.list_supported_countries()
    except AttributeError:
        supported = {}
    if supported and country not in supported:
        return None
    try:
        years = range(
            (start - timedelta(days=7)).year,
            (end + timedelta(days=7)).year + 1,
        )
        return holidays.country_holidays(country, years=years)
    except (KeyError, NotImplementedError, ValueError):
        return None


def long_weekend_ranges(
    start: date,
    end: date,
    holiday_dates: set[date],
) -> dict[date, tuple[date, date]]:
    window_start = start - timedelta(days=7)
    window_end = end + timedelta(days=7)
    days = [
        window_start + timedelta(days=offset)
        for offset in range((window_end - window_start).days + 1)
    ]
    ranges: dict[date, tuple[date, date]] = {}
    run_start: date | None = None

    for current in [*days, None]:
        non_working = current is not None and (
            current.weekday() >= 5 or current in holiday_dates
        )
        if non_working and run_start is None:
            run_start = current
        if not non_working and run_start is not None:
            run_end = current - timedelta(days=1) if current else days[-1]
            if (run_end - run_start).days + 1 >= 3:
                for offset in range((run_end - run_start).days + 1):
                    ranges[run_start + timedelta(days=offset)] = (run_start, run_end)
            run_start = None
    return ranges


def calendar(country: str, start: date, end: date) -> list[Day] | None:
    local_holidays = load_holidays(country, start, end)
    if local_holidays is None:
        return None
    holiday_dates = set(local_holidays.keys())
    long_weekends = long_weekend_ranges(start, end, holiday_dates)
    result: list[Day] = []
    for offset in range((end - start).days + 1):
        current = start + timedelta(days=offset)
        holiday_name = local_holidays.get(current)
        long_weekend = long_weekends.get(current)
        result.append(
            Day(
                date=current.isoformat(),
                weekday=current.strftime("%A"),
                is_weekend=current.weekday() >= 5,
                is_public_holiday=holiday_name is not None,
                holiday_name=str(holiday_name) if holiday_name else None,
                in_long_weekend=long_weekend is not None,
                long_weekend_range=(
                    f"{long_weekend[0].isoformat()} to {long_weekend[1].isoformat()}"
                    if long_weekend
                    else None
                ),
            )
        )
    return result


def print_calendar(country: str, days: list[Day]) -> None:
    print(f"已用网络时间核验 · {country}")
    print("日期         星期       周末  法定假日  假日名称                 连假区间")
    print("-" * 88)
    for day in days:
        print(
            f"{day.date}  {day.weekday:<9}  {'是' if day.is_weekend else '否':<4}  "
            f"{'是' if day.is_public_holiday else '否':<8}  "
            f"{(day.holiday_name or '—'):<23}  {day.long_weekend_range or '—'}"
        )
    print("\nJSON:")
    print(json.dumps([asdict(day) for day in days], ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify weekdays, public holidays, and long weekends for a trip."
    )
    parser.add_argument("country", help="ISO 3166-1 alpha-2 code, e.g. JP")
    parser.add_argument("start_date", type=parse_date, help="YYYY-MM-DD")
    parser.add_argument("end_date", type=parse_date, help="YYYY-MM-DD")
    args = parser.parse_args()
    if args.end_date < args.start_date:
        parser.error("结束日期不能早于开始日期")

    verified, detail = verify_clock()
    if not verified:
        print(detail, file=sys.stderr)
        return 1
    days = calendar(args.country, args.start_date, args.end_date)
    if days is None:
        print(
            f"{args.country.upper()}：该地区无假日数据，需手工核验。"
            "请从当地政府或旅游主管部门的官方日历确认法定假日与连假。"
        )
        return 0
    print_calendar(args.country.upper(), days)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
