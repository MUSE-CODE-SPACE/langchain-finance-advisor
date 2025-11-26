"""
Finance Agent - LangChain agent for personal finance assistance
DISCLAIMER: For educational purposes only. Not financial advice.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

from app.tools.finance_tools import get_finance_tools, DISCLAIMER
from app.data.finance_knowledge import (
    CONCEPTS_DB, INVESTMENTS_DB, BUDGET_CATEGORIES,
    calculate_compound_interest, calculate_retirement_savings,
    calculate_loan_payment, get_budget_recommendation,
    RiskLevel
)


# i18n Messages
MESSAGES = {
    "en": {
        "welcome": "Personal Finance Advisor",
        "welcome_desc": "I can help you with financial education and planning.",
        "disclaimer": "DISCLAIMER: This is for educational purposes only. Not financial advice.",
        "features": {
            "budget": "Budget Planning",
            "savings": "Savings Goals",
            "retirement": "Retirement Calculator",
            "investment": "Investment Education",
            "debt": "Debt Management",
            "emergency": "Emergency Fund"
        },
        "ask": "What would you like to learn about?",
        "not_found": "I couldn't find specific information about that.",
        "try_asking": "Try asking about"
    },
    "ko": {
        "welcome": "개인 금융 어드바이저",
        "welcome_desc": "금융 교육 및 계획을 도와드립니다.",
        "disclaimer": "면책조항: 이것은 교육 목적으로만 제공됩니다. 재정 조언이 아닙니다.",
        "features": {
            "budget": "예산 계획",
            "savings": "저축 목표",
            "retirement": "은퇴 계산기",
            "investment": "투자 교육",
            "debt": "부채 관리",
            "emergency": "비상 자금"
        },
        "ask": "무엇에 대해 알고 싶으신가요?",
        "not_found": "해당 정보를 찾을 수 없습니다.",
        "try_asking": "다음에 대해 물어보세요"
    },
    "ja": {
        "welcome": "パーソナルファイナンスアドバイザー",
        "welcome_desc": "金融教育と計画をお手伝いします。",
        "disclaimer": "免責事項: これは教育目的のみです。財務アドバイスではありません。",
        "features": {
            "budget": "予算計画",
            "savings": "貯蓄目標",
            "retirement": "退職計算機",
            "investment": "投資教育",
            "debt": "債務管理",
            "emergency": "緊急資金"
        },
        "ask": "何について知りたいですか？",
        "not_found": "その情報は見つかりませんでした。",
        "try_asking": "次について質問してみてください"
    }
}


@dataclass
class FinanceContext:
    """Maintains finance session context."""
    user_id: str = "default"
    language: str = "en"
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    savings_goal: Optional[float] = None
    risk_tolerance: str = "moderate"
    discussed_topics: List[str] = field(default_factory=list)


class FinanceAdvisorAgent:
    """
    Personal finance education assistant that can:
    - Explain financial concepts
    - Calculate compound interest
    - Project retirement savings
    - Create budget recommendations
    - Explain investment types
    - Calculate loan payments
    - Help with debt payoff planning

    IMPORTANT: This is NOT a substitute for professional financial advice.
    """

    def __init__(self, llm=None, verbose: bool = False, language: str = "en"):
        """Initialize the finance advisor agent."""
        self.llm = llm
        self.verbose = verbose
        self.language = language
        self.context = FinanceContext(language=language)
        self.conversation_history: List[Dict[str, str]] = []
        self.tools = get_finance_tools()
        self.messages = MESSAGES.get(language, MESSAGES["en"])

        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10
        )

    def set_language(self, lang: str):
        """Set the language for responses."""
        if lang in MESSAGES:
            self.language = lang
            self.context.language = lang
            self.messages = MESSAGES[lang]

    def chat(self, user_message: str) -> str:
        """Process user message and generate response."""

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        response = self._generate_response(user_message)

        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return response

    def _generate_response(self, message: str) -> str:
        """Generate appropriate finance response."""
        message_lower = message.lower()
        lang = self.language

        # Budget queries
        if any(word in message_lower for word in ['budget', '예산', '予算', '50/30/20']):
            return self._handle_budget_query(message)

        # Compound interest
        if any(word in message_lower for word in ['compound', '복리', '複利', 'interest']):
            return self._handle_compound_interest_query(message)

        # Retirement
        if any(word in message_lower for word in ['retire', '은퇴', '退職', 'pension', '연금', '年金']):
            return self._handle_retirement_query(message)

        # Investment
        if any(word in message_lower for word in ['invest', '투자', '投資', 'stock', '주식', '株', 'bond', '채권', '債券']):
            return self._handle_investment_query(message)

        # Debt
        if any(word in message_lower for word in ['debt', '부채', '借金', 'loan', '대출', 'ローン', 'payoff']):
            return self._handle_debt_query(message)

        # Emergency fund
        if any(word in message_lower for word in ['emergency', '비상', '緊急', 'fund', '자금', '資金']):
            return self._handle_emergency_fund_query(message)

        # Savings
        if any(word in message_lower for word in ['save', 'saving', '저축', '貯蓄', 'goal']):
            return self._handle_savings_query(message)

        # Diversification
        if any(word in message_lower for word in ['diversif', '분산', '分散']):
            return self._handle_concept_query("diversification")

        # Default
        return self._handle_general_query(message)

    def _handle_budget_query(self, message: str) -> str:
        """Handle budget-related queries."""
        lang = self.language
        concept = CONCEPTS_DB.get("budgeting")

        response = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        response += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        response += "## " + ("Key Points" if lang == "en" else "핵심 포인트" if lang == "ko" else "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points['en']):
            response += f"- {point}\n"

        response += "\n## " + ("Budget Categories" if lang == "en" else "예산 카테고리" if lang == "ko" else "予算カテゴリ") + "\n\n"
        for cat in BUDGET_CATEGORIES:
            response += f"**{cat.name.get(lang, cat.name['en'])}** - {cat.recommended_percent}%\n"
            response += f"  {cat.description.get(lang, cat.description['en'])}\n\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_compound_interest_query(self, message: str) -> str:
        """Handle compound interest queries."""
        lang = self.language
        concept = CONCEPTS_DB.get("compound_interest")

        response = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        response += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        response += "## " + ("Key Points" if lang == "en" else "핵심 포인트" if lang == "ko" else "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points['en']):
            response += f"- {point}\n"

        # Example calculation
        example = calculate_compound_interest(10000, 7, 30, 12)
        response += "\n## " + ("Example" if lang == "en" else "예시" if lang == "ko" else "例") + "\n\n"

        if lang == "en":
            response += f"$10,000 invested at 7% for 30 years:\n"
            response += f"- **Final Amount:** ${example['final_amount']:,.2f}\n"
            response += f"- **Interest Earned:** ${example['interest_earned']:,.2f}\n"
        elif lang == "ko":
            response += f"1,000만원을 7%로 30년 투자:\n"
            response += f"- **최종 금액:** {example['final_amount']*100:,.0f}원\n"
            response += f"- **이자 수익:** {example['interest_earned']*100:,.0f}원\n"
        else:
            response += f"100万円を7%で30年投資:\n"
            response += f"- **最終金額:** {example['final_amount']*100:,.0f}円\n"
            response += f"- **利息収入:** {example['interest_earned']*100:,.0f}円\n"

        response += "\n## " + ("Tips" if lang == "en" else "팁" if lang == "ko" else "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips['en']):
            response += f"💡 {tip}\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_retirement_query(self, message: str) -> str:
        """Handle retirement planning queries."""
        lang = self.language
        concept = CONCEPTS_DB.get("retirement_planning")

        response = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        response += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        response += "## " + ("Key Points" if lang == "en" else "핵심 포인트" if lang == "ko" else "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points['en']):
            response += f"- {point}\n"

        # Example calculation
        example = calculate_retirement_savings(30, 65, 500, 10000, 7)
        response += "\n## " + ("Example Projection" if lang == "en" else "예상 시뮬레이션" if lang == "ko" else "予測シミュレーション") + "\n\n"

        if lang == "en":
            response += f"Starting at age 30, retiring at 65:\n"
            response += f"- Monthly contribution: $500\n"
            response += f"- Starting savings: $10,000\n"
            response += f"- **Projected Total:** ${example['projected_total']:,.2f}\n"
            response += f"- **Investment Growth:** ${example['investment_growth']:,.2f}\n"
        elif lang == "ko":
            response += f"30세에 시작, 65세 은퇴:\n"
            response += f"- 월 기여금: 50만원\n"
            response += f"- 시작 저축: 1,000만원\n"
            response += f"- **예상 총액:** {example['projected_total']*100:,.0f}원\n"
            response += f"- **투자 성장:** {example['investment_growth']*100:,.0f}원\n"
        else:
            response += f"30歳で開始、65歳で退職:\n"
            response += f"- 毎月の拠出: 5万円\n"
            response += f"- 開始時の貯蓄: 100万円\n"
            response += f"- **予測総額:** {example['projected_total']*100:,.0f}円\n"
            response += f"- **投資成長:** {example['investment_growth']*100:,.0f}円\n"

        response += "\n## " + ("Tips" if lang == "en" else "팁" if lang == "ko" else "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips['en']):
            response += f"💡 {tip}\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_investment_query(self, message: str) -> str:
        """Handle investment-related queries."""
        lang = self.language
        message_lower = message.lower()

        # Check for specific investment type
        for inv_id, inv in INVESTMENTS_DB.items():
            if inv_id in message_lower or any(name.lower() in message_lower for name in inv.name.values()):
                response = f"# {inv.name.get(lang, inv.name['en'])}\n\n"
                response += f"{inv.description.get(lang, inv.description['en'])}\n\n"
                response += f"**" + ("Risk Level" if lang == "en" else "리스크 수준" if lang == "ko" else "リスクレベル") + f":** {inv.risk_level.value.title()}\n"
                response += f"**" + ("Typical Returns" if lang == "en" else "일반적인 수익률" if lang == "ko" else "典型的なリターン") + f":** {inv.typical_returns}\n\n"

                response += "## " + ("Pros" if lang == "en" else "장점" if lang == "ko" else "メリット") + "\n"
                for pro in inv.pros.get(lang, inv.pros['en']):
                    response += f"✅ {pro}\n"

                response += "\n## " + ("Cons" if lang == "en" else "단점" if lang == "ko" else "デメリット") + "\n"
                for con in inv.cons.get(lang, inv.cons['en']):
                    response += f"⚠️ {con}\n"

                response += "\n## " + ("Best For" if lang == "en" else "추천 대상" if lang == "ko" else "おすすめの対象") + "\n"
                for best in inv.best_for.get(lang, inv.best_for['en']):
                    response += f"- {best}\n"

                response += "\n---\n"
                response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"
                return response

        # General investment overview
        response = "# " + ("Investment Types" if lang == "en" else "투자 유형" if lang == "ko" else "投資タイプ") + "\n\n"

        for inv in INVESTMENTS_DB.values():
            response += f"### {inv.name.get(lang, inv.name['en'])}\n"
            response += f"{inv.description.get(lang, inv.description['en'])}\n"
            response += f"*" + ("Risk" if lang == "en" else "리스크" if lang == "ko" else "リスク") + f": {inv.risk_level.value.title()}*\n\n"

        response += "---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_debt_query(self, message: str) -> str:
        """Handle debt management queries."""
        lang = self.language
        concept = CONCEPTS_DB.get("debt_management")

        response = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        response += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        response += "## " + ("Key Strategies" if lang == "en" else "핵심 전략" if lang == "ko" else "主要戦略") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points['en']):
            response += f"- {point}\n"

        response += "\n## " + ("Debt Payoff Methods" if lang == "en" else "부채 상환 방법" if lang == "ko" else "借金返済方法") + "\n\n"

        if lang == "en":
            response += "**Avalanche Method:** Pay highest interest first (saves money)\n"
            response += "**Snowball Method:** Pay smallest balance first (builds momentum)\n"
        elif lang == "ko":
            response += "**눈사태 방식:** 고금리 부채 먼저 상환 (돈 절약)\n"
            response += "**눈덩이 방식:** 작은 잔액 먼저 상환 (동기 부여)\n"
        else:
            response += "**アバランチ法:** 高金利から先に返済（お金を節約）\n"
            response += "**スノーボール法:** 最小残高から先に返済（モチベーション向上）\n"

        response += "\n## " + ("Tips" if lang == "en" else "팁" if lang == "ko" else "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips['en']):
            response += f"💡 {tip}\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_emergency_fund_query(self, message: str) -> str:
        """Handle emergency fund queries."""
        lang = self.language
        concept = CONCEPTS_DB.get("emergency_fund")

        response = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        response += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        response += "## " + ("Key Points" if lang == "en" else "핵심 포인트" if lang == "ko" else "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points['en']):
            response += f"- {point}\n"

        response += "\n## " + ("How Much Do You Need?" if lang == "en" else "얼마나 필요한가요?" if lang == "ko" else "いくら必要ですか？") + "\n\n"

        if lang == "en":
            response += "| Situation | Recommended |\n"
            response += "|-----------|-------------|\n"
            response += "| Stable job, no dependents | 3 months |\n"
            response += "| Family or variable income | 6 months |\n"
            response += "| Self-employed | 9-12 months |\n"
        elif lang == "ko":
            response += "| 상황 | 권장 |\n"
            response += "|------|------|\n"
            response += "| 안정적인 직장, 부양가족 없음 | 3개월 |\n"
            response += "| 가족 또는 변동 소득 | 6개월 |\n"
            response += "| 자영업 | 9-12개월 |\n"
        else:
            response += "| 状況 | 推奨 |\n"
            response += "|------|------|\n"
            response += "| 安定した仕事、扶養家族なし | 3ヶ月 |\n"
            response += "| 家族または変動収入 | 6ヶ月 |\n"
            response += "| 自営業 | 9-12ヶ月 |\n"

        response += "\n## " + ("Tips" if lang == "en" else "팁" if lang == "ko" else "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips['en']):
            response += f"💡 {tip}\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_savings_query(self, message: str) -> str:
        """Handle savings-related queries."""
        lang = self.language

        response = "# " + ("Savings Strategies" if lang == "en" else "저축 전략" if lang == "ko" else "貯蓄戦略") + "\n\n"

        if lang == "en":
            response += "## Pay Yourself First\n"
            response += "Save a portion of income before spending on anything else.\n\n"
            response += "## Automation Tips\n"
            response += "- Set up automatic transfers to savings\n"
            response += "- Use apps that round up purchases\n"
            response += "- Increase savings with each raise\n\n"
            response += "## Common Savings Goals\n"
            response += "1. Emergency Fund (3-6 months expenses)\n"
            response += "2. Retirement (15% of income)\n"
            response += "3. Major Purchases (house, car)\n"
            response += "4. Education\n"
            response += "5. Travel/Personal Goals\n"
        elif lang == "ko":
            response += "## 자신에게 먼저 지불하기\n"
            response += "다른 것에 지출하기 전에 소득의 일부를 저축하세요.\n\n"
            response += "## 자동화 팁\n"
            response += "- 저축으로 자동 이체 설정\n"
            response += "- 구매 금액을 반올림하는 앱 사용\n"
            response += "- 급여 인상 시 저축 증가\n\n"
            response += "## 일반적인 저축 목표\n"
            response += "1. 비상 자금 (3-6개월 생활비)\n"
            response += "2. 은퇴 (소득의 15%)\n"
            response += "3. 큰 구매 (집, 자동차)\n"
            response += "4. 교육\n"
            response += "5. 여행/개인 목표\n"
        else:
            response += "## まず自分に支払う\n"
            response += "他のことに支出する前に、収入の一部を貯蓄しましょう。\n\n"
            response += "## 自動化のヒント\n"
            response += "- 貯蓄への自動振替を設定\n"
            response += "- 購入金額を切り上げるアプリを使用\n"
            response += "- 昇給時に貯蓄を増やす\n\n"
            response += "## 一般的な貯蓄目標\n"
            response += "1. 緊急資金（3〜6ヶ月分の生活費）\n"
            response += "2. 退職（収入の15%）\n"
            response += "3. 大きな買い物（家、車）\n"
            response += "4. 教育\n"
            response += "5. 旅行/個人的な目標\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_concept_query(self, concept_id: str) -> str:
        """Handle general concept queries."""
        lang = self.language
        concept = CONCEPTS_DB.get(concept_id)

        if not concept:
            return self._handle_general_query("")

        response = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        response += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        response += "## " + ("Key Points" if lang == "en" else "핵심 포인트" if lang == "ko" else "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points['en']):
            response += f"- {point}\n"

        response += "\n## " + ("Tips" if lang == "en" else "팁" if lang == "ko" else "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips['en']):
            response += f"💡 {tip}\n"

        response += "\n---\n"
        response += f"*{DISCLAIMER.get(lang, DISCLAIMER['en'])}*"

        return response

    def _handle_general_query(self, message: str) -> str:
        """Handle general queries with welcome message."""
        lang = self.language
        msg = self.messages

        response = f"# 💰 {msg['welcome']}\n\n"
        response += f"{msg['welcome_desc']}\n\n"

        response += "## " + ("I Can Help With" if lang == "en" else "도움을 드릴 수 있는 것들" if lang == "ko" else "お手伝いできること") + "\n\n"

        features = msg['features']
        response += f"- 📊 **{features['budget']}** - 50/30/20\n"
        response += f"- 🎯 **{features['savings']}**\n"
        response += f"- 🏖️ **{features['retirement']}**\n"
        response += f"- 📈 **{features['investment']}**\n"
        response += f"- 💳 **{features['debt']}**\n"
        response += f"- 🚨 **{features['emergency']}**\n\n"

        response += f"**{msg['ask']}**\n\n"

        response += "---\n"
        response += f"⚠️ *{msg['disclaimer']}*"

        return response

    def reset(self):
        """Reset the finance advisor."""
        self.context = FinanceContext(language=self.language)
        self.conversation_history = []
        self.memory.clear()


def create_finance_agent(llm=None, verbose: bool = False, language: str = "en") -> FinanceAdvisorAgent:
    """Factory function to create finance advisor."""
    return FinanceAdvisorAgent(llm=llm, verbose=verbose, language=language)
