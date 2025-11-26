"""
Flask API for Finance Advisor
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime

from app.agents.finance_agent import FinanceAdvisorAgent, create_finance_agent
from app.data.finance_knowledge import (
    CONCEPTS_DB, INVESTMENTS_DB, BUDGET_CATEGORIES,
    calculate_compound_interest, calculate_retirement_savings,
    calculate_loan_payment, get_budget_recommendation
)


def create_app():
    app = Flask(__name__,
                static_folder='../static',
                template_folder='../templates')
    CORS(app)

    agents = {}

    def get_agent(session_id: str, language: str = "en") -> FinanceAdvisorAgent:
        key = f"{session_id}_{language}"
        if key not in agents:
            agents[key] = create_finance_agent(language=language)
        return agents[key]

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'finance-advisor',
            'timestamp': datetime.utcnow().isoformat()
        })

    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.json
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        language = data.get('language', 'en')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        try:
            agent = get_agent(session_id, language)
            response = agent.chat(message)

            return jsonify({
                'response': response,
                'session_id': session_id,
                'language': language
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/concepts', methods=['GET'])
    def list_concepts():
        """List all financial concepts."""
        lang = request.args.get('lang', 'en')
        concepts = []
        for key, concept in CONCEPTS_DB.items():
            concepts.append({
                'id': key,
                'name': concept.name.get(lang, concept.name['en']),
                'description': concept.description.get(lang, concept.description['en'])
            })
        return jsonify({'concepts': concepts})

    @app.route('/api/investments', methods=['GET'])
    def list_investments():
        """List all investment types."""
        lang = request.args.get('lang', 'en')
        investments = []
        for key, inv in INVESTMENTS_DB.items():
            investments.append({
                'id': key,
                'name': inv.name.get(lang, inv.name['en']),
                'description': inv.description.get(lang, inv.description['en']),
                'risk_level': inv.risk_level.value,
                'typical_returns': inv.typical_returns
            })
        return jsonify({'investments': investments})

    @app.route('/api/budget-categories', methods=['GET'])
    def list_budget_categories():
        """List budget categories."""
        lang = request.args.get('lang', 'en')
        categories = []
        for cat in BUDGET_CATEGORIES:
            categories.append({
                'id': cat.id,
                'name': cat.name.get(lang, cat.name['en']),
                'description': cat.description.get(lang, cat.description['en']),
                'recommended_percent': cat.recommended_percent,
                'tips': cat.tips.get(lang, cat.tips['en'])
            })
        return jsonify({'categories': categories})

    @app.route('/api/calculate/compound-interest', methods=['POST'])
    def calc_compound_interest():
        """Calculate compound interest."""
        data = request.json
        try:
            result = calculate_compound_interest(
                principal=float(data.get('principal', 0)),
                annual_rate=float(data.get('annual_rate', 0)),
                years=int(data.get('years', 0)),
                compounds_per_year=int(data.get('compounds_per_year', 12))
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/calculate/retirement', methods=['POST'])
    def calc_retirement():
        """Calculate retirement savings projection."""
        data = request.json
        try:
            result = calculate_retirement_savings(
                current_age=int(data.get('current_age', 30)),
                retirement_age=int(data.get('retirement_age', 65)),
                monthly_contribution=float(data.get('monthly_contribution', 0)),
                current_savings=float(data.get('current_savings', 0)),
                annual_return=float(data.get('annual_return', 7.0))
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/calculate/loan', methods=['POST'])
    def calc_loan():
        """Calculate loan payment."""
        data = request.json
        try:
            result = calculate_loan_payment(
                principal=float(data.get('principal', 0)),
                annual_rate=float(data.get('annual_rate', 0)),
                years=int(data.get('years', 0))
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/calculate/budget', methods=['POST'])
    def calc_budget():
        """Get budget recommendations."""
        data = request.json
        lang = data.get('language', 'en')
        try:
            result = get_budget_recommendation(
                monthly_income=float(data.get('monthly_income', 0))
            )
            # Apply language
            for cat_id, cat_data in result["categories"].items():
                cat_data["name"] = cat_data["name"].get(lang, cat_data["name"].get("en"))
                cat_data["tips"] = cat_data["tips"].get(lang, cat_data["tips"].get("en"))
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/session/reset', methods=['POST'])
    def reset_session():
        data = request.json
        session_id = data.get('session_id', 'default')
        language = data.get('language', 'en')

        key = f"{session_id}_{language}"
        if key in agents:
            agents[key].reset()
            del agents[key]

        return jsonify({'status': 'reset', 'session_id': session_id})

    return app


app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
