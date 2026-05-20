"""
Finance Agent - LangChain 0.3 agent for the personal-finance education app.

DISCLAIMER: This module powers an *educational* assistant. It is NOT a
substitute for personalised financial advice from a licensed professional.

Two execution modes are supported, chosen automatically (or via the
``LLM_PROVIDER`` environment variable):

- ``anthropic`` — uses ChatAnthropic (Claude) when ``ANTHROPIC_API_KEY`` is set
- ``openai`` — uses ChatOpenAI (GPT) when ``OPENAI_API_KEY`` is set
- ``none`` — graceful fallback to a deterministic keyword router (no network)

Whenever a response involves a specific recommendation (budget plan, investment
advice, debt payoff plan, large purchase, retirement projection, etc.), the
"NOT financial advice" disclaimer is appended to the final answer.
"""

from __future__ import annotations

import logging
import os
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from app.data.finance_knowledge import (
    BUDGET_CATEGORIES,
    CONCEPTS_DB,
    INVESTMENTS_DB,
    calculate_compound_interest,
    calculate_retirement_savings,
)
from app.tools.finance_tools import DISCLAIMER, get_finance_tools

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


# Topics that should always carry the financial-advice disclaimer.
ADVISORY_KEYWORDS: tuple[str, ...] = (
    "invest",
    "stock",
    "bond",
    "fund",
    "portfolio",
    "buy",
    "sell",
    "should i",
    "recommend",
    "advice",
    "loan",
    "mortgage",
    "debt",
    "payoff",
    "retirement",
    "401k",
    "ira",
    "savings",
    "budget",
    "house",
    "car",
    "crypto",
    "주식",
    "투자",
    "대출",
    "은퇴",
    "부채",
    "예산",
    "株",
    "投資",
    "退職",
    "借金",
    "ローン",
    "予算",
)


MESSAGES: dict[str, dict[str, Any]] = {
    "en": {
        "welcome": "Personal Finance Advisor",
        "welcome_desc": "I can help you with financial education and planning.",
        "disclaimer": "DISCLAIMER: This is for educational purposes only. NOT financial advice.",
        "features": {
            "budget": "Budget Planning",
            "savings": "Savings Goals",
            "retirement": "Retirement Calculator",
            "investment": "Investment Education",
            "debt": "Debt Management",
            "emergency": "Emergency Fund",
        },
        "ask": "What would you like to learn about?",
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
            "emergency": "비상 자금",
        },
        "ask": "무엇에 대해 알고 싶으신가요?",
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
            "emergency": "緊急資金",
        },
        "ask": "何について知りたいですか？",
    },
}


SYSTEM_PROMPT = """You are a careful, plain-spoken *personal-finance education* assistant.

CRITICAL DISCLAIMER (read every turn):
- You are NOT a licensed financial advisor and do NOT provide personalised
  financial, tax, legal, or investment advice.
- The information you share is GENERAL and EDUCATIONAL only.
- For specific recommendations (investing a specific amount, paying off a
  specific debt, retirement product selection, large purchases like a house or
  car, choosing between insurance products), you ALWAYS remind the user that
  they should consult a licensed financial advisor.
- Never quote live market prices, never promise returns, never recommend
  specific tickers or specific brokerages, and never claim something is
  "guaranteed" or "risk-free".

How you should respond:
1. Be warm, concrete, and concise.
2. Use the provided tools when they fit — budget_planner, compound_interest_calculator,
   retirement_calculator, investment_education, debt_payoff_calculator,
   emergency_fund_calculator, loan_calculator, financial_concept,
   budget_categories_overview. Prefer tools over free-form recall for numbers.
3. Always append a one-line "NOT financial advice — consult a licensed advisor"
   reminder whenever the response includes a specific recommendation involving
   money (investments, debt, large purchases, retirement projections, budget
   plans).
4. Support the user's language: respond in English, Korean (한국어), or
   Japanese (日本語) according to the user's message.
"""


@dataclass
class FinanceContext:
    """Lightweight session context for the finance advisor."""

    user_id: str = "default"
    language: str = "en"
    income: float | None = None
    goals: list[str] = field(default_factory=list)
    risk_tolerance: str = "moderate"
    discussed_topics: list[str] = field(default_factory=list)


