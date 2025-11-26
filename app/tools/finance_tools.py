"""
Finance Tools - LangChain tools for financial assistance
DISCLAIMER: For educational purposes only. Not financial advice.
"""

import json
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.data.finance_knowledge import (
    CONCEPTS_DB, INVESTMENTS_DB, BUDGET_CATEGORIES,
    RiskLevel, get_concept, get_investment_type,
    get_investments_by_risk, calculate_compound_interest,
    calculate_retirement_savings, calculate_loan_payment,
    get_budget_recommendation
)


DISCLAIMER = {
    "en": "DISCLAIMER: This is for educational purposes only and is not financial advice. Consult a qualified financial advisor for personalized guidance.",
    "ko": "면책조항: 이것은 교육 목적으로만 제공되며 재정 조언이 아닙니다. 개인화된 안내를 위해 자격을 갖춘 재정 상담사와 상담하세요.",
    "ja": "免責事項: これは教育目的のみであり、財務アドバイスではありません。個別のガイダンスについては、資格のあるファイナンシャルアドバイザーにご相談ください。"
}


class CompoundInterestInput(BaseModel):
    """Input for compound interest calculation."""
    principal: float = Field(description="Initial investment amount")
    annual_rate: float = Field(description="Annual interest rate as percentage (e.g., 7 for 7%)")
    years: int = Field(description="Number of years to invest")
    compounds_per_year: int = Field(default=12, description="Times interest compounds per year")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class CompoundInterestTool(BaseTool):
    """Tool for calculating compound interest."""
    name: str = "compound_interest_calculator"
    description: str = "Calculate compound interest growth over time"
    args_schema: type[BaseModel] = CompoundInterestInput

    def _run(
        self,
        principal: float,
        annual_rate: float,
        years: int,
        compounds_per_year: int = 12,
        lang: str = "en"
    ) -> str:
        if principal <= 0 or years <= 0:
            return json.dumps({"error": "Principal and years must be positive"})

        result = calculate_compound_interest(principal, annual_rate, years, compounds_per_year)
        result["disclaimer"] = DISCLAIMER.get(lang, DISCLAIMER["en"])

        return json.dumps(result, indent=2)


class RetirementCalculatorInput(BaseModel):
    """Input for retirement savings calculation."""
    current_age: int = Field(description="Current age")
    retirement_age: int = Field(default=65, description="Target retirement age")
    monthly_contribution: float = Field(description="Monthly contribution amount")
    current_savings: float = Field(default=0, description="Current retirement savings")
    annual_return: float = Field(default=7.0, description="Expected annual return percentage")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class RetirementCalculatorTool(BaseTool):
    """Tool for calculating retirement savings projections."""
    name: str = "retirement_calculator"
    description: str = "Calculate projected retirement savings based on contributions and time"
    args_schema: type[BaseModel] = RetirementCalculatorInput

    def _run(
        self,
        current_age: int,
        retirement_age: int = 65,
        monthly_contribution: float = 0,
        current_savings: float = 0,
        annual_return: float = 7.0,
        lang: str = "en"
    ) -> str:
        if current_age >= retirement_age:
            return json.dumps({"error": "Current age must be less than retirement age"})

        result = calculate_retirement_savings(
            current_age, retirement_age, monthly_contribution, current_savings, annual_return
        )
        result["disclaimer"] = DISCLAIMER.get(lang, DISCLAIMER["en"])

        return json.dumps(result, indent=2)


class LoanCalculatorInput(BaseModel):
    """Input for loan payment calculation."""
    principal: float = Field(description="Loan amount")
    annual_rate: float = Field(description="Annual interest rate as percentage")
    years: int = Field(description="Loan term in years")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class LoanCalculatorTool(BaseTool):
    """Tool for calculating loan payments."""
    name: str = "loan_calculator"
    description: str = "Calculate monthly loan payment and total interest"
    args_schema: type[BaseModel] = LoanCalculatorInput

    def _run(
        self,
        principal: float,
        annual_rate: float,
        years: int,
        lang: str = "en"
    ) -> str:
        if principal <= 0 or years <= 0:
            return json.dumps({"error": "Principal and years must be positive"})

        result = calculate_loan_payment(principal, annual_rate, years)
        result["disclaimer"] = DISCLAIMER.get(lang, DISCLAIMER["en"])

        return json.dumps(result, indent=2)


class BudgetPlannerInput(BaseModel):
    """Input for budget planning."""
    monthly_income: float = Field(description="Monthly income after taxes")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class BudgetPlannerTool(BaseTool):
    """Tool for creating budget recommendations."""
    name: str = "budget_planner"
    description: str = "Get budget recommendations based on income using 50/30/20 rule"
    args_schema: type[BaseModel] = BudgetPlannerInput

    def _run(self, monthly_income: float, lang: str = "en") -> str:
        if monthly_income <= 0:
            return json.dumps({"error": "Monthly income must be positive"})

        result = get_budget_recommendation(monthly_income)

        # Apply language to category names and tips
        for cat_id, cat_data in result["categories"].items():
            cat_data["name"] = cat_data["name"].get(lang, cat_data["name"].get("en"))
            cat_data["tips"] = cat_data["tips"].get(lang, cat_data["tips"].get("en"))

        result["disclaimer"] = DISCLAIMER.get(lang, DISCLAIMER["en"])

        return json.dumps(result, indent=2)


