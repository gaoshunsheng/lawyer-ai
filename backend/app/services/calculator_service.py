"""赔偿计算器 - 纯函数实现，基于中国劳动法律法规。

计算类型:
- illegal_termination: 违法解除劳动合同 (2N)
- overtime: 加班费
- annual_leave: 未休年休假工资
- work_injury: 工伤赔偿
"""

from __future__ import annotations

from dataclasses import dataclass


# 2024年全国城镇非私营单位在岗职工月平均工资（社平工资）
# 实际使用中会取统筹地区上年度社平工资
SOCIAL_AVERAGE_MONTHLY = {
    "全国": 10058,
    "北京": 13930,
    "上海": 13490,
    "广东": 11208,
    "深圳": 14568,
    "江苏": 10458,
    "浙江": 10232,
    "天津": 9652,
    "四川": 8524,
    "重庆": 8236,
    "湖北": 7985,
    "湖南": 7652,
    "山东": 8965,
    "河南": 7236,
    "河北": 7586,
    "福建": 9123,
    "安徽": 7856,
    "陕西": 8123,
    "辽宁": 7856,
    "吉林": 6856,
    "黑龙江": 6523,
}


@dataclass
class CalcResult:
    result: float
    breakdown: dict
    basis: list[str]
    steps: list[str]


def calculate_illegal_termination(
    *,
    monthly_salary: float,
    work_years: float,
    city: str = "全国",
    is_high_salary: bool = False,
) -> CalcResult:
    """违法解除劳动合同赔偿金 = 2N (经济补偿标准的二倍)

    经济补偿 = 工作年限 × 月工资
    N = 工作年限 (每满一年支付一个月工资, 六个月以上不满一年的按一年算, 不满六个月的支付半个月)
    高薪封顶: 月工资高于社平工资3倍的, 按社平工资3倍支付, 年限最高12年
    """
    basis = []
    steps = []
    social_avg = SOCIAL_AVERAGE_MONTHLY.get(city, SOCIAL_AVERAGE_MONTHLY["全国"])
    cap = social_avg * 3

    basis.append("《劳动合同法》第47条: 经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。")
    basis.append("《劳动合同法》第87条: 用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第47条规定的经济补偿标准的二倍向劳动者支付赔偿金。")

    actual_salary = monthly_salary
    actual_years = work_years

    if is_high_salary or monthly_salary > cap:
        actual_salary = cap
        steps.append(f"月工资({monthly_salary:.2f}元) > 社平工资3倍({cap:.2f}元), 按封顶基数{cap:.2f}元计算")
        basis.append("《劳动合同法》第47条: 劳动者月工资高于用人单位所在地区上年度职工月平均工资三倍的，按三倍支付，年限最高不超过十二年。")
        actual_years = min(work_years, 12)

    # 计算N
    years_int = int(actual_years)
    months_remainder = actual_years - years_int

    if months_remainder >= 0.5:
        n = years_int + 1
    elif months_remainder > 0:
        n = years_int + 0.5
    else:
        n = years_int

    n = max(n, 0.5)  # 最少半个月
    compensation = actual_salary * n  # 经济补偿 N
    total = compensation * 2  # 违法解除 2N

    steps.append(f"工作年限: {work_years}年 → N = {n}")
    steps.append(f"经济补偿(N) = 月工资({actual_salary:.2f}元) × N({n}) = {compensation:.2f}元")
    steps.append(f"违法解除赔偿金(2N) = {compensation:.2f}元 × 2 = {total:.2f}元")

    breakdown = {
        "monthly_salary": monthly_salary,
        "actual_base_salary": actual_salary,
        "social_average_salary": social_avg,
        "is_capped": monthly_salary > cap,
        "cap_amount": cap if monthly_salary > cap else None,
        "work_years": work_years,
        "actual_years": actual_years,
        "n": n,
        "compensation_n": compensation,
        "total_2n": total,
    }

    return CalcResult(result=round(total, 2), breakdown=breakdown, basis=basis, steps=steps)


