"""
Finance Tools - LangChain tools for personal finance education.

DISCLAIMER: For educational purposes only. NOT financial advice.
"""

from __future__ import annotations

import json
import math

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.data.finance_knowledge import (
    BUDGET_CATEGORIES,
    CONCEPTS_DB,
    INVESTMENTS_DB,
    calculate_compound_interest,
    calculate_loan_payment,
    calculate_retirement_savings,
    get_budget_recommendation,
    get_concept,
    get_investment_type,
)

# i18n-aware disclaimer. Always append to any response that touches a specific
# recommendation involving money so that users are reminded this is general
# education, not personalised financial advice.
DISCLAIMER: dict[str, str] = {
    "en": (
        "DISCLAIMER: This is for educational purposes only and is NOT financial advice. "
        "Consult a licensed financial advisor for personalised guidance."
    ),
    "ko": (
        "면책조항: 이것은 교육 목적으로만 제공되며 재정 조언이 아닙니다. "
        "개인화된 안내를 위해 자격을 갖춘 재정 상담사와 상담하세요."
    ),
    "ja": (
        "免責事項: これは教育目的のみであり、財務アドバイスではありません。"
        "個別のガイダンスについては、資格のあるファイナンシャルアドバイザーにご相談ください。"
    ),
}


def _disclaimer(lang: str) -> str:
    return DISCLAIMER.get(lang, DISCLAIMER["en"])


# ---------------------------------------------------------------------------
# Budget planner
# ---------------------------------------------------------------------------


class BudgetPlannerInput(BaseModel):
    """Input for the 50/30/20 budget planner."""

    monthly_income: float = Field(description="Monthly income after taxes")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class BudgetPlannerTool(BaseTool):
    """Generate a category budget for a monthly income."""

    name: str = "budget_planner"
    description: str = (
        "Get budget recommendations based on monthly income using the 50/30/20 rule "
        "and category breakdowns."
    )
    args_schema: type[BaseModel] = BudgetPlannerInput

    def _run(self, monthly_income: float, lang: str = "en") -> str:
        if monthly_income <= 0:
            return json.dumps({"error": "Monthly income must be positive"})

        result = get_budget_recommendation(monthly_income)

        for _cat_id, cat_data in result["categories"].items():
            cat_data["name"] = cat_data["name"].get(lang, cat_data["name"].get("en"))
            cat_data["tips"] = cat_data["tips"].get(lang, cat_data["tips"].get("en"))

        result["disclaimer"] = _disclaimer(lang)
        return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Compound interest
# ---------------------------------------------------------------------------


class CompoundInterestInput(BaseModel):
    """Input for compound interest calculation."""

    principal: float = Field(description="Initial investment amount")
    annual_rate: float = Field(description="Annual interest rate as percentage (e.g., 7 for 7%)")
    years: int = Field(description="Number of years to invest")
    compounds_per_year: int = Field(default=12, description="Times interest compounds per year")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class CompoundInterestTool(BaseTool):
    """Calculate compound interest growth."""

    name: str = "compound_interest_calculator"
    description: str = "Calculate compound interest growth over time."
    args_schema: type[BaseModel] = CompoundInterestInput

    def _run(
        self,
        principal: float,
        annual_rate: float,
        years: int,
        compounds_per_year: int = 12,
        lang: str = "en",
    ) -> str:
        if principal <= 0 or years <= 0:
            return json.dumps({"error": "Principal and years must be positive"})

        result = calculate_compound_interest(principal, annual_rate, years, compounds_per_year)
        result["disclaimer"] = _disclaimer(lang)
        return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Retirement projection
# ---------------------------------------------------------------------------


class RetirementCalcInput(BaseModel):
    """Input for retirement savings projection."""

    current_age: int = Field(description="Current age")
    retirement_age: int = Field(default=65, description="Target retirement age")
    monthly_contribution: float = Field(description="Monthly contribution amount")
    current_savings: float = Field(default=0, description="Current retirement savings")
    annual_return: float = Field(default=7.0, description="Expected annual return percentage")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class RetirementCalcTool(BaseTool):
    """Project retirement savings."""

    name: str = "retirement_calculator"
    description: str = "Project retirement savings based on contributions, time horizon, and return."
    args_schema: type[BaseModel] = RetirementCalcInput

    def _run(
        self,
        current_age: int,
        retirement_age: int = 65,
        monthly_contribution: float = 0,
        current_savings: float = 0,
        annual_return: float = 7.0,
        lang: str = "en",
    ) -> str:
        if current_age >= retirement_age:
            return json.dumps({"error": "Current age must be less than retirement age"})

        result = calculate_retirement_savings(
            current_age,
            retirement_age,
            monthly_contribution,
            current_savings,
            annual_return,
        )
        result["disclaimer"] = _disclaimer(lang)
        return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Investment education