class InvestmentInfoInput(BaseModel):
    """Input for investment information."""
    investment_type: str = Field(description="Type of investment (stocks, bonds, index_funds, real_estate, savings_account)")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class InvestmentInfoTool(BaseTool):
    """Tool for getting investment type information."""
    name: str = "investment_info"
    description: str = "Get information about different investment types"
    args_schema: type[BaseModel] = InvestmentInfoInput

    def _run(self, investment_type: str, lang: str = "en") -> str:
        inv = get_investment_type(investment_type.lower().replace(" ", "_"))

        if not inv:
            available = list(INVESTMENTS_DB.keys())
            return json.dumps({
                "error": f"Investment type '{investment_type}' not found",
                "available_types": available
            }, indent=2)

        return json.dumps({
            "name": inv.name.get(lang, inv.name["en"]),
            "description": inv.description.get(lang, inv.description["en"]),
            "risk_level": inv.risk_level.value,
            "typical_returns": inv.typical_returns,
            "pros": inv.pros.get(lang, inv.pros["en"]),
            "cons": inv.cons.get(lang, inv.cons["en"]),
            "best_for": inv.best_for.get(lang, inv.best_for["en"]),
            "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["en"])
        }, indent=2)


class FinancialConceptInput(BaseModel):
    """Input for financial concept information."""
    concept: str = Field(description="Financial concept to learn about")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class FinancialConceptTool(BaseTool):
    """Tool for getting financial concept information."""
    name: str = "financial_concept"
    description: str = "Learn about financial concepts like compound interest, diversification, etc."
    args_schema: type[BaseModel] = FinancialConceptInput

    def _run(self, concept: str, lang: str = "en") -> str:
        concept_key = concept.lower().replace(" ", "_")
        info = get_concept(concept_key)

        if not info:
            # Try partial match
            for key, val in CONCEPTS_DB.items():
                if concept.lower() in key or concept.lower() in val.name.get("en", "").lower():
                    info = val
                    break

        if not info:
            available = list(CONCEPTS_DB.keys())
            return json.dumps({
                "error": f"Concept '{concept}' not found",
                "available_concepts": available
            }, indent=2)

        return json.dumps({
            "name": info.name.get(lang, info.name["en"]),
            "description": info.description.get(lang, info.description["en"]),
            "key_points": info.key_points.get(lang, info.key_points["en"]),
            "tips": info.tips.get(lang, info.tips["en"]),
            "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["en"])
        }, indent=2)


class EmergencyFundCalculatorInput(BaseModel):
    """Input for emergency fund calculation."""
    monthly_expenses: float = Field(description="Total monthly expenses")
    months: int = Field(default=6, description="Number of months to cover (3-12 recommended)")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class EmergencyFundCalculatorTool(BaseTool):
    """Tool for calculating emergency fund needs."""
    name: str = "emergency_fund_calculator"
    description: str = "Calculate how much you need in your emergency fund"
    args_schema: type[BaseModel] = EmergencyFundCalculatorInput

    def _run(
        self,
        monthly_expenses: float,
        months: int = 6,
        lang: str = "en"
    ) -> str:
        if monthly_expenses <= 0:
            return json.dumps({"error": "Monthly expenses must be positive"})

        target = monthly_expenses * months

        messages = {
            "en": {
                "target_label": "Target Emergency Fund",
                "months_label": "Months of Coverage",
                "monthly_label": "Monthly Expenses",
                "tip": "Start with 1 month, then build to 3-6 months over time"
            },
            "ko": {
                "target_label": "목표 비상 자금",
                "months_label": "보장 개월 수",
                "monthly_label": "월별 지출",
                "tip": "1개월치부터 시작하여 시간이 지남에 따라 3-6개월치로 늘리세요"
            },
            "ja": {
                "target_label": "目標緊急資金",
                "months_label": "カバー月数",
                "monthly_label": "月間支出",
                "tip": "1ヶ月分から始めて、徐々に3〜6ヶ月分まで増やしましょう"
            }
        }

        msg = messages.get(lang, messages["en"])

        return json.dumps({
            msg["target_label"]: round(target, 2),
            msg["months_label"]: months,
            msg["monthly_label"]: monthly_expenses,
            "tip": msg["tip"],
            "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["en"])
        }, indent=2)