def calculate_overtime(
    *,
    hourly_wage: float,
    overtime_hours_workday: float = 0,
    overtime_hours_weekend: float = 0,
    overtime_hours_holiday: float = 0,
) -> CalcResult:
    """加班费计算

    工作日加班: 150% × 小时工资
    休息日加班: 200% × 小时工资
    法定节假日加班: 300% × 小时工资
    """
    basis = [
        "《劳动法》第44条: 安排劳动者延长工作时间的，支付不低于工资的百分之一百五十的工资报酬；"
        "休息日安排劳动者工作又不能安排补休的，支付不低于工资的百分之二百的工资报酬；"
        "法定休假日安排劳动者工作的，支付不低于工资的百分之三百的工资报酬。",
    ]

    steps = []
    total = 0.0
    breakdown = {}

    if overtime_hours_workday > 0:
        amount = hourly_wage * 1.5 * overtime_hours_workday
        total += amount
        steps.append(f"工作日加班: {hourly_wage:.2f}元/h × 150% × {overtime_hours_workday}h = {amount:.2f}元")
        breakdown["workday_overtime"] = {"hours": overtime_hours_workday, "rate": 1.5, "amount": amount}

    if overtime_hours_weekend > 0:
        amount = hourly_wage * 2.0 * overtime_hours_weekend
        total += amount
        steps.append(f"休息日加班: {hourly_wage:.2f}元/h × 200% × {overtime_hours_weekend}h = {amount:.2f}元")
        breakdown["weekend_overtime"] = {"hours": overtime_hours_weekend, "rate": 2.0, "amount": amount}

    if overtime_hours_holiday > 0:
        amount = hourly_wage * 3.0 * overtime_hours_holiday
        total += amount
        steps.append(f"法定节假日加班: {hourly_wage:.2f}元/h × 300% × {overtime_hours_holiday}h = {amount:.2f}元")
        breakdown["holiday_overtime"] = {"hours": overtime_hours_holiday, "rate": 3.0, "amount": amount}

    steps.append(f"加班费合计: {total:.2f}元")

    breakdown["hourly_wage"] = hourly_wage
    breakdown["total_overtime_hours"] = overtime_hours_workday + overtime_hours_weekend + overtime_hours_holiday
    breakdown["total_amount"] = total

    return CalcResult(result=round(total, 2), breakdown=breakdown, basis=basis, steps=steps)


def calculate_annual_leave(
    *,
    daily_wage: float,
    total_leave_days: float,
    used_leave_days: float = 0,
    work_years_total: float = 0,
) -> CalcResult:
    """未休年休假工资补偿

    法定年休假天数:
    - 累计工作满1年不满10年: 5天
    - 累计工作满10年不满20年: 10天
    - 累计工作满20年: 15天

    未休年休假工资 = 日工资 × 200% × 未休天数 (因为正常工作期间已支付100%, 额外补200%)
    """
    basis = [
        "《职工带薪年休假条例》第3条: 职工累计工作已满1年不满10年的，年休假5天；已满10年不满20年的，年休假10天；已满20年的，年休假15天。",
        "《企业职工带薪年休假实施办法》第10条: 用人单位经职工同意不安排年休假或者安排职工年休假天数少于应休年休假天数的，应当在本年度内对职工应休未休年休假天数，按照其日工资收入的300%支付未休年休假工资报酬，其中包含用人单位支付职工正常工作期间的工资收入。",
    ]

    steps = []

    if work_years_total < 1:
        return CalcResult(
            result=0,
            breakdown={"reason": "工作不满1年，不享受带薪年休假"},
            basis=basis,
            steps=["工作不满1年，不享受法定带薪年休假"],
        )

    if work_years_total < 10:
        entitled_days = 5
    elif work_years_total < 20:
        entitled_days = 10
    else:
        entitled_days = 15

    steps.append(f"累计工作年限: {work_years_total}年 → 法定年休假天数: {entitled_days}天")

    actual_leave = min(total_leave_days, entitled_days)
    unused_days = entitled_days - used_leave_days
    unused_days = max(unused_days, 0)

    steps.append(f"应休年休假: {entitled_days}天, 已休: {used_leave_days}天, 未休: {unused_days}天")

    # 300% - 100% (已付) = 200% 额外补偿
    compensation = daily_wage * 2 * unused_days
    steps.append(f"未休年休假补偿 = 日工资({daily_wage:.2f}元) × 200% × 未休天数({unused_days}) = {compensation:.2f}元")
    steps.append(f"注: 正常工作期间已支付100%工资，此处为额外200%补偿")

    breakdown = {
        "daily_wage": daily_wage,
        "work_years_total": work_years_total,
        "entitled_days": entitled_days,
        "used_leave_days": used_leave_days,
        "unused_days": unused_days,
        "compensation_rate": 2.0,
        "total_compensation": compensation,
    }

    return CalcResult(result=round(compensation, 2), breakdown=breakdown, basis=basis, steps=steps)