def _resolve_llm() -> tuple[str, BaseChatModel | None]:
    """Return ``(mode, llm)`` based on environment configuration.

    ``mode`` is one of ``"anthropic" | "openai" | "none"``.
    """
    provider = (os.environ.get("LLM_PROVIDER") or "").strip().lower()

    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    if provider == "none":
        return "none", None

    if not provider:
        if has_anthropic:
            provider = "anthropic"
        elif has_openai:
            provider = "openai"
        else:
            return "none", None

    try:
        if provider == "anthropic":
            if not has_anthropic:
                logger.warning("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is missing.")
                return "none", None
            from langchain_anthropic import ChatAnthropic

            model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
            return "anthropic", ChatAnthropic(model=model, temperature=0.2, max_tokens=1024)

        if provider == "openai":
            if not has_openai:
                logger.warning("LLM_PROVIDER=openai but OPENAI_API_KEY is missing.")
                return "none", None
            from langchain_openai import ChatOpenAI

            model = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
            return "openai", ChatOpenAI(model=model, temperature=0.2)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to construct LLM for provider %s: %s", provider, exc)
        return "none", None

    logger.warning("Unknown LLM_PROVIDER=%s; falling back to keyword router.", provider)
    return "none", None


class FinanceAdvisorAgent:
    """Personal finance education assistant with optional LLM tool-calling."""

    SYSTEM_PROMPT = SYSTEM_PROMPT

    def __init__(
        self,
        llm: BaseChatModel | None = None,
        verbose: bool = False,
        language: str = "en",
        history_window: int = 10,
    ) -> None:
        self.verbose = verbose
        self.language = language if language in MESSAGES else "en"
        self.context = FinanceContext(language=self.language)
        self.conversation_history: list[dict[str, str]] = []
        self._recent_turns: deque[tuple[str, str]] = deque(maxlen=history_window * 2)
        self.tools: list[BaseTool] = get_finance_tools()

        if llm is not None:
            self.llm: BaseChatModel | None = llm
            self.mode = "custom"
        else:
            self.mode, self.llm = _resolve_llm()

        self._agent_executor: Any | None = (
            self._build_agent_executor() if self.llm is not None else None
        )

    # ------------------------------------------------------------------ public

    @property
    def llm_enabled(self) -> bool:
        """``True`` if requests are answered by an LLM-backed agent."""
        return self._agent_executor is not None

    def set_language(self, lang: str) -> None:
        """Update the response language for this session."""
        if lang in MESSAGES:
            self.language = lang
            self.context.language = lang

    def chat(self, user_message: str) -> str:
        """Process a user message and return the assistant response."""
        self._append_history("user", user_message)

        try:
            if self._agent_executor is not None:
                response = self._llm_response(user_message)
            else:
                response = self._keyword_router(user_message)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Agent failed; falling back to keyword router: %s", exc)
            response = self._keyword_router(user_message)

        response = self._maybe_append_disclaimer(user_message, response)
        self._append_history("assistant", response)
        return response

    def reset(self) -> None:
        """Reset session state."""
        self.context = FinanceContext(language=self.language)
        self.conversation_history = []
        self._recent_turns.clear()

    # ------------------------------------------------------------------ internals

    def _append_history(self, role: str, content: str) -> None:
        self.conversation_history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        self._recent_turns.append((role, content))

    def _maybe_append_disclaimer(self, user_message: str, response: str) -> str:
        """Append the "NOT financial advice" disclaimer when relevant."""
        msg_lower = user_message.lower()
        triggers = any(keyword in msg_lower for keyword in ADVISORY_KEYWORDS)
        already_has = (
            "NOT financial advice" in response
            or "재정 조언이 아닙니다" in response
            or "財務アドバイスではありません" in response
        )
        if triggers and not already_has:
            disclaimer = DISCLAIMER.get(self.language, DISCLAIMER["en"])
            response = f"{response.rstrip()}\n\n---\n*{disclaimer}*"
        return response

    # -------- LLM-backed path --------------------------------------------

    def _build_agent_executor(self) -> Any | None:
        """Construct a LangChain tool-calling agent executor."""
        try:
            from langchain.agents import AgentExecutor, create_tool_calling_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.SYSTEM_PROMPT),
                    MessagesPlaceholder("chat_history", optional=True),
                    ("human", "{input}"),
                    MessagesPlaceholder("agent_scratchpad"),
                ]
            )
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                handle_parsing_errors=True,
                max_iterations=6,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Could not build agent executor: %s; using keyword fallback.", exc)
            return None

    def _llm_response(self, user_message: str) -> str:
        assert self._agent_executor is not None
        history_msgs = self._chat_history_for_lcel()
        result = self._agent_executor.invoke(
            {"input": user_message, "chat_history": history_msgs}
        )
        output = result.get("output") if isinstance(result, dict) else str(result)
        if isinstance(output, list):
            parts: list[str] = []
            for block in output:
                if isinstance(block, dict) and "text" in block:
                    parts.append(str(block["text"]))
                else:
                    parts.append(str(block))
            output = "\n".join(parts).strip()
        if not isinstance(output, str) or not output.strip():
            return self._keyword_router(user_message)
        return output

    def _chat_history_for_lcel(self) -> list[Any]:
        """Convert the deque into LangChain message objects."""
        try:
            from langchain_core.messages import AIMessage, HumanMessage
        except Exception:  # pragma: no cover
            return []

        messages: list[Any] = []
        # Skip the just-appended user message (it goes into "input").
        for role, content in list(self._recent_turns)[:-1]:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
        return messages

    # -------- keyword router (fallback) -----------------------------------

    def _keyword_router(self, message: str) -> str:
        message_lower = message.lower()

        if any(w in message_lower for w in ("budget", "예산", "予算", "50/30/20")):
            return self._handle_budget_query()

        if any(w in message_lower for w in ("compound", "복리", "複利", "interest", "이자", "利息")):
            return self._handle_compound_interest_query()

        if any(
            w in message_lower
            for w in ("retire", "은퇴", "退職", "pension", "연금", "年金", "401k", "ira")
        ):
            return self._handle_retirement_query()

        if any(
            w in message_lower
            for w in ("invest", "투자", "投資", "stock", "주식", "株", "bond", "채권", "債券", "fund")
        ):
            return self._handle_investment_query(message)

        if any(
            w in message_lower
            for w in ("debt", "부채", "借金", "loan", "대출", "ローン", "mortgage", "payoff")
        ):
            return self._handle_debt_query()

        if any(w in message_lower for w in ("emergency", "비상", "緊急", "rainy day")):
            return self._handle_emergency_fund_query()

        if any(w in message_lower for w in ("save", "saving", "저축", "貯蓄", "goal", "목표")):
            return self._handle_savings_query()

        if any(w in message_lower for w in ("diversif", "분산", "分散")):
            return self._handle_concept_query("diversification")

        return self._handle_general_query()

    # -------- keyword response builders -----------------------------------

    def _localise(self, en: str, ko: str, ja: str) -> str:
        return {"en": en, "ko": ko, "ja": ja}.get(self.language, en)

    def _handle_budget_query(self) -> str:
        lang = self.language
        concept = CONCEPTS_DB["budgeting"]

        out = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        out += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        out += "## " + self._localise("Key Points", "핵심 포인트", "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points["en"]):
            out += f"- {point}\n"

        out += "\n## " + self._localise("Budget Categories", "예산 카테고리", "予算カテゴリ") + "\n\n"
        for cat in BUDGET_CATEGORIES:
            out += f"**{cat.name.get(lang, cat.name['en'])}** — {cat.recommended_percent}%\n"
            out += f"  {cat.description.get(lang, cat.description['en'])}\n\n"

        return out.rstrip()

    def _handle_compound_interest_query(self) -> str:
        lang = self.language
        concept = CONCEPTS_DB["compound_interest"]

        out = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        out += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        out += "## " + self._localise("Key Points", "핵심 포인트", "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points["en"]):
            out += f"- {point}\n"

        example = calculate_compound_interest(10000, 7, 30, 12)
        out += "\n## " + self._localise("Example", "예시", "例") + "\n\n"
        if lang == "ko":
            out += "1,000만원을 7%로 30년 투자 (예시):\n"
            out += f"- **최종 금액:** {example['final_amount'] * 100:,.0f}원\n"
            out += f"- **이자 수익:** {example['interest_earned'] * 100:,.0f}원\n"
        elif lang == "ja":
            out += "100万円を7%で30年投資（例）:\n"
            out += f"- **最終金額:** {example['final_amount'] * 100:,.0f}円\n"
            out += f"- **利息収入:** {example['interest_earned'] * 100:,.0f}円\n"
        else:
            out += "$10,000 invested at 7% for 30 years:\n"
            out += f"- **Final Amount:** ${example['final_amount']:,.2f}\n"
            out += f"- **Interest Earned:** ${example['interest_earned']:,.2f}\n"

        out += "\n## " + self._localise("Tips", "팁", "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips["en"]):
            out += f"- {tip}\n"

        return out.rstrip()

    def _handle_retirement_query(self) -> str:
        lang = self.language
        concept = CONCEPTS_DB["retirement_planning"]

        out = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        out += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        out += "## " + self._localise("Key Points", "핵심 포인트", "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points["en"]):
            out += f"- {point}\n"

        example = calculate_retirement_savings(30, 65, 500, 10000, 7)
        out += "\n## " + self._localise(
            "Example Projection", "예상 시뮬레이션", "予測シミュレーション"
        ) + "\n\n"
        if lang == "ko":
            out += "30세에 시작, 65세 은퇴 (예시):\n"
            out += "- 월 기여금: 50만원, 시작 저축: 1,000만원\n"
            out += f"- **예상 총액:** {example['projected_total'] * 100:,.0f}원\n"
            out += f"- **투자 성장:** {example['investment_growth'] * 100:,.0f}원\n"
        elif lang == "ja":
            out += "30歳開始、65歳退職（例）:\n"
            out += "- 毎月の拠出: 5万円、開始貯蓄: 100万円\n"
            out += f"- **予測総額:** {example['projected_total'] * 100:,.0f}円\n"
            out += f"- **投資成長:** {example['investment_growth'] * 100:,.0f}円\n"
        else:
            out += "Starting at 30, retiring at 65 (illustrative):\n"
            out += "- Monthly contribution: $500, starting savings: $10,000\n"
            out += f"- **Projected Total:** ${example['projected_total']:,.2f}\n"
            out += f"- **Investment Growth:** ${example['investment_growth']:,.2f}\n"

        return out.rstrip()

    def _handle_investment_query(self, message: str) -> str:
        lang = self.language
        message_lower = message.lower()

        for inv_id, inv in INVESTMENTS_DB.items():
            if inv_id in message_lower or any(
                name.lower() in message_lower for name in inv.name.values()
            ):
                out = f"# {inv.name.get(lang, inv.name['en'])}\n\n"
                out += f"{inv.description.get(lang, inv.description['en'])}\n\n"
                out += (
                    "**"
                    + self._localise("Risk Level", "리스크 수준", "リスクレベル")
                    + f":** {inv.risk_level.value.title()}\n"
                )
                out += (
                    "**"
                    + self._localise("Typical Returns", "일반적인 수익률", "典型的なリターン")
                    + f":** {inv.typical_returns}\n\n"
                )
                out += "## " + self._localise("Pros", "장점", "メリット") + "\n"
                for pro in inv.pros.get(lang, inv.pros["en"]):
                    out += f"- {pro}\n"
                out += "\n## " + self._localise("Cons", "단점", "デメリット") + "\n"
                for con in inv.cons.get(lang, inv.cons["en"]):
                    out += f"- {con}\n"
                out += "\n## " + self._localise("Best For", "추천 대상", "おすすめの対象") + "\n"
                for best in inv.best_for.get(lang, inv.best_for["en"]):
                    out += f"- {best}\n"
                return out.rstrip()

        out = "# " + self._localise("Investment Types", "투자 유형", "投資タイプ") + "\n\n"
        for inv in INVESTMENTS_DB.values():
            out += f"### {inv.name.get(lang, inv.name['en'])}\n"
            out += f"{inv.description.get(lang, inv.description['en'])}\n"
            out += (
                "*"
                + self._localise("Risk", "리스크", "リスク")
                + f": {inv.risk_level.value.title()}*\n\n"
            )
        return out.rstrip()

    def _handle_debt_query(self) -> str:
        lang = self.language
        concept = CONCEPTS_DB["debt_management"]

        out = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        out += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        out += "## " + self._localise("Key Strategies", "핵심 전략", "主要戦略") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points["en"]):
            out += f"- {point}\n"

        out += "\n## " + self._localise(
            "Debt Payoff Methods", "부채 상환 방법", "借金返済方法"
        ) + "\n\n"
        if lang == "ko":
            out += "- **눈사태 방식:** 고금리 부채 먼저 상환 (총 이자 최소화)\n"
            out += "- **눈덩이 방식:** 가장 작은 잔액 먼저 상환 (동기 부여)\n"
        elif lang == "ja":
            out += "- **アバランチ法:** 高金利の借金から返済（総利息を最小化）\n"
            out += "- **スノーボール法:** 最小残高から返済（モチベーション向上）\n"
        else:
            out += "- **Avalanche method:** pay highest-interest debt first (lowest total interest)\n"
            out += "- **Snowball method:** pay smallest balance first (builds momentum)\n"

        return out.rstrip()

    def _handle_emergency_fund_query(self) -> str:
        lang = self.language
        concept = CONCEPTS_DB["emergency_fund"]

        out = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        out += f"{concept.description.get(lang, concept.description['en'])}\n\n"

        out += "## " + self._localise("Key Points", "핵심 포인트", "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points["en"]):
            out += f"- {point}\n"

        out += "\n## " + self._localise(
            "How Much Do You Need?", "얼마나 필요한가요?", "いくら必要ですか？"
        ) + "\n\n"
        if lang == "ko":
            out += "- 안정적인 직장, 부양가족 없음: 3개월\n"
            out += "- 가족 또는 변동 소득: 6개월\n"
            out += "- 자영업: 9-12개월\n"
        elif lang == "ja":
            out += "- 安定した仕事、扶養家族なし: 3ヶ月\n"
            out += "- 家族または変動収入: 6ヶ月\n"
            out += "- 自営業: 9-12ヶ月\n"
        else:
            out += "- Stable job, no dependents: 3 months\n"
            out += "- Family or variable income: 6 months\n"
            out += "- Self-employed: 9-12 months\n"

        return out.rstrip()

    def _handle_savings_query(self) -> str:
        lang = self.language
        if lang == "ko":
            return (
                "# 저축 전략\n\n"
                "## 자신에게 먼저 지불하기\n"
                "다른 것에 지출하기 전에 소득의 일부를 자동으로 저축으로 이체하세요.\n\n"
                "## 일반적인 저축 목표\n"
                "1. 비상 자금 (3-6개월 생활비)\n"
                "2. 은퇴 (소득의 15%)\n"
                "3. 큰 구매 (집, 자동차)\n"
                "4. 교육\n"
                "5. 여행/개인 목표"
            )
        if lang == "ja":
            return (
                "# 貯蓄戦略\n\n"
                "## まず自分に支払う\n"
                "他のことに支出する前に、収入の一部を自動的に貯蓄に振り替えましょう。\n\n"
                "## 一般的な貯蓄目標\n"
                "1. 緊急資金（3〜6ヶ月分の生活費）\n"
                "2. 退職（収入の15%）\n"
                "3. 大きな買い物（家、車）\n"
                "4. 教育\n"
                "5. 旅行/個人的な目標"
            )
        return (
            "# Savings Strategies\n\n"
            "## Pay Yourself First\n"
            "Automate a portion of every paycheck into savings before you spend anything else.\n\n"
            "## Common Savings Goals\n"
            "1. Emergency Fund (3-6 months of expenses)\n"
            "2. Retirement (15% of income)\n"
            "3. Major Purchases (house, car)\n"
            "4. Education\n"
            "5. Travel / Personal Goals"
        )

    def _handle_concept_query(self, concept_id: str) -> str:
        lang = self.language
        concept = CONCEPTS_DB.get(concept_id)
        if not concept:
            return self._handle_general_query()

        out = f"# {concept.name.get(lang, concept.name['en'])}\n\n"
        out += f"{concept.description.get(lang, concept.description['en'])}\n\n"
        out += "## " + self._localise("Key Points", "핵심 포인트", "キーポイント") + "\n\n"
        for point in concept.key_points.get(lang, concept.key_points["en"]):
            out += f"- {point}\n"
        out += "\n## " + self._localise("Tips", "팁", "ヒント") + "\n\n"
        for tip in concept.tips.get(lang, concept.tips["en"]):
            out += f"- {tip}\n"
        return out.rstrip()

    def _handle_general_query(self) -> str:
        lang = self.language
        msg = MESSAGES.get(lang, MESSAGES["en"])
        features = msg["features"]
        out = f"# {msg['welcome']}\n\n{msg['welcome_desc']}\n\n"
        out += "## " + self._localise(
            "I Can Help With", "도움을 드릴 수 있는 것들", "お手伝いできること"
        ) + "\n\n"
        out += f"- **{features['budget']}** — 50/30/20\n"
        out += f"- **{features['savings']}**\n"
        out += f"- **{features['retirement']}**\n"
        out += f"- **{features['investment']}**\n"
        out += f"- **{features['debt']}**\n"
        out += f"- **{features['emergency']}**\n\n"
        out += f"**{msg['ask']}**\n\n---\n*{msg['disclaimer']}*"
        return out


def create_finance_agent(
    llm: BaseChatModel | None = None,
    verbose: bool = False,
    language: str = "en",
) -> FinanceAdvisorAgent:
    """Factory function to create a finance advisor agent."""
    return FinanceAdvisorAgent(llm=llm, verbose=verbose, language=language)


__all__ = [
    "ADVISORY_KEYWORDS",
    "SYSTEM_PROMPT",
    "FinanceAdvisorAgent",
    "FinanceContext",
    "create_finance_agent",
]