# ---------------------------------------------------------------------------


class InvestmentEducationInput(BaseModel):
    """Input for investment education lookups."""

    investment_type: str = Field(
        description="Type of investment (stocks, bonds, index_funds, real_estate, savings_account)"
    )
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class InvestmentEducationTool(BaseTool):
    """Educational explainer for an investment type."""

    name: str = "investment_education"
    description: str = (
        "Look up educational information about investment types: stocks, bonds, index funds, "
        "real estate, high-yield savings."
    )
    args_schema: type[BaseModel] = InvestmentEducationInput

    def _run(self, investment_type: str, lang: str = "en") -> str:
        key = investment_type.lower().replace(" ", "_")
        inv = get_investment_type(key)

        if not inv:
            return json.dumps(
                {
                    "error": f"Investment type '{investment_type}' not found",
                    "available_types": list(INVESTMENTS_DB.keys()),
                    "disclaimer": _disclaimer(lang),
                },
                indent=2,
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "name": inv.name.get(lang, inv.name["en"]),
                "description": inv.description.get(lang, inv.description["en"]),
                "risk_level": inv.risk_level.value,
                "typical_returns": inv.typical_returns,
                "pros": inv.pros.get(lang, inv.pros["en"]),
                "cons": inv.cons.get(lang, inv.cons["en"]),
                "best_for": inv.best_for.get(lang, inv.best_for["en"]),
                "disclaimer": _disclaimer(lang),
            },
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Concept lookup
# ---------------------------------------------------------------------------


class FinancialConceptInput(BaseModel):
    """Input for financial concept lookups."""

    concept: str = Field(description="Financial concept to learn about")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class FinancialConceptTool(BaseTool):
    """Explainer for a financial concept (compound interest, diversification, etc.)."""

    name: str = "financial_concept"
    description: str = (
        "Learn about financial concepts: compound_interest, diversification, "
        "emergency_fund, debt_management, budgeting, retirement_planning."
    )
    args_schema: type[BaseModel] = FinancialConceptInput

    def _run(self, concept: str, lang: str = "en") -> str:
        key = concept.lower().replace(" ", "_")
        info = get_concept(key)

        if not info:
            # Partial / substring match
            for db_key, val in CONCEPTS_DB.items():
                if concept.lower() in db_key or concept.lower() in val.name.get("en", "").lower():
                    info = val
                    break

        if not info:
            return json.dumps(
                {
                    "error": f"Concept '{concept}' not found",
                    "available_concepts": list(CONCEPTS_DB.keys()),
                    "disclaimer": _disclaimer(lang),
                },
                indent=2,
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "name": info.name.get(lang, info.name["en"]),
                "description": info.description.get(lang, info.description["en"]),
                "key_points": info.key_points.get(lang, info.key_points["en"]),
                "tips": info.tips.get(lang, info.tips["en"]),
                "disclaimer": _disclaimer(lang),
            },
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Debt payoff
# ---------------------------------------------------------------------------