def calculate_work_injury(
    *,
    monthly_salary: float,
    disability_level: int,  # 1-10级
    work_years: float = 0,
    medical_expenses: float = 0,
    is_resign: bool = False,
    city: str = "全国",
    has_rehabilitation_expenses: bool = False,
    rehabilitation_expenses: float = 0,
) -> CalcResult:
    """工伤赔偿计算

    一次性伤残补助金 (由工伤保险支付):
    - 1级: 27个月本人工资
    - 2级: 25个月
    - 3级: 23个月
    - 4级: 21个月
    - 5级: 18个月
    - 6级: 16个月
    - 7级: 13个月
    - 8级: 11个月
    - 9级: 9个月
    - 10级: 7个月

    1-4级保留劳动关系，按月发放伤残津贴
    5-6级保留劳动关系，适当安排工作，难以安排的按月发放伤残津贴
    7-10级劳动合同期满终止或职工本人提出解除的，支付一次性工伤医疗补助金和一次性伤残就业补助金
    """
    basis = [
        "《工伤保险条例》第35-37条: 职工因工致残被鉴定为一级至十级伤残的，享受相应待遇。",
    ]

    steps = []
    total = 0.0
    breakdown = {}

    social_avg = SOCIAL_AVERAGE_MONTHLY.get(city, SOCIAL_AVERAGE_MONTHLY["全国"])

    # 一次性伤残补助金月数
    disability_months = {
        1: 27, 2: 25, 3: 23, 4: 21, 5: 18, 6: 16,
        7: 13, 8: 11, 9: 9, 10: 7,
    }
    months = disability_months.get(disability_level, 0)

    # 本人工资低于社平60%的按60%算, 高于300%的按300%算
    base_salary = monthly_salary
    if monthly_salary < social_avg * 0.6:
        base_salary = social_avg * 0.6
        steps.append(f"本人工资({monthly_salary:.2f}) < 社平60%({social_avg * 0.6:.2f}), 按社平60%计算")
    elif monthly_salary > social_avg * 3:
        base_salary = social_avg * 3
        steps.append(f"本人工资({monthly_salary:.2f}) > 社平300%({social_avg * 3:.2f}), 按社平300%计算")

    disability_lump_sum = base_salary * months
    total += disability_lump_sum
    steps.append(f"一次性伤残补助金 = {base_salary:.2f}元/月 × {months}个月 = {disability_lump_sum:.2f}元")
    basis.append(f"《工伤保险条例》第35条: {disability_level}级伤残，一次性伤残补助金为{months}个月本人工资。")

    breakdown["disability_lump_sum"] = {
        "base_salary": base_salary,
        "months": months,
        "amount": disability_lump_sum,
    }

    # 伤残津贴 (1-6级)
    if disability_level <= 4:
        disability_rates = {1: 0.90, 2: 0.85, 3: 0.80, 4: 0.75}
        rate = disability_rates[disability_level]
        monthly_allowance = base_salary * rate
        steps.append(f"伤残津贴(按月) = {base_salary:.2f}元 × {rate*100:.0f}% = {monthly_allowance:.2f}元/月")
        breakdown["monthly_disability_allowance"] = {
            "rate": rate,
            "monthly_amount": monthly_allowance,
        }
        basis.append(f"《工伤保险条例》第35条: {disability_level}级伤残，伤残津贴为本人工资的{rate*100:.0f}%。")
    elif disability_level <= 6:
        disability_rates = {5: 0.70, 6: 0.60}
        rate = disability_rates[disability_level]
        monthly_allowance = base_salary * rate
        steps.append(f"伤残津贴(难以安排工作时按月) = {base_salary:.2f}元 × {rate*100:.0f}% = {monthly_allowance:.2f}元/月")
        breakdown["monthly_disability_allowance"] = {
            "rate": rate,
            "monthly_amount": monthly_allowance,
            "note": "难以安排工作时发放",
        }

    # 解除/终止时的一次性工伤医疗补助金和就业补助金 (5-10级)
    if is_resign and disability_level >= 5:
        # 一次性工伤医疗补助金 (各地标准不同，使用简化计算)
        medical_lump_sum = social_avg * (disability_level * 2)  # 简化公式
        total += medical_lump_sum
        steps.append(f"一次性工伤医疗补助金 ≈ 社平工资({social_avg}元) × {disability_level * 2}个月 = {medical_lump_sum:.2f}元")

        employment_lump_sum = social_avg * (disability_level * 1.5)  # 简化公式
        total += employment_lump_sum
        steps.append(f"一次性伤残就业补助金 ≈ 社平工资({social_avg}元) × {disability_level * 1.5}个月 = {employment_lump_sum:.2f}元")
        basis.append("《工伤保险条例》第36-37条: 经工伤职工本人提出解除劳动合同的，由工伤保险基金支付一次性工伤医疗补助金，由用人单位支付一次性伤残就业补助金。")

        breakdown["medical_lump_sum_on_resign"] = medical_lump_sum
        breakdown["employment_lump_sum_on_resign"] = employment_lump_sum

    # 医疗费用
    if medical_expenses > 0:
        total += medical_expenses
        steps.append(f"工伤医疗费用: {medical_expenses:.2f}元")
        breakdown["medical_expenses"] = medical_expenses
        basis.append("《工伤保险条例》第30条: 治疗工伤所需费用符合工伤保险诊疗项目目录、工伤保险药品目录、工伤保险住院服务标准的，从工伤保险基金支付。")

    if has_rehabilitation_expenses and rehabilitation_expenses > 0:
        total += rehabilitation_expenses
        steps.append(f"康复费用: {rehabilitation_expenses:.2f}元")
        breakdown["rehabilitation_expenses"] = rehabilitation_expenses

    steps.append(f"工伤赔偿合计: {total:.2f}元 (不含伤残津贴按月部分)")

    breakdown["monthly_salary"] = monthly_salary
    breakdown["disability_level"] = disability_level
    breakdown["social_average_salary"] = social_avg
    breakdown["city"] = city
    breakdown["is_resign"] = is_resign
    breakdown["total"] = total

    return CalcResult(result=round(total, 2), breakdown=breakdown, basis=basis, steps=steps)


