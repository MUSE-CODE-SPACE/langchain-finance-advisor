"""
Flask API for the Finance Advisor.

DISCLAIMER: This service exposes a *personal-finance education* assistant.
It does NOT provide personalised financial advice. See README and in-app
disclaimers.

Run for development with:

    python -m app.api

For production, prefer running through gunicorn:

    gunicorn --bind 0.0.0.0:5000 --workers 2 app.api:app
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

from app.agents.finance_agent import FinanceAdvisorAgent, create_finance_agent
from app.data.finance_knowledge import (
    BUDGET_CATEGORIES,
    CONCEPTS_DB,
    INVESTMENTS_DB,
    calculate_compound_interest,
    calculate_loan_payment,
    calculate_retirement_savings,
    get_budget_recommendation,
)

load_dotenv()

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATE_DIR = _REPO_ROOT / "templates"
_STATIC_DIR = _REPO_ROOT / "static"
_DOCS_DIR = _REPO_ROOT / "docs"


def create_app() -> Flask:
    """Application factory."""
    app = Flask(
        __name__,
        static_folder=str(_STATIC_DIR) if _STATIC_DIR.exists() else None,
        template_folder=str(_TEMPLATE_DIR) if _TEMPLATE_DIR.exists() else None,
    )
    CORS(app)

    agents: dict[str, FinanceAdvisorAgent] = {}

    def get_agent(session_id: str, language: str = "en") -> FinanceAdvisorAgent:
        key = f"{session_id}_{language}"
        if key not in agents:
            agents[key] = create_finance_agent(language=language)
        return agents[key]

    @app.route("/")
    def index():
        if _TEMPLATE_DIR.exists() and (_TEMPLATE_DIR / "index.html").exists():
            return render_template("index.html")
        if (_DOCS_DIR / "index.html").exists():
            return send_from_directory(str(_DOCS_DIR), "index.html")
        return jsonify(
            {
                "service": "finance-advisor",
                "message": (
                    "Finance Advisor API. POST /api/chat with "
                    '{"message": "..."} to talk to the assistant. '
                    "Educational use only — NOT financial advice."
                ),
                "endpoints": [
                    "GET /api/health",
                    "POST /api/chat",
                    "GET /api/concepts",
                    "GET /api/investments",
                    "GET /api/budget-categories",
                    "POST /api/calculate/compound",
                    "POST /api/calculate/retirement",
                    "POST /api/calculate/loan",
                    "POST /api/calculate/emergency",
                    "POST /api/calculate/budget",
                    "POST /api/session/reset",
                ],
            }
        )

    @app.route("/static/<path:filename>")
    def serve_static(filename: str):
        if app.static_folder is None:
            return jsonify({"error": "static assets not available"}), 404
        return send_from_directory(app.static_folder, filename)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        sample_agent = next(iter(agents.values()), None)
        llm_enabled = sample_agent.llm_enabled if sample_agent is not None else False
        return jsonify(
            {
                "status": "healthy",
                "service": "finance-advisor",
                "timestamp": datetime.now(UTC).isoformat(),
                "active_sessions": len(agents),
                "llm_enabled": llm_enabled,
            }
        )

    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json(silent=True) or {}
        session_id = data.get("session_id", "default")
        message = data.get("message", "")
        language = data.get("language", "en")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        try:
            agent = get_agent(session_id, language)
            response = agent.chat(message)
            return jsonify(
                {
                    "response": response,
                    "session_id": session_id,
                    "language": language,
                    "llm_enabled": agent.llm_enabled,
                    "mode": getattr(agent, "mode", "unknown"),
                }
            )
        except Exception as exc:
            logger.exception("Chat request failed")
            return jsonify({"error": str(exc)}), 500

    # -- read-only knowledge endpoints -----------------------------------

    @app.route("/api/concepts", methods=["GET"])
    def list_concepts():
        lang = request.args.get("lang", "en")
        concepts = [
            {
                "id": key,
                "name": concept.name.get(lang, concept.name["en"]),
                "description": concept.description.get(lang, concept.description["en"]),
            }
            for key, concept in CONCEPTS_DB.items()
        ]
        return jsonify({"concepts": concepts})

    @app.route("/api/investments", methods=["GET"])
    def list_investments():
        lang = request.args.get("lang", "en")
        investments = [
            {
                "id": key,
                "name": inv.name.get(lang, inv.name["en"]),
                "description": inv.description.get(lang, inv.description["en"]),
                "risk_level": inv.risk_level.value,
                "typical_returns": inv.typical_returns,
            }
            for key, inv in INVESTMENTS_DB.items()
        ]
        return jsonify({"investments": investments})

    @app.route("/api/budget-categories", methods=["GET"])
    def list_budget_categories():
        lang = request.args.get("lang", "en")
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
        return jsonify({"categories": categories})

    # -- calculator endpoints --------------------------------------------

    @app.route("/api/calculate/compound", methods=["POST"])
    def calc_compound():
        data = request.get_json(silent=True) or {}
        try:
            result = calculate_compound_interest(
                principal=float(data.get("principal", 0)),
                annual_rate=float(data.get("annual_rate", 0)),
                years=int(data.get("years", 0)),
                compounds_per_year=int(data.get("compounds_per_year", 12)),
            )
            return jsonify(result)
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/calculate/retirement", methods=["POST"])
    def calc_retirement():
        data = request.get_json(silent=True) or {}
        try:
            result = calculate_retirement_savings(
                current_age=int(data.get("current_age", 30)),
                retirement_age=int(data.get("retirement_age", 65)),
                monthly_contribution=float(data.get("monthly_contribution", 0)),
                current_savings=float(data.get("current_savings", 0)),
                annual_return=float(data.get("annual_return", 7.0)),
            )
            return jsonify(result)
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/calculate/loan", methods=["POST"])
    def calc_loan():
        data = request.get_json(silent=True) or {}
        try:
            result = calculate_loan_payment(
                principal=float(data.get("principal", 0)),
                annual_rate=float(data.get("annual_rate", 0)),
                years=int(data.get("years", 0)),
            )
            return jsonify(result)
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/calculate/emergency", methods=["POST"])
    def calc_emergency():
        data = request.get_json(silent=True) or {}
        try:
            monthly_expenses = float(data.get("monthly_expenses", 0))
            months = int(data.get("months", 6))
            if monthly_expenses <= 0 or months <= 0:
                return jsonify({"error": "monthly_expenses and months must be positive"}), 400
            return jsonify(
                {
                    "monthly_expenses": monthly_expenses,
                    "months_of_coverage": months,
                    "target_emergency_fund": round(monthly_expenses * months, 2),
                }
            )
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/calculate/budget", methods=["POST"])
    def calc_budget():
        data = request.get_json(silent=True) or {}
        lang = data.get("language", "en")
        try:
            result = get_budget_recommendation(
                monthly_income=float(data.get("monthly_income", 0))
            )
            for _cat_id, cat_data in result["categories"].items():
                cat_data["name"] = cat_data["name"].get(lang, cat_data["name"].get("en"))
                cat_data["tips"] = cat_data["tips"].get(lang, cat_data["tips"].get("en"))
            return jsonify(result)
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/session/reset", methods=["POST"])
    def reset_session():
        data = request.get_json(silent=True) or {}
        session_id = data.get("session_id", "default")
        language = data.get("language", "en")

        key = f"{session_id}_{language}"
        if key in agents:
            agents[key].reset()
            del agents[key]

        return jsonify({"status": "reset", "session_id": session_id})

    return app


app = create_app()


if __name__ == "__main__":
    # Dev server only. Use gunicorn in production (see Dockerfile / README).
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
