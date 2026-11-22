"""
Tests for Policy Engine
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from policy_engine import PolicyEngine


def test_pass_tier_response():
    """Test PASS tier policy response."""
    engine = PolicyEngine()
    
    risk_assessment = {
        'risk_tier': 'PASS',
        'rule_score': 10,
        'ml_probability': 0.1,
        'ml_probability_pct': 10.0,
        'top_reasons': [],
        'num_triggered_rules': 0
    }
    
    response = engine.get_policy_response(risk_assessment)
    
    assert response['action'] == 'PASS'
    assert response['show_warning'] == False
    assert response['require_confirmation'] == False
    assert response['severity'] == 'low'
    
    print("✓ PASS tier response test passed")


def test_soft_warning_response():
    """Test SOFT_WARNING tier policy response."""
    engine = PolicyEngine()
    
    risk_assessment = {
        'risk_tier': 'SOFT_WARNING',
        'rule_score': 30,
        'ml_probability': 0.4,
        'ml_probability_pct': 40.0,
        'top_reasons': ['Active call detected'],
        'num_triggered_rules': 1
    }
    
    response = engine.get_policy_response(risk_assessment)
    
    assert response['action'] == 'SOFT_WARNING'
    assert response['show_warning'] == True
    assert response['require_confirmation'] == False
    assert response['severity'] == 'medium'
    assert len(response['reasons']) > 0
    
    print("✓ SOFT_WARNING response test passed")


def test_delay_and_confirm_response():
    """Test DELAY_AND_CONFIRM tier policy response."""
    engine = PolicyEngine()
    
    risk_assessment = {
        'risk_tier': 'DELAY_AND_CONFIRM',
        'rule_score': 55,
        'ml_probability': 0.7,
        'ml_probability_pct': 70.0,
        'top_reasons': [
            'Active call detected',
            'Payee is new',
            'High amount ratio'
        ],
        'num_triggered_rules': 3
    }
    
    response = engine.get_policy_response(risk_assessment)
    
    assert response['action'] == 'DELAY_AND_CONFIRM'
    assert response['show_warning'] == True
    assert response['require_confirmation'] == True
    assert response['severity'] == 'high'
    assert 'confirmation_questions' in response
    assert len(response['confirmation_questions']) > 0
    
    print("✓ DELAY_AND_CONFIRM response test passed")


def test_human_review_response():
    """Test HUMAN_REVIEW tier policy response."""
    engine = PolicyEngine()
    
    risk_assessment = {
        'risk_tier': 'HUMAN_REVIEW',
        'rule_score': 85,
        'ml_probability': 0.9,
        'ml_probability_pct': 90.0,
        'top_reasons': [
            'Remote access app detected',
            'Active call detected',
            'Payee has reports'
        ],
        'num_triggered_rules': 5
    }
    
    response = engine.get_policy_response(risk_assessment)
    
    assert response['action'] == 'HUMAN_REVIEW'
    assert response['show_warning'] == True
    assert response['require_confirmation'] == True
    assert response['recommend_review'] == True
    assert response['severity'] == 'critical'
    assert 'safety_tips' in response
    assert len(response['safety_tips']) > 0
    
    print("✓ HUMAN_REVIEW response test passed")


def test_response_formatting():
    """Test response formatting for display."""
    engine = PolicyEngine()
    
    risk_assessment = {
        'risk_tier': 'SOFT_WARNING',
        'rule_score': 30,
        'ml_probability': 0.4,
        'ml_probability_pct': 40.0,
        'top_reasons': ['Test reason'],
        'num_triggered_rules': 1
    }
    
    response = engine.get_policy_response(risk_assessment)
    formatted = engine.format_response_for_display(response)
    
    assert isinstance(formatted, str)
    assert len(formatted) > 0
    assert 'SOFT_WARNING' in formatted
    
    print("✓ Response formatting test passed")


if __name__ == "__main__":
    test_pass_tier_response()
    test_soft_warning_response()
    test_delay_and_confirm_response()
    test_human_review_response()
    test_response_formatting()
    print("\n✓ All policy engine tests passed!")