class DebtPayoffInput(BaseModel):
    """Input for debt payoff projection."""

    total_debt: float = Field(description="Total debt amount")
    interest_rate: float = Field(description="Average annual interest rate as percentage")
    monthly_payment: float = Field(description="Planned monthly payment")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class DebtPayoffTool(BaseTool):
    """Project months/total interest to pay off a debt."""

    name: str = "debt_payoff_calculator"
    description: str = (
        "Estimate how long it will take to pay off a debt given a fixed monthly payment, "
        "and the total interest paid."
    )
    args_schema: type[BaseModel] = DebtPayoffInput

    def _run(
        self,
        total_debt: float,
        interest_rate: float,
        monthly_payment: float,
        lang: str = "en",
    ) -> str:
        if total_debt <= 0 or monthly_payment <= 0:
            return json.dumps({"error": "Debt and payment must be positive"})

        monthly_rate = interest_rate / 100 / 12

        min_payment = total_debt * monthly_rate
        if monthly_rate > 0 and monthly_payment <= min_payment:
            messages = {
                "en": "Payment too low to cover interest. Increase the monthly payment.",
                "ko": "이자를 충당하기에 월 납입금이 너무 낮습니다. 월 납입금을 늘리세요.",
                "ja": "支払額が利息をカバーするには低すぎます。毎月の支払額を増やしてください。",
            }
            return json.dumps(
                {
                    "error": messages.get(lang, messages["en"]),
                    "minimum_payment_to_cover_interest": round(min_payment + 1, 2),
                    "disclaimer": _disclaimer(lang),
                },
                indent=2,
                ensure_ascii=False,
            )

        if monthly_rate > 0:
            months = math.ceil(
                math.log(monthly_payment / (monthly_payment - total_debt * monthly_rate))
                / math.log(1 + monthly_rate)
            )
        else:
            months = math.ceil(total_debt / monthly_payment)

        years = months // 12
        remaining_months = months % 12
        total_paid = monthly_payment * months
        total_interest = total_paid - total_debt

        return json.dumps(
            {
                "months_to_payoff": months,
                "human_time": (
                    f"{years} year(s), {remaining_months} month(s)" if years > 0 else f"{months} month(s)"
                ),
                "total_paid": round(total_paid, 2),
                "total_interest": round(total_interest, 2),
                "disclaimer": _disclaimer(lang),
            },
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Emergency fund
# ---------------------------------------------------------------------------


class EmergencyFundInput(BaseModel):
    """Input for emergency fund target calculation."""

    monthly_expenses: float = Field(description="Total monthly expenses")
    months: int = Field(default=6, description="Number of months to cover (3-12 recommended)")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class EmergencyFundTool(BaseTool):
    """Calculate an emergency fund target."""

    name: str = "emergency_fund_calculator"
    description: str = "Calculate how much you should keep in an emergency fund."
    args_schema: type[BaseModel] = EmergencyFundInput

    def _run(self, monthly_expenses: float, months: int = 6, lang: str = "en") -> str:
        if monthly_expenses <= 0 or months <= 0:
            return json.dumps({"error": "Monthly expenses and months must be positive"})

        target = monthly_expenses * months
        tip = {
            "en": "Start with 1 month, then build to 3-6 months of expenses over time.",
            "ko": "1개월치부터 시작하여 시간이 지남에 따라 3-6개월치로 늘리세요.",
            "ja": "1ヶ月分から始めて、徐々に3〜6ヶ月分まで増やしましょう。",
        }
        return json.dumps(
            {
                "target_emergency_fund": round(target, 2),
                "months_of_coverage": months,
                "monthly_expenses": monthly_expenses,
                "tip": tip.get(lang, tip["en"]),
                "disclaimer": _disclaimer(lang),
            },
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Loan calculator
# ---------------------------------------------------------------------------


class LoanCalculatorInput(BaseModel):
    """Input for loan payment calculation."""

    principal: float = Field(description="Loan amount")
    annual_rate: float = Field(description="Annual interest rate as percentage")
    years: int = Field(description="Loan term in years")
    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class LoanCalculatorTool(BaseTool):
    """Calculate the monthly payment and total interest for a loan."""

    name: str = "loan_calculator"
    description: str = "Calculate the monthly loan payment and total interest for a fixed-rate loan."
    args_schema: type[BaseModel] = LoanCalculatorInput

    def _run(self, principal: float, annual_rate: float, years: int, lang: str = "en") -> str:
        if principal <= 0 or years <= 0:
            return json.dumps({"error": "Principal and years must be positive"})

        result = calculate_loan_payment(principal, annual_rate, years)
        result["disclaimer"] = _disclaimer(lang)
        return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Budget categories overview (educational, no input math)
# ---------------------------------------------------------------------------


class BudgetCategoriesOverviewInput(BaseModel):
    """Input for budget categories overview."""

    lang: str = Field(default="en", description="Language code (en, ko, ja)")


class BudgetCategoriesOverviewTool(BaseTool):
    """List recommended budget category percentages and tips."""

    name: str = "budget_categories_overview"
    description: str = (
        "List recommended household budget categories with target percentages "
        "(Housing, Transportation, Food, Savings, Insurance, Entertainment)."
    )
    args_schema: type[BaseModel] = BudgetCategoriesOverviewInput

    def _run(self, lang: str = "en") -> str:
        categories = [
            {
                "id": cat.id,
                "name": cat.name.get(lang, cat.name["en"]),
                "description": cat.description.get(lang, cat.description["en"]),
                "recommended_percent": cat.recommended_percent,
                "tips": cat.tips.get(lang, cat.tips["en"]),
            }
            for cat in BUDGET_CATEGORIES
        ]
        return json.dumps(
            {"categories": categories, "disclaimer": _disclaimer(lang)},
            indent=2,
            ensure_ascii=False,
        )


def get_finance_tools() -> list[BaseTool]:
    """Return the canonical set of finance tools for the agent."""
    return [
        BudgetPlannerTool(),
        CompoundInterestTool(),
        RetirementCalcTool(),
        InvestmentEducationTool(),
        DebtPayoffTool(),
        EmergencyFundTool(),
        LoanCalculatorTool(),
        FinancialConceptTool(),
        BudgetCategoriesOverviewTool(),
    ]