def calculate(calc_type: str, params: dict) -> CalcResult:
    match calc_type:
        case "illegal_termination":
            return calculate_illegal_termination(
                monthly_salary=float(params["monthly_salary"]),
                work_years=float(params["work_years"]),
                city=params.get("city", "全国"),
                is_high_salary=params.get("is_high_salary", False),
            )
        case "overtime":
            monthly_salary = float(params.get("monthly_salary", 0))
            hourly_wage = monthly_salary / 21.75 / 8  # 月薪 / 21.75天 / 8小时
            return calculate_overtime(
                hourly_wage=hourly_wage,
                overtime_hours_workday=float(params.get("workday_hours", 0)),
                overtime_hours_weekend=float(params.get("weekend_hours", 0)),
                overtime_hours_holiday=float(params.get("holiday_hours", 0)),
            )
        case "annual_leave":
            monthly_salary = float(params.get("monthly_salary", 0))
            daily_wage = monthly_salary / 21.75
            return calculate_annual_leave(
                daily_wage=daily_wage,
                total_leave_days=float(params.get("total_leave_days", 0)),
                used_leave_days=float(params.get("used_leave_days", 0)),
                work_years_total=float(params.get("work_years_total", 0)),
            )
        case "work_injury":
            return calculate_work_injury(
                monthly_salary=float(params["monthly_salary"]),
                disability_level=int(params["disability_level"]),
                work_years=float(params.get("work_years", 0)),
                medical_expenses=float(params.get("medical_expenses", 0)),
                is_resign=params.get("is_resign", False),
                city=params.get("city", "全国"),
                has_rehabilitation_expenses=params.get("has_rehabilitation_expenses", False),
                rehabilitation_expenses=float(params.get("rehabilitation_expenses", 0)),
            )
        case _:
            raise ValueError(f"不支持的计算类型: {calc_type}")
