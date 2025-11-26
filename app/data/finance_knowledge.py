"""
Finance Knowledge Base - Financial concepts and calculations
DISCLAIMER: For educational purposes only. Not financial advice.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class GoalType(Enum):
    RETIREMENT = "retirement"
    EMERGENCY_FUND = "emergency_fund"
    HOME_PURCHASE = "home_purchase"
    EDUCATION = "education"
    INVESTMENT = "investment"
    DEBT_PAYOFF = "debt_payoff"


@dataclass
class FinancialConcept:
    """Represents a financial concept."""
    id: str
    name: Dict[str, str]  # i18n: {"en": "...", "ko": "...", "ja": "..."}
    description: Dict[str, str]
    key_points: Dict[str, List[str]]
    tips: Dict[str, List[str]]


@dataclass
class InvestmentType:
    """Represents an investment type."""
    id: str
    name: Dict[str, str]
    description: Dict[str, str]
    risk_level: RiskLevel
    typical_returns: str
    pros: Dict[str, List[str]]
    cons: Dict[str, List[str]]
    best_for: Dict[str, List[str]]


@dataclass
class BudgetCategory:
    """Budget category with recommended percentages."""
    id: str
    name: Dict[str, str]
    description: Dict[str, str]
    recommended_percent: float
    tips: Dict[str, List[str]]


# =============================================================================
# FINANCIAL CONCEPTS DATABASE
# =============================================================================

CONCEPTS_DB: Dict[str, FinancialConcept] = {
    "compound_interest": FinancialConcept(
        id="compound_interest",
        name={
            "en": "Compound Interest",
            "ko": "복리",
            "ja": "複利"
        },
        description={
            "en": "Interest calculated on both the initial principal and accumulated interest from previous periods.",
            "ko": "원금과 이전 기간에 축적된 이자 모두에 대해 계산되는 이자입니다.",
            "ja": "元本と過去の期間に蓄積された利子の両方に対して計算される利子です。"
        },
        key_points={
            "en": [
                "Money grows exponentially over time",
                "Starting early maximizes benefits",
                "Reinvesting earnings accelerates growth",
                "The '72 Rule' estimates doubling time"
            ],
            "ko": [
                "시간이 지남에 따라 돈이 기하급수적으로 증가합니다",
                "일찍 시작할수록 혜택이 극대화됩니다",
                "수익 재투자가 성장을 가속화합니다",
                "'72의 법칙'으로 자산 2배 기간을 추정할 수 있습니다"
            ],
            "ja": [
                "時間とともにお金は指数関数的に増加します",
                "早く始めるほど利益が最大化されます",
                "収益の再投資が成長を加速させます",
                "「72の法則」で倍増期間を推定できます"
            ]
        },
        tips={
            "en": [
                "Start investing as early as possible",
                "Reinvest dividends and interest",
                "Be patient - compounding takes time",
                "Use tax-advantaged accounts"
            ],
            "ko": [
                "가능한 한 빨리 투자를 시작하세요",
                "배당금과 이자를 재투자하세요",
                "인내심을 가지세요 - 복리에는 시간이 필요합니다",
                "세제 혜택 계좌를 활용하세요"
            ],
            "ja": [
                "できるだけ早く投資を始めましょう",
                "配当と利子を再投資しましょう",
                "忍耐強く - 複利には時間がかかります",
                "税制優遇口座を活用しましょう"
            ]
        }
    ),

    "emergency_fund": FinancialConcept(
        id="emergency_fund",
        name={
            "en": "Emergency Fund",
            "ko": "비상 자금",
            "ja": "緊急資金"
        },
        description={
            "en": "Money set aside for unexpected expenses or financial emergencies.",
            "ko": "예상치 못한 지출이나 금융 비상 상황을 위해 따로 모아둔 돈입니다.",
            "ja": "予期せぬ出費や金融緊急事態のために取っておくお金です。"
        },
        key_points={
            "en": [
                "Aim for 3-6 months of living expenses",
                "Keep in easily accessible account",
                "Only use for true emergencies",
                "Replenish after use"
            ],
            "ko": [
                "3-6개월치 생활비를 목표로 하세요",
                "쉽게 접근 가능한 계좌에 보관하세요",
                "진정한 비상 상황에만 사용하세요",
                "사용 후 다시 채우세요"
            ],
            "ja": [
                "3〜6ヶ月分の生活費を目標にしましょう",
                "簡単にアクセスできる口座に保管しましょう",
                "本当の緊急事態にのみ使用しましょう",
                "使用後は補充しましょう"
            ]
        },
        tips={
            "en": [
                "Start with $1,000 mini emergency fund",
                "Automate monthly contributions",
                "Use high-yield savings account",
                "Don't invest emergency fund in stocks"
            ],
            "ko": [
                "100만원 미니 비상 자금부터 시작하세요",
                "월별 자동 이체를 설정하세요",
                "고금리 저축 계좌를 활용하세요",
                "비상 자금을 주식에 투자하지 마세요"
            ],
            "ja": [
                "10万円のミニ緊急資金から始めましょう",
                "毎月の自動積立を設定しましょう",
                "高金利の普通預金口座を活用しましょう",
                "緊急資金を株式に投資しないでください"
            ]
        }
    ),

    "diversification": FinancialConcept(
        id="diversification",
        name={
            "en": "Diversification",
            "ko": "분산 투자",
            "ja": "分散投資"
        },
        description={
            "en": "Spreading investments across different assets to reduce risk.",
            "ko": "리스크를 줄이기 위해 여러 자산에 투자를 분산하는 것입니다.",
            "ja": "リスクを軽減するために、さまざまな資産に投資を分散させることです。"
        },
        key_points={
            "en": [
                "Don't put all eggs in one basket",
                "Mix different asset classes",
                "Include domestic and international",
                "Rebalance periodically"
            ],
            "ko": [
                "모든 달걀을 한 바구니에 담지 마세요",
                "다양한 자산 클래스를 혼합하세요",
                "국내외 투자를 포함하세요",
                "주기적으로 리밸런싱하세요"
            ],
            "ja": [
                "すべての卵を一つのカゴに入れないでください",
                "異なる資産クラスを組み合わせましょう",
                "国内外の投資を含めましょう",
                "定期的にリバランスしましょう"
            ]
        },
        tips={
            "en": [
                "Use index funds for instant diversification",
                "Consider target-date funds",
                "Review allocation annually",
                "Don't over-diversify"
            ],
            "ko": [
                "즉각적인 분산을 위해 인덱스 펀드를 활용하세요",
                "타겟데이트 펀드를 고려하세요",
                "연간 자산 배분을 검토하세요",
                "과도한 분산은 피하세요"
            ],
            "ja": [
                "即座の分散のためにインデックスファンドを活用しましょう",
                "ターゲットデートファンドを検討しましょう",
                "年次で資産配分を見直しましょう",
                "過度な分散は避けましょう"
            ]
        }
    ),

    "debt_management": FinancialConcept(
        id="debt_management",
        name={
            "en": "Debt Management",
            "ko": "부채 관리",
            "ja": "債務管理"
        },
        description={
            "en": "Strategies for effectively managing and paying off debt.",
            "ko": "부채를 효과적으로 관리하고 상환하기 위한 전략입니다.",
            "ja": "効果的に借金を管理し返済するための戦略です。"
        },
        key_points={
            "en": [
                "High-interest debt first (avalanche method)",
                "Or smallest balance first (snowball method)",
                "Avoid new debt while paying off",
                "Consider consolidation options"
            ],
            "ko": [
                "고금리 부채 먼저 상환 (눈사태 방식)",
                "또는 가장 작은 잔액부터 상환 (눈덩이 방식)",
                "상환 중 새로운 부채 피하기",
                "통합 옵션 고려하기"
            ],
            "ja": [
                "高金利の借金から先に返済（アバランチ法）",
                "または最小残高から先に返済（スノーボール法）",
                "返済中は新たな借金を避ける",
                "統合オプションを検討する"
            ]
        },
        tips={
            "en": [
                "List all debts with interest rates",
                "Pay more than minimum when possible",
                "Negotiate lower interest rates",
                "Build emergency fund while paying debt"
            ],
            "ko": [
                "모든 부채와 금리를 목록화하세요",
                "가능하면 최소 금액 이상 상환하세요",
                "낮은 금리로 협상하세요",
                "부채 상환 중에도 비상 자금을 만드세요"
            ],
            "ja": [
                "すべての借金と金利をリストアップしましょう",
                "可能な限り最低額以上を支払いましょう",
                "低い金利に交渉しましょう",
                "借金返済中も緊急資金を作りましょう"
            ]
        }
    ),

    "budgeting": FinancialConcept(
        id="budgeting",
        name={
            "en": "Budgeting (50/30/20 Rule)",
            "ko": "예산 관리 (50/30/20 법칙)",
            "ja": "予算管理（50/30/20ルール）"
        },
        description={
            "en": "A simple budgeting framework: 50% needs, 30% wants, 20% savings.",
            "ko": "간단한 예산 프레임워크: 필수 지출 50%, 원하는 것 30%, 저축 20%.",
            "ja": "シンプルな予算フレームワーク：必需品50%、欲しいもの30%、貯蓄20%。"
        },
        key_points={
            "en": [
                "50% - Needs (rent, utilities, food)",
                "30% - Wants (entertainment, dining)",
                "20% - Savings and debt repayment",
                "Adjust percentages to your situation"
            ],
            "ko": [
                "50% - 필수 (월세, 공과금, 식비)",
                "30% - 원하는 것 (오락, 외식)",
                "20% - 저축 및 부채 상환",
                "상황에 맞게 비율 조정하기"
            ],
            "ja": [
                "50% - 必需品（家賃、光熱費、食費）",
                "30% - 欲しいもの（娯楽、外食）",
                "20% - 貯蓄と借金返済",
                "状況に応じて割合を調整する"
            ]
        },
        tips={
            "en": [
                "Track spending for one month first",
                "Use budgeting apps",
                "Review and adjust monthly",
                "Automate savings"
            ],
            "ko": [
                "먼저 한 달간 지출을 추적하세요",
                "예산 앱을 활용하세요",
                "매월 검토하고 조정하세요",
                "저축을 자동화하세요"
            ],
            "ja": [
                "まず1ヶ月間支出を追跡しましょう",
                "予算アプリを活用しましょう",
                "毎月見直して調整しましょう",
                "貯蓄を自動化しましょう"
            ]
        }
    ),

    "retirement_planning": FinancialConcept(
        id="retirement_planning",
        name={
            "en": "Retirement Planning",
            "ko": "은퇴 계획",
            "ja": "退職計画"
        },
        description={
            "en": "Long-term financial planning for retirement years.",
            "ko": "은퇴 후를 위한 장기 재무 계획입니다.",
            "ja": "退職後のための長期的な財務計画です。"
        },
        key_points={
            "en": [
                "Start early to maximize compounding",
                "Contribute to employer-matched accounts",
                "Diversify retirement investments",
                "Plan for healthcare costs"
            ],
            "ko": [
                "복리 효과 극대화를 위해 일찍 시작하세요",
                "회사 매칭 계좌에 기여하세요",
                "은퇴 투자를 분산하세요",
                "의료비를 계획하세요"
            ],
            "ja": [
                "複利効果を最大化するために早く始めましょう",
                "会社のマッチング口座に拠出しましょう",
                "退職投資を分散しましょう",
                "医療費を計画しましょう"
            ]
        },
        tips={
            "en": [
                "Aim to save 15% of income for retirement",
                "Increase contributions with raises",
                "Don't withdraw early",
                "Consider Roth vs Traditional accounts"
            ],
            "ko": [
                "소득의 15%를 은퇴 저축 목표로 하세요",
                "급여 인상 시 기여금을 늘리세요",
                "조기 인출을 피하세요",
                "개인연금 vs 퇴직연금 고려하세요"
            ],
            "ja": [
                "収入の15%を退職貯蓄の目標にしましょう",
                "昇給時に拠出額を増やしましょう",
                "早期引き出しを避けましょう",
                "iDeCoとNISAを検討しましょう"
            ]
        }
    )
}


# =============================================================================
# INVESTMENT TYPES DATABASE
# =============================================================================

INVESTMENTS_DB: Dict[str, InvestmentType] = {
    "stocks": InvestmentType(
        id="stocks",
        name={"en": "Stocks", "ko": "주식", "ja": "株式"},
        description={
            "en": "Ownership shares in a company that can appreciate in value and pay dividends.",
            "ko": "가치가 상승하고 배당금을 지급할 수 있는 회사의 소유 지분입니다.",
            "ja": "価値が上昇し配当を支払う可能性のある会社の所有株式です。"
        },
        risk_level=RiskLevel.AGGRESSIVE,
        typical_returns="7-10% annually (historical average)",
        pros={
            "en": ["High growth potential", "Dividend income", "Liquidity", "Easy to buy/sell"],
            "ko": ["높은 성장 잠재력", "배당 수익", "유동성", "매매 용이"],
            "ja": ["高い成長可能性", "配当収入", "流動性", "売買が容易"]
        },
        cons={
            "en": ["High volatility", "Requires research", "Can lose value", "Emotional decisions"],
            "ko": ["높은 변동성", "연구 필요", "가치 손실 가능", "감정적 결정"],
            "ja": ["高いボラティリティ", "調査が必要", "価値が下がる可能性", "感情的な判断"]
        },
        best_for={
            "en": ["Long-term investors", "Those comfortable with risk", "Retirement accounts"],
            "ko": ["장기 투자자", "리스크를 감수할 수 있는 사람", "은퇴 계좌"],
            "ja": ["長期投資家", "リスクを許容できる人", "退職口座"]
        }
    ),

    "bonds": InvestmentType(
        id="bonds",
        name={"en": "Bonds", "ko": "채권", "ja": "債券"},
        description={
            "en": "Fixed-income investments where you lend money to governments or corporations.",
            "ko": "정부나 기업에 돈을 빌려주는 고정 수익 투자입니다.",
            "ja": "政府や企業にお金を貸す固定収入投資です。"
        },
        risk_level=RiskLevel.CONSERVATIVE,
        typical_returns="3-5% annually",
        pros={
            "en": ["Stable income", "Lower risk than stocks", "Predictable returns", "Portfolio balance"],
            "ko": ["안정적인 수익", "주식보다 낮은 리스크", "예측 가능한 수익", "포트폴리오 균형"],
            "ja": ["安定した収入", "株式より低いリスク", "予測可能なリターン", "ポートフォリオのバランス"]
        },
        cons={
            "en": ["Lower returns", "Interest rate risk", "Inflation risk", "Less liquidity"],
            "ko": ["낮은 수익률", "금리 리스크", "인플레이션 리스크", "낮은 유동성"],
            "ja": ["低いリターン", "金利リスク", "インフレリスク", "流動性が低い"]
        },
        best_for={
            "en": ["Conservative investors", "Near-retirement", "Income seekers", "Portfolio diversification"],
            "ko": ["보수적인 투자자", "은퇴 임박자", "수익 추구자", "포트폴리오 분산"],
            "ja": ["保守的な投資家", "退職間近の人", "収入を求める人", "ポートフォリオ分散"]
        }
    ),

    "index_funds": InvestmentType(
        id="index_funds",
        name={"en": "Index Funds", "ko": "인덱스 펀드", "ja": "インデックスファンド"},
        description={
            "en": "Funds that track a market index like S&P 500, offering instant diversification.",
            "ko": "S&P 500과 같은 시장 지수를 추종하여 즉각적인 분산을 제공하는 펀드입니다.",
            "ja": "S&P 500などの市場指数に連動し、即座の分散を提供するファンドです。"
        },
        risk_level=RiskLevel.MODERATE,
        typical_returns="7-10% annually (market average)",
        pros={
            "en": ["Low fees", "Instant diversification", "Simple to understand", "Consistent performance"],
            "ko": ["낮은 수수료", "즉각적인 분산", "이해하기 쉬움", "일관된 성과"],
            "ja": ["低い手数料", "即座の分散", "理解しやすい", "一貫したパフォーマンス"]
        },
        cons={
            "en": ["No outperformance", "Market risk", "Less control", "Includes all companies"],
            "ko": ["시장 초과 수익 없음", "시장 리스크", "통제력 부족", "모든 기업 포함"],
            "ja": ["市場を上回らない", "市場リスク", "コントロールが少ない", "すべての企業を含む"]
        },
        best_for={
            "en": ["Beginners", "Long-term investors", "Hands-off approach", "Retirement accounts"],
            "ko": ["초보자", "장기 투자자", "수동적 접근", "은퇴 계좌"],
            "ja": ["初心者", "長期投資家", "ハンズオフアプローチ", "退職口座"]
        }
    ),

    "real_estate": InvestmentType(
        id="real_estate",
        name={"en": "Real Estate", "ko": "부동산", "ja": "不動産"},
        description={
            "en": "Investment in property for rental income or appreciation.",
            "ko": "임대 수익이나 가치 상승을 위한 부동산 투자입니다.",
            "ja": "賃貸収入や価値上昇のための不動産投資です。"
        },
        risk_level=RiskLevel.MODERATE,
        typical_returns="8-12% annually (including appreciation)",
        pros={
            "en": ["Tangible asset", "Rental income", "Tax benefits", "Inflation hedge"],
            "ko": ["유형 자산", "임대 수익", "세금 혜택", "인플레이션 헤지"],
            "ja": ["有形資産", "賃貸収入", "税制優遇", "インフレヘッジ"]
        },
        cons={
            "en": ["High entry cost", "Illiquid", "Management required", "Market dependent"],
            "ko": ["높은 진입 비용", "비유동적", "관리 필요", "시장 의존"],
            "ja": ["高い参入コスト", "非流動的", "管理が必要", "市場依存"]
        },
        best_for={
            "en": ["Long-term wealth building", "Income seekers", "Hands-on investors", "Tax optimization"],
            "ko": ["장기 자산 형성", "수익 추구자", "능동적 투자자", "세금 최적화"],
            "ja": ["長期的な資産形成", "収入を求める人", "実践的な投資家", "税金最適化"]
        }
    ),

    "savings_account": InvestmentType(
        id="savings_account",
        name={"en": "High-Yield Savings", "ko": "고금리 저축", "ja": "高金利預金"},
        description={
            "en": "Bank accounts offering higher interest rates than traditional savings.",
            "ko": "기존 저축보다 높은 이자율을 제공하는 은행 계좌입니다.",
            "ja": "従来の預金よりも高い金利を提供する銀行口座です。"
        },
        risk_level=RiskLevel.CONSERVATIVE,
        typical_returns="4-5% annually (varies with rates)",
        pros={
            "en": ["FDIC insured", "No risk to principal", "Highly liquid", "Easy access"],
            "ko": ["예금 보호", "원금 손실 없음", "높은 유동성", "쉬운 접근"],
            "ja": ["預金保険対象", "元本リスクなし", "高い流動性", "簡単なアクセス"]
        },
        cons={
            "en": ["Low returns", "May not beat inflation", "Rate changes", "Opportunity cost"],
            "ko": ["낮은 수익률", "인플레이션 미달 가능", "금리 변동", "기회 비용"],
            "ja": ["低いリターン", "インフレに負ける可能性", "金利変動", "機会費用"]
        },
        best_for={
            "en": ["Emergency fund", "Short-term savings", "Risk-averse savers", "Goal-based saving"],
            "ko": ["비상 자금", "단기 저축", "리스크 회피 저축자", "목표 기반 저축"],
            "ja": ["緊急資金", "短期貯蓄", "リスク回避型の貯蓄者", "目標ベースの貯蓄"]
        }
    )
}


# =============================================================================
# BUDGET CATEGORIES
# =============================================================================

BUDGET_CATEGORIES: List[BudgetCategory] = [
    BudgetCategory(
        id="housing",
        name={"en": "Housing", "ko": "주거비", "ja": "住居費"},
        description={
            "en": "Rent or mortgage, utilities, maintenance",
            "ko": "월세 또는 주택담보대출, 공과금, 유지보수",
            "ja": "家賃または住宅ローン、光熱費、メンテナンス"
        },
        recommended_percent=30.0,
        tips={
            "en": ["Keep under 30% of income", "Consider roommates", "Negotiate rent annually"],
            "ko": ["소득의 30% 이하로 유지", "룸메이트 고려", "연간 임대료 협상"],
            "ja": ["収入の30%以下に抑える", "ルームメイトを検討", "毎年家賃を交渉"]
        }
    ),
    BudgetCategory(
        id="transportation",
        name={"en": "Transportation", "ko": "교통비", "ja": "交通費"},
        description={
            "en": "Car payments, insurance, gas, public transit",
            "ko": "자동차 할부금, 보험, 주유비, 대중교통",
            "ja": "車のローン、保険、ガソリン、公共交通機関"
        },
        recommended_percent=15.0,
        tips={
            "en": ["Consider used cars", "Use public transit", "Carpool when possible"],
            "ko": ["중고차 고려", "대중교통 이용", "가능하면 카풀"],
            "ja": ["中古車を検討", "公共交通機関を利用", "可能な限りカープール"]
        }
    ),
    BudgetCategory(
        id="food",
        name={"en": "Food", "ko": "식비", "ja": "食費"},
        description={
            "en": "Groceries and dining out",
            "ko": "식료품 및 외식",
            "ja": "食料品と外食"
        },
        recommended_percent=10.0,
        tips={
            "en": ["Meal prep weekly", "Limit dining out", "Use grocery lists"],
            "ko": ["주간 식사 준비", "외식 제한", "장보기 목록 사용"],
            "ja": ["週間の食事準備", "外食を制限", "買い物リストを使用"]
        }
    ),
    BudgetCategory(
        id="savings",
        name={"en": "Savings & Investments", "ko": "저축 및 투자", "ja": "貯蓄と投資"},
        description={
            "en": "Emergency fund, retirement, investments",
            "ko": "비상 자금, 은퇴, 투자",
            "ja": "緊急資金、退職、投資"
        },
        recommended_percent=20.0,
        tips={
            "en": ["Pay yourself first", "Automate transfers", "Increase with raises"],
            "ko": ["먼저 자신에게 지불", "자동 이체 설정", "급여 인상 시 증가"],
            "ja": ["まず自分に支払う", "自動振替を設定", "昇給時に増額"]
        }
    ),
    BudgetCategory(
        id="insurance",
        name={"en": "Insurance & Healthcare", "ko": "보험 및 의료", "ja": "保険と医療"},
        description={
            "en": "Health, life, disability insurance",
            "ko": "건강, 생명, 장애 보험",
            "ja": "健康、生命、障害保険"
        },
        recommended_percent=10.0,
        tips={
            "en": ["Shop around annually", "Use HSA if available", "Review coverage needs"],
            "ko": ["연간 비교 쇼핑", "가능하면 건강저축계좌 사용", "보장 필요성 검토"],
            "ja": ["毎年比較検討", "可能ならHSAを使用", "補償ニーズを見直す"]
        }
    ),
    BudgetCategory(
        id="entertainment",
        name={"en": "Entertainment & Personal", "ko": "오락 및 개인", "ja": "娯楽と個人"},
        description={
            "en": "Hobbies, subscriptions, personal care",
            "ko": "취미, 구독, 개인 관리",
            "ja": "趣味、サブスクリプション、パーソナルケア"
        },
        recommended_percent=10.0,
        tips={
            "en": ["Audit subscriptions regularly", "Find free alternatives", "Set spending limits"],
            "ko": ["정기적으로 구독 감사", "무료 대안 찾기", "지출 한도 설정"],
            "ja": ["定期的にサブスクを監査", "無料の代替品を探す", "支出制限を設定"]
        }
    )
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_concept(concept_id: str) -> Optional[FinancialConcept]:
    """Get a financial concept by ID."""
    return CONCEPTS_DB.get(concept_id)


def get_investment_type(investment_id: str) -> Optional[InvestmentType]:
    """Get an investment type by ID."""
    return INVESTMENTS_DB.get(investment_id)


def get_concepts_list() -> List[FinancialConcept]:
    """Get all financial concepts."""
    return list(CONCEPTS_DB.values())


def get_investments_by_risk(risk_level: RiskLevel) -> List[InvestmentType]:
    """Get investments by risk level."""
    return [inv for inv in INVESTMENTS_DB.values() if inv.risk_level == risk_level]


def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12
) -> Dict:
    """Calculate compound interest."""
    rate = annual_rate / 100
    amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    interest_earned = amount - principal

    return {
        "principal": principal,
        "final_amount": round(amount, 2),
        "interest_earned": round(interest_earned, 2),
        "annual_rate": annual_rate,
        "years": years,
        "compounds_per_year": compounds_per_year
    }


def calculate_retirement_savings(
    current_age: int,
    retirement_age: int,
    monthly_contribution: float,
    current_savings: float = 0,
    annual_return: float = 7.0
) -> Dict:
    """Calculate projected retirement savings."""
    years = retirement_age - current_age
    rate = annual_return / 100 / 12

    # Future value of current savings
    fv_current = current_savings * (1 + annual_return/100) ** years

    # Future value of monthly contributions
    if rate > 0:
        fv_contributions = monthly_contribution * (((1 + rate) ** (years * 12) - 1) / rate)
    else:
        fv_contributions = monthly_contribution * years * 12

    total = fv_current + fv_contributions
    total_contributed = current_savings + (monthly_contribution * 12 * years)
    growth = total - total_contributed

    return {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "years_to_retirement": years,
        "monthly_contribution": monthly_contribution,
        "projected_total": round(total, 2),
        "total_contributed": round(total_contributed, 2),
        "investment_growth": round(growth, 2),
        "assumed_return": annual_return
    }


def calculate_loan_payment(
    principal: float,
    annual_rate: float,
    years: int
) -> Dict:
    """Calculate monthly loan payment."""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12

    if monthly_rate > 0:
        payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                 ((1 + monthly_rate) ** num_payments - 1)
    else:
        payment = principal / num_payments

    total_paid = payment * num_payments
    total_interest = total_paid - principal

    return {
        "principal": principal,
        "monthly_payment": round(payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "annual_rate": annual_rate,
        "loan_term_years": years
    }


def get_budget_recommendation(monthly_income: float) -> Dict:
    """Get budget recommendation based on income."""
    recommendations = {}
    for category in BUDGET_CATEGORIES:
        amount = monthly_income * (category.recommended_percent / 100)
        recommendations[category.id] = {
            "name": category.name,
            "recommended_percent": category.recommended_percent,
            "recommended_amount": round(amount, 2),
            "tips": category.tips
        }

    return {
        "monthly_income": monthly_income,
        "categories": recommendations
    }
