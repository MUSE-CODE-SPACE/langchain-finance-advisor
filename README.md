# AI Finance Advisor

LangChain 0.3 powered personal finance *education* assistant with a Flask API
and multi-language support (English / Korean / Japanese).

> **IMPORTANT FINANCIAL DISCLAIMER**
> This application is for **educational purposes only**. It is **NOT** a
> substitute for personalised financial, tax, legal, or investment advice.
> Always consult a **licensed financial advisor** for guidance specific to
> your situation. Past performance does not guarantee future results. All
> investments carry risk.
>
> 본 애플리케이션은 **교육 목적**의 일반 금융 정보 제공용입니다. 어떠한
> 재무·세무·법률·투자 자문도 아닙니다. 본인의 상황에 맞는 안내가 필요하다면
> 반드시 **자격을 갖춘 재정 상담사**와 상담하세요.

[**Live demo**](https://yoon-k.github.io/langchain-finance-advisor/)

---

## Features

- **Budget Planning** — 50 / 30 / 20 rule + per-category breakdown
- **Compound Interest** — see how money grows over time
- **Retirement Projections** — contribution + return + horizon
- **Investment Education** — stocks, bonds, index funds, real estate, HYSA
- **Debt Management** — avalanche / snowball + payoff calculator
- **Emergency Fund** — target sizing (3 / 6 / 9-12 months)
- **Loan Calculator** — monthly payment + total interest
- **Multi-language** — English, Korean (한국어), Japanese (日本語)
- **Graceful LLM fallback** — runs without any API key (keyword router) or
  with Anthropic Claude / OpenAI GPT when keys are configured

## Quick start

### Using `pip`

```bash
git clone https://github.com/MUSE-CODE-SPACE/langchain-finance-advisor.git
cd langchain-finance-advisor

python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Editable install with dev extras (pytest, ruff, mypy).
pip install -e ".[dev]"

# (optional) configure LLM keys
cp .env.example .env

# Start the dev server
python -m app.api
```

### Using `uv`

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
python -m app.api
```

### Using `make`

```bash
make install
make dev
make test
make lint
```

Check the API is alive:

```bash
curl http://localhost:5000/api/health
# {"status":"healthy","service":"finance-advisor","timestamp":"...","llm_enabled":false}

curl -X POST http://localhost:5000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Explain compound interest"}'
```

## LLM modes

The agent picks a backend based on environment variables:

| `LLM_PROVIDER` | Required keys                       | Default model                 | Behaviour |
| -------------- | ----------------------------------- | ----------------------------- | --------- |
| `anthropic`    | `ANTHROPIC_API_KEY`                 | `claude-haiku-4-5-20251001`   | Tool-calling agent (LCEL) |
| `openai`       | `OPENAI_API_KEY`                    | `gpt-4o-mini`                 | Tool-calling agent (LCEL) |
| `none`         | —                                   | —                             | Deterministic keyword router (offline) |
| *(unset)*      | auto-detect from any key present    | as above                      | Falls back to `none` if no keys |

Override the model with `ANTHROPIC_MODEL` / `OPENAI_MODEL`.

**Whenever the response involves a specific recommendation (investments, debt
payoff, large purchases, retirement projections, budget plans), the
"NOT financial advice" disclaimer is appended automatically.**

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | auto-detect | `anthropic`, `openai`, or `none` |
| `ANTHROPIC_API_KEY` | — | Anthropic API key for the Claude provider |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5-20251001` | Override the Claude model id |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Override the OpenAI model id |
| `PORT` | `5000` | Port for the Flask dev server / gunicorn |
| `FLASK_DEBUG` | `1` | Set to `0` to disable Werkzeug debug mode |

A ready-to-edit template lives at `.env.example`.

## Docker

```bash
make docker-build
make docker-run

# ...or directly
docker build -t finance-advisor:dev .
docker run --rm -p 5000:5000 --env-file .env finance-advisor:dev
```

The image is based on `python:3.12-slim`, installs runtime deps from
`requirements.txt`, drops to a non-root `app` user, and serves the Flask app
via gunicorn (`--workers 2`).

## Architecture

```
langchain-finance-advisor/
├── app/
│   ├── agents/finance_agent.py     # LCEL tool-calling agent + keyword fallback
│   ├── tools/finance_tools.py      # BaseTool implementations (Pydantic v2)
│   ├── data/finance_knowledge.py   # Dataclass-backed concept / investment / budget DB
│   └── api.py                      # Flask app factory
├── tests/test_smoke.py             # pytest smoke tests (no network)
├── docs/index.html                 # Static demo page
├── Dockerfile                      # python:3.12-slim + gunicorn
├── Makefile                        # install / dev / test / lint / docker
├── pyproject.toml                  # PEP 621 + ruff / pytest / mypy config
└── requirements.txt
```

## API endpoints

| Endpoint                         | Method | Description                                          |
| -------------------------------- | ------ | ---------------------------------------------------- |
| `/api/health`                    | GET    | Liveness probe (includes `llm_enabled`)              |
| `/api/chat`                      | POST   | `{ message, session_id?, language? }`                 |
| `/api/concepts`                  | GET    | List financial concepts                              |
| `/api/investments`               | GET    | List investment types                                |
| `/api/budget-categories`         | GET    | List budget categories                               |
| `/api/calculate/compound`        | POST   | Compound interest                                    |
| `/api/calculate/retirement`      | POST   | Retirement projection                                |
| `/api/calculate/loan`            | POST   | Loan monthly payment / total interest                |
| `/api/calculate/emergency`       | POST   | Emergency fund target                                |
| `/api/calculate/budget`          | POST   | Budget recommendation (with language)                |
| `/api/session/reset`             | POST   | `{ session_id }` — clear a session                    |

## LangChain components

- **Tools** (`langchain_core.tools.BaseTool`): `BudgetPlannerTool`,
  `CompoundInterestTool`, `RetirementCalcTool`, `InvestmentEducationTool`,
  `DebtPayoffTool`, `EmergencyFundTool`, `LoanCalculatorTool`,
  `FinancialConceptTool`, `BudgetCategoriesOverviewTool`.
- **Agent** (LangChain 0.3): `create_tool_calling_agent` + `AgentExecutor`,
  with a `ChatPromptTemplate` that bakes in the financial education
  disclaimer.
- **Memory**: a windowed `collections.deque` (no deprecated
  `ConversationBufferWindowMemory`).

## Tech stack

- **LangChain 0.3** (`langchain`, `langchain-core`, `langchain-community`)
- **Provider SDKs**: `langchain-anthropic`, `langchain-openai`
- **Flask 3.1** + `flask-cors`
- **Pydantic v2** for tool input schemas
- **Python 3.12** (PEP 585 / PEP 604 typing throughout)
- **Tooling**: `ruff`, `pytest`, `mypy`, `gunicorn`, Docker, GitHub Actions

## License

MIT. Educational project — not financial advice.

---

## 한국어 안내 (Korean)

LangChain 0.3 기반의 개인 금융 *교육용* 어시스턴트입니다. 한국어/영어/일본어를
지원하며, API 키가 있으면 Anthropic Claude 또는 OpenAI GPT를 자동 선택해
LLM + 툴콜링으로 응답합니다. 키가 없으면 내장 키워드 라우터로 폴백되어 외부
호출 없이도 동작합니다.

- 예산(50/30/20), 복리, 은퇴 시뮬레이션, 투자 교육, 부채 관리, 비상 자금,
  대출 계산 등을 제공합니다.
- 투자/부채/대규모 구매/은퇴 등 *구체적인 권유*가 포함되는 응답에는 항상
  **"NOT financial advice — 자격을 갖춘 재정 상담사와 상담하세요"**
  면책 고지가 자동 부착됩니다.

### 빠른 시작

```bash
git clone https://github.com/MUSE-CODE-SPACE/langchain-finance-advisor.git
cd langchain-finance-advisor

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env   # 필요 시 API 키 입력
python -m app.api
```

`uv` 사용자는 `uv venv --python 3.12 && uv pip install -e ".[dev]"`도 OK.
간단히 쓰려면 `make install && make dev`.

### 테스트 & 린트

```bash
make test    # pytest 스모크 테스트
make lint    # ruff check
make format  # ruff format + auto-fix
```

테스트는 `LLM_PROVIDER=none`으로 실행되어 API 키 없이도 통과합니다.
