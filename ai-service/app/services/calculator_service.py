"""
赔偿计算器服务
"""
import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


@dataclass
class CalculationResult:
    """计算结果"""
    item: str
    description: str
    amount: float
    formula: str
    legal_basis: str


class CompensationCalculator:
    """赔偿计算器"""

    # 2023年各城市社平工资（示例数据）
    SOCIAL_AVERAGE_SALARY = {
        "上海": 12183,
        "北京": 11297,
        "深圳": 11620,
        "广州": 10308,
        "杭州": 10292,
        "南京": 9428,
        "苏州": 9461,
        "成都": 7988,
        "武汉": 7884,
        "西安": 7259,
    }

    @staticmethod
    def calculate_illegal_termination(
            entry_date: str,
            leave_date: str,
            monthly_salary: float,
            average_salary_12m: float = None,
            city: str = None,
            high_salary_cap: bool = False,
            is_negotiated: bool = False
    ) -> Dict[str, Any]:
        """
        计算违法解除劳动合同赔偿金

        Args:
            entry_date: 入职日期 (YYYY-MM-DD)
            leave_date: 解除日期 (YYYY-MM-DD)
            monthly_salary: 月工资
            average_salary_12m: 12个月平均工资
            city: 城市
            high_salary_cap: 是否适用高薪封顶
            is_negotiated: 是否协商解除

        Returns:
            计算结果
        """
        # 解析日期
        entry = datetime.strptime(entry_date, "%Y-%m-%d").date()
        leave = datetime.strptime(leave_date, "%Y-%m-%d").date()

        # 计算工作年限
        years = (leave - entry).days / 365.25
        years_int = int(years)
        months_remainder = (years - years_int) * 12

        # 工作年限取整规则：不满6个月按0.5年，满6个月按1年
        if months_remainder >= 6:
            work_years = years_int + 1
        else:
            work_years = years_int + 0.5 if months_remainder > 0 else years_int

        # 使用12个月平均工资或月工资
        avg_salary = average_salary_12m or monthly_salary

        # 判断是否适用高薪封顶
        city_avg_salary = CompensationCalculator.SOCIAL_AVERAGE_SALARY.get(city, 8000) if city else 8000
        cap_salary = city_avg_salary * 3

        actual_salary = avg_salary
        capped = False
        if high_salary_cap and avg_salary > cap_salary:
            actual_salary = cap_salary
            capped = True

        # 计算经济补偿金
        # 协商解除：N年 × 月工资
        # 违法解除：2N年 × 月工资
        if is_negotiated:
            compensation = work_years * actual_salary
            compensation_years = work_years
            compensation_type = "经济补偿金"
            multiplier = 1
        else:
            compensation = work_years * actual_salary * 2
            compensation_years = work_years * 2
            compensation_type = "赔偿金"
            multiplier = 2

        # 封顶年限（高薪情况下最多12年）
        capped_years = False
        if capped and work_years > 12:
            if is_negotiated:
                compensation = 12 * cap_salary
            else:
                compensation = 12 * cap_salary * 2
            capped_years = True

        # 构建详细计算步骤
        calculations = []

        # 1. 工作年限计算
        calculations.append(CalculationResult(
            item="工作年限",
            description=f"入职日期{entry_date}至解除日期{leave_date}",
            amount=work_years,
            formula=f"{entry_date} ~ {leave_date} = {years:.2f}年 → {work_years}年",
            legal_basis="《劳动合同法》第47条"
        ))

        # 2. 工资标准
        calculations.append(CalculationResult(
            item="月工资标准",
            description="解除前12个月平均工资" if average_salary_12m else "月工资",
            amount=actual_salary,
            formula=f"{'12个月平均工资' if average_salary_12m else '月工资'} = {actual_salary:.2f}元",
            legal_basis="《劳动合同法》第47条"
        ))

        # 3. 高薪封顶
        if capped:
            calculations.append(CalculationResult(
                item="工资封顶",
                description=f"工资超过社平工资3倍，按{city}社平工资3倍计算",
                amount=cap_salary,
                formula=f"{city}社平工资{city_avg_salary}元 × 3 = {cap_salary:.2f}元",
                legal_basis="《劳动合同法》第47条"
            ))

        # 4. 计算
        calculations.append(CalculationResult(
            item=compensation_type,
            description="违法解除赔偿金" if not is_negotiated else "协商解除经济补偿金",
            amount=compensation,
            formula=f"{work_years}年 × {actual_salary:.2f}元" + (f" × 2 = {compensation:.2f}元" if not is_negotiated else f" = {compensation:.2f}元"),
            legal_basis="《劳动合同法》第87条" if not is_negotiated else "《劳动合同法》第46条"
        ))

        return {
            "total_amount": round(compensation, 2),
            "work_years": work_years,
            "monthly_salary": monthly_salary,
            "average_salary": avg_salary,
            "actual_salary": actual_salary,
            "is_capped": capped,
            "cap_salary": cap_salary if capped else None,
            "city_average_salary": city_avg_salary if city else None,
            "compensation_type": compensation_type,
            "multiplier": multiplier,
            "calculations": [
                {
                    "item": c.item,
                    "description": c.description,
                    "amount": c.amount,
                    "formula": c.formula,
                    "legal_basis": c.legal_basis
                }
                for c in calculations
            ],
            "legal_basis": [
                {"law": "《劳动合同法》第47条", "content": "经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。"},
                {"law": "《劳动合同法》第48条", "content": "用人单位违反本法规定解除或者终止劳动合同...应当依照本法第八十七条规定支付赔偿金。"},
                {"law": "《劳动合同法》第87条", "content": "用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。"}
            ]
        }

    @staticmethod
    def calculate_overtime(
            monthly_salary: float,
            workday_hours: float = 0,
            weekend_hours: float = 0,
            holiday_hours: float = 0,
            work_days_per_month: float = 21.75
    ) -> Dict[str, Any]:
        """
        计算加班费

        Args:
            monthly_salary: 月工资
            workday_hours: 工作日加班小时数
            weekend_hours: 休息日加班小时数
            holiday_hours: 法定节假日加班小时数
            work_days_per_month: 每月工作天数

        Returns:
            计算结果
        """
        # 计算小时工资
        hourly_rate = monthly_salary / work_days_per_month / 8

        # 各类加班费
        workday_pay = workday_hours * hourly_rate * 1.5
        weekend_pay = weekend_hours * hourly_rate * 2.0
        holiday_pay = holiday_hours * hourly_rate * 3.0

        total_overtime_pay = workday_pay + weekend_pay + holiday_pay

        calculations = [
            CalculationResult(
                item="小时工资",
                description="月工资÷21.75÷8",
                amount=round(hourly_rate, 2),
                formula=f"{monthly_salary}元 ÷ {work_days_per_month}天 ÷ 8小时 = {hourly_rate:.2f}元/小时",
                legal_basis="《劳动法》第44条"
            ),
            CalculationResult(
                item="工作日加班费",
                description="小时工资×1.5×加班小时",
                amount=round(workday_pay, 2),
                formula=f"{hourly_rate:.2f}元 × 1.5 × {workday_hours}小时 = {workday_pay:.2f}元",
                legal_basis="《劳动法》第44条"
            ),
            CalculationResult(
                item="休息日加班费",
                description="小时工资×2×加班小时",
                amount=round(weekend_pay, 2),
                formula=f"{hourly_rate:.2f}元 × 2 × {weekend_hours}小时 = {weekend_pay:.2f}元",
                legal_basis="《劳动法》第44条"
            ),
            CalculationResult(
                item="法定节假日加班费",
                description="小时工资×3×加班小时",
                amount=round(holiday_pay, 2),
                formula=f"{hourly_rate:.2f}元 × 3 × {holiday_hours}小时 = {holiday_pay:.2f}元",
                legal_basis="《劳动法》第44条"
            )
        ]

        return {
            "total_amount": round(total_overtime_pay, 2),
            "hourly_rate": round(hourly_rate, 2),
            "workday_overtime": {
                "hours": workday_hours,
                "rate": 1.5,
                "pay": round(workday_pay, 2)
            },
            "weekend_overtime": {
                "hours": weekend_hours,
                "rate": 2.0,
                "pay": round(weekend_pay, 2)
            },
            "holiday_overtime": {
                "hours": holiday_hours,
                "rate": 3.0,
                "pay": round(holiday_pay, 2)
            },
            "calculations": [
                {
                    "item": c.item,
                    "description": c.description,
                    "amount": c.amount,
                    "formula": c.formula,
                    "legal_basis": c.legal_basis
                }
                for c in calculations
            ],
            "legal_basis": [
                {"law": "《劳动法》第44条", "content": "有下列情形之一的，用人单位应当按照下列标准支付高于劳动者正常工作时间工资的工资报酬：(一)安排劳动者延长工作时间的，支付不低于工资的百分之一百五十的工资报酬；(二)休息日安排劳动者工作又不能安排补休的，支付不低于工资的百分之二百的工资报酬；(三)法定休假日安排劳动者工作的，支付不低于工资的百分之三百的工资报酬。"}
            ]
        }

    @staticmethod
    def calculate_annual_leave(
            monthly_salary: float,
            total_work_years: float,
            unused_days: float,
            work_days_per_month: float = 21.75
    ) -> Dict[str, Any]:
        """
        计算未休年休假工资

        Args:
            monthly_salary: 月工资
            total_work_years: 累计工作年限
            unused_days: 未休年休假天数
            work_days_per_month: 每月工作天数

        Returns:
            计算结果
        """
        # 计算日工资
        daily_rate = monthly_salary / work_days_per_month

        # 未休年休假工资 = 日工资 × 未休天数 × 300%
        # 其中100%是正常工资，额外支付200%
        annual_leave_pay = daily_rate * unused_days * 3

        # 确定应休年休假天数
        if total_work_years < 1:
            entitled_days = 0
            note = "工作不满1年，无法定年休假"
        elif total_work_years < 10:
            entitled_days = 5
            note = "累计工作满1年不满10年，年休假5天"
        elif total_work_years < 20:
            entitled_days = 10
            note = "累计工作满10年不满20年，年休假10天"
        else:
            entitled_days = 15
            note = "累计工作满20年，年休假15天"

        calculations = [
            CalculationResult(
                item="日工资",
                description="月工资÷21.75",
                amount=round(daily_rate, 2),
                formula=f"{monthly_salary}元 ÷ {work_days_per_month}天 = {daily_rate:.2f}元/天",
                legal_basis="《企业职工带薪年休假实施办法》第10条"
            ),
            CalculationResult(
                item="应休年休假",
                description=note,
                amount=entitled_days,
                formula=f"累计工作年限{total_work_years}年",
                legal_basis="《职工带薪年休假条例》第3条"
            ),
            CalculationResult(
                item="未休年休假工资",
                description="日工资×未休天数×300%",
                amount=round(annual_leave_pay, 2),
                formula=f"{daily_rate:.2f}元 × {unused_days}天 × 300% = {annual_leave_pay:.2f}元",
                legal_basis="《企业职工带薪年休假实施办法》第10条"
            )
        ]

        return {
            "total_amount": round(annual_leave_pay, 2),
            "daily_rate": round(daily_rate, 2),
            "total_work_years": total_work_years,
            "entitled_days": entitled_days,
            "unused_days": unused_days,
            "calculations": [
                {
                    "item": c.item,
                    "description": c.description,
                    "amount": c.amount,
                    "formula": c.formula,
                    "legal_basis": c.legal_basis
                }
                for c in calculations
            ],
            "legal_basis": [
                {"law": "《职工带薪年休假条例》第3条", "content": "职工累计工作已满1年不满10年的，年休假5天；已满10年不满20年的，年休假10天；已满20年的，年休假15天。"},
                {"law": "《企业职工带薪年休假实施办法》第10条", "content": "用人单位经职工同意不安排年休假或者安排职工年休假天数少于应休年休假天数，应当对本年度应休未休年休假天数，按照其日工资收入的300%支付未休年休假工资报酬。"}
            ]
        }
