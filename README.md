# AI Finance Advisor

LangChain-powered personal finance education assistant with multi-language support (English, Korean, Japanese).

**IMPORTANT DISCLAIMER**: This application provides general financial education for informational purposes only. It is NOT financial advice. Always consult a qualified financial advisor for personalized guidance.

## Live Demo

[**View Demo**](https://yoon-k.github.io/langchain-finance-advisor/)

## Features

- **Budget Planning**: Learn the 50/30/20 rule for managing income
- **Compound Interest Calculator**: See how money grows over time
- **Retirement Projections**: Calculate future retirement savings
- **Investment Education**: Learn about stocks, bonds, index funds, and more
- **Debt Management**: Understand avalanche and snowball payoff methods
- **Emergency Fund Calculator**: Determine how much to save
- **Loan Calculator**: Calculate monthly payments and total interest
- **Multi-language Support**: English, Korean (한국어), Japanese (日本語)

## Architecture

```
langchain-finance-advisor/
├── app/
│   ├── agents/
│   │   └── finance_agent.py      # Main finance advisor agent
│   ├── tools/
│   │   └── finance_tools.py      # LangChain financial tools
│   ├── data/
│   │   └── finance_knowledge.py  # Financial concepts database
│   └── api.py                    # Flask API endpoints
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── index.html
└── requirements.txt
```

## LangChain Components

### Custom Tools
- `CompoundInterestTool`: Calculate compound interest growth
- `RetirementCalculatorTool`: Project retirement savings
- `LoanCalculatorTool`: Calculate loan payments
- `BudgetPlannerTool`: Generate budget recommendations
- `InvestmentInfoTool`: Get investment type information
- `FinancialConceptTool`: Learn financial concepts
- `EmergencyFundCalculatorTool`: Calculate emergency fund needs
- `DebtPayoffTool`: Calculate debt payoff timeline
- `SavingsGoalTool`: Plan savings goals

### Agent Architecture
```python
from app.agents.finance_agent import create_finance_agent

# Create agent with language preference
agent = create_finance_agent(language="en")  # or "ko", "ja"

# Chat with context awareness
response = agent.chat("Explain compound interest")
response = agent.chat("How should I budget my $5000 monthly income?")
response = agent.chat("Calculate retirement savings if I invest $500/month")
```

### Multi-language Support
```python
# All responses support English, Korean, and Japanese
from app.data.finance_knowledge import CONCEPTS_DB

concept = CONCEPTS_DB["compound_interest"]
print(concept.name["en"])  # "Compound Interest"
print(concept.name["ko"])  # "복리"
print(concept.name["ja"])  # "複利"
```

## Installation

```bash
# Clone repository
git clone https://github.com/yoon-k/langchain-finance-advisor.git
cd langchain-finance-advisor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.api
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Main chat endpoint (supports language param) |
| `/api/concepts` | GET | List financial concepts |
| `/api/investments` | GET | List investment types |
| `/api/budget-categories` | GET | List budget categories |
| `/api/calculate/compound-interest` | POST | Calculate compound interest |
| `/api/calculate/retirement` | POST | Calculate retirement projection |
| `/api/calculate/loan` | POST | Calculate loan payments |
| `/api/calculate/budget` | POST | Get budget recommendations |

## Financial Concepts Covered

### Core Concepts
- Compound Interest
- Budgeting (50/30/20 Rule)
- Emergency Fund
- Diversification
- Debt Management
- Retirement Planning

### Investment Types
- Stocks
- Bonds
- Index Funds
- Real Estate
- High-Yield Savings

### Budget Categories
- Housing (30%)
- Transportation (15%)
- Food (10%)
- Savings & Investments (20%)
- Insurance & Healthcare (10%)
- Entertainment & Personal (10%)

## Tech Stack

- **LangChain**: Agent framework and tool orchestration
- **Flask**: Backend API server
- **Python 3.9+**: Core language
- **Pydantic**: Data validation and tool input schemas

## Supported Languages

| Language | Code | Status |
|----------|------|--------|
| English | `en` | ✅ Full Support |
| Korean | `ko` | ✅ Full Support |
| Japanese | `ja` | ✅ Full Support |

## Contributing

Contributions are welcome! When adding financial information, please ensure accuracy and include appropriate disclaimers.

## License

MIT License - This is an educational project demonstrating LangChain capabilities.

## Disclaimer

This application is for educational and demonstration purposes only. The financial information provided is general in nature and should not be used as a substitute for professional financial advice. Always consult a qualified financial advisor for personalized guidance. Past performance does not guarantee future results. All investments carry risk.
