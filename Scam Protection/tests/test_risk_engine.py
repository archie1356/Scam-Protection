"""
Tests for Risk Engine
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from risk_engine import RiskEngine


def test_rule_score_calculation():
    """Test rule-based scoring."""
    engine = RiskEngine()
    
    # Test 1: Clean transaction
    features = {
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 100,
        'amount_ratio_to_usual': 1.0,
        'seconds_on_confirm_screen': 5,
        'payee_reported_count': 0,
        'time_of_day': 14
    }
    
    score, rules = engine.calculate_rule_score(features)
    assert score == 0, "Clean transaction should have 0 score"
    assert len(rules) == 0, "Clean transaction should trigger no rules"
    
    # Test 2: High-risk transaction
    features_risky = {
        'call_active': 1,
        'remote_app_present': 1,
        'payee_is_new': 1,
        'payee_age_days': 2,
        'amount_ratio_to_usual': 10.0,
        'seconds_on_confirm_screen': 30,
        'payee_reported_count': 5,
        'time_of_day': 20
    }
    
    score, rules = engine.calculate_rule_score(features_risky)
    assert score > 70, "High-risk transaction should have high score"
    assert len(rules) >= 5, "High-risk transaction should trigger multiple rules"
    
    print("✓ Rule score calculation tests passed")


def test_risk_tier_determination():
    """Test risk tier classification."""
    engine = RiskEngine()
    
    # Test tier boundaries
    assert engine.determine_risk_tier(10, 0.2) == 'PASS'
    assert engine.determine_risk_tier(30, 0.3) == 'SOFT_WARNING'
    assert engine.determine_risk_tier(50, 0.5) == 'DELAY_AND_CONFIRM'
    assert engine.determine_risk_tier(75, 0.7) == 'HUMAN_REVIEW'
    
    print("✓ Risk tier determination tests passed")


def test_top_reasons_extraction():
    """Test extraction of top reasons."""
    engine = RiskEngine()
    
    features = {
        'call_active': 1,
        'remote_app_present': 1,
        'payee_is_new': 1,
        'payee_age_days': 100,
        'amount_ratio_to_usual': 2.0,
        'seconds_on_confirm_screen': 5,
        'payee_reported_count': 0,
        'time_of_day': 14
    }
    
    _, rules = engine.calculate_rule_score(features)
    top_reasons = engine.get_top_reasons(rules, top_n=2)
    
    assert len(top_reasons) <= 2, "Should return at most 2 reasons"
    assert all(isinstance(r, str) for r in top_reasons), "Reasons should be strings"
    
    print("✓ Top reasons extraction tests passed")


def test_complete_assessment():
    """Test complete risk assessment."""
    engine = RiskEngine()
    
    features = {
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 2,
        'amount_ratio_to_usual': 8.0,
        'seconds_on_confirm_screen': 25,
        'payee_reported_count': 0,
        'time_of_day': 15
    }
    
    assessment = engine.assess_risk(features)
    
    # Check all required fields present
    required_fields = [
        'risk_tier', 'rule_score', 'ml_probability',
        'triggered_rules', 'top_reasons', 'num_triggered_rules'
    ]
    
    for field in required_fields:
        assert field in assessment, f"Assessment missing field: {field}"
    
    assert assessment['risk_tier'] in ['PASS', 'SOFT_WARNING', 'DELAY_AND_CONFIRM', 'HUMAN_REVIEW']
    assert 0 <= assessment['ml_probability'] <= 1.0
    assert assessment['rule_score'] >= 0
    
    print("✓ Complete assessment tests passed")


if __name__ == "__main__":
    test_rule_score_calculation()
    test_risk_tier_determination()
    test_top_reasons_extraction()
    test_complete_assessment()
    print("\n✓ All risk engine tests passed!")