class DebtPayoffInput(BaseModel):
    """Input for debt payoff calculation."""
    total_debt: float = Field(description="Total debt amount")
    interest_rate: float = Field(description="Average interest rate as percentage")
    monthly_payment: float = Field(description="Monthly payment amount")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class DebtPayoffTool(BaseTool):
    """Tool for calculating debt payoff timeline."""
    name: str = "debt_payoff_calculator"
    description: str = "Calculate how long it will take to pay off debt"
    args_schema: type[BaseModel] = DebtPayoffInput

    def _run(
        self,
        total_debt: float,
        interest_rate: float,
        monthly_payment: float,
        lang: str = "en"
    ) -> str:
        if total_debt <= 0 or monthly_payment <= 0:
            return json.dumps({"error": "Debt and payment must be positive"})

        monthly_rate = interest_rate / 100 / 12

        # Check if payment covers interest
        min_payment = total_debt * monthly_rate
        if monthly_payment <= min_payment:
            messages = {
                "en": "Payment too low to cover interest. Increase monthly payment.",
                "ko": "이자를 충당하기에 월 납입금이 너무 낮습니다. 월 납입금을 늘리세요.",
                "ja": "支払額が利息をカバーするには低すぎます。毎月の支払額を増やしてください。"
            }
            return json.dumps({
                "error": messages.get(lang, messages["en"]),
                "minimum_payment": round(min_payment + 1, 2)
            }, indent=2)

        # Calculate months to payoff
        if monthly_rate > 0:
            months = -1 * (
                (1 / (1 + monthly_rate)) *
                (1 / (monthly_rate)) *
                (total_debt * monthly_rate - monthly_payment) /
                monthly_payment
            )
            import math
            months = math.ceil(math.log(monthly_payment / (monthly_payment - total_debt * monthly_rate)) /
                             math.log(1 + monthly_rate))
        else:
            months = math.ceil(total_debt / monthly_payment)

        years = months // 12
        remaining_months = months % 12
        total_paid = monthly_payment * months
        total_interest = total_paid - total_debt

        labels = {
            "en": {"months": "Months to Payoff", "years": "Years", "total": "Total Paid", "interest": "Total Interest"},
            "ko": {"months": "상환 개월 수", "years": "년", "total": "총 납입금", "interest": "총 이자"},
            "ja": {"months": "返済月数", "years": "年", "total": "総支払額", "interest": "総利息"}
        }
        lbl = labels.get(lang, labels["en"])

        return json.dumps({
            lbl["months"]: months,
            "time": f"{years} {lbl['years']}, {remaining_months} months" if years > 0 else f"{months} months",
            lbl["total"]: round(total_paid, 2),
            lbl["interest"]: round(total_interest, 2),
            "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["en"])
        }, indent=2)


class SavingsGoalInput(BaseModel):
    """Input for savings goal calculation."""
    goal_amount: float = Field(description="Target savings amount")
    months: int = Field(description="Number of months to reach goal")
    current_savings: float = Field(default=0, description="Current savings amount")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class SavingsGoalTool(BaseTool):
    """Tool for calculating savings goals."""
    name: str = "savings_goal_calculator"
    description: str = "Calculate monthly savings needed to reach a goal"
    args_schema: type[BaseModel] = SavingsGoalInput

    def _run(
        self,
        goal_amount: float,
        months: int,
        current_savings: float = 0,
        lang: str = "en"
    ) -> str:
        if goal_amount <= 0 or months <= 0:
            return json.dumps({"error": "Goal and months must be positive"})

        remaining = goal_amount - current_savings
        monthly_needed = remaining / months if months > 0 else remaining
        weekly_needed = monthly_needed / 4

        labels = {
            "en": {
                "goal": "Savings Goal",
                "current": "Current Savings",
                "remaining": "Amount Needed",
                "monthly": "Monthly Savings Needed",
                "weekly": "Weekly Savings Needed",
                "months": "Months to Goal"
            },
            "ko": {
                "goal": "저축 목표",
                "current": "현재 저축",
                "remaining": "필요 금액",
                "monthly": "월 필요 저축액",
                "weekly": "주 필요 저축액",
                "months": "목표까지 개월 수"
            },
            "ja": {
                "goal": "貯蓄目標",
                "current": "現在の貯蓄",
                "remaining": "必要額",
                "monthly": "必要な月間貯蓄額",
                "weekly": "必要な週間貯蓄額",
                "months": "目標までの月数"
            }
        }
        lbl = labels.get(lang, labels["en"])

        return json.dumps({
            lbl["goal"]: goal_amount,
            lbl["current"]: current_savings,
            lbl["remaining"]: round(remaining, 2),
            lbl["monthly"]: round(monthly_needed, 2),
            lbl["weekly"]: round(weekly_needed, 2),
            lbl["months"]: months,
            "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["en"])
        }, indent=2)


def get_finance_tools() -> List[BaseTool]:
    """Get all finance assistant tools."""
    return [
        CompoundInterestTool(),
        RetirementCalculatorTool(),
        LoanCalculatorTool(),
        BudgetPlannerTool(),
        InvestmentInfoTool(),
        FinancialConceptTool(),
        EmergencyFundCalculatorTool(),
        DebtPayoffTool(),
        SavingsGoalTool(),
    ]
