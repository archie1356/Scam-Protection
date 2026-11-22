"""
ScamShield Risk Engine

Combines ML predictions with transparent rule-based scoring
to provide explainable risk assessment.
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Tuple, List


class RiskEngine:
    """
    Risk assessment engine that combines:
    1. Machine Learning probability score
    2. Transparent rule-based score
    3. Risk tier classification
    """
    
    # Rule-based scoring weights
    RULE_WEIGHTS = {
        'call_active': 15,
        'remote_app_present': 25,
        'payee_is_new': 15,
        'payee_age_recent': 10,  # Age < 7 days
        'amount_high': 20,  # Ratio > 5x
        'long_confirmation': 10,  # > 15 seconds
        'payee_reported': 25,  # Has reports
    }
    
    # Risk tier thresholds
    RISK_TIERS = {
        'PASS': (0, 24),
        'SOFT_WARNING': (25, 44),
        'DELAY_AND_CONFIRM': (45, 69),
        'HUMAN_REVIEW': (70, float('inf'))
    }
    
    def __init__(self, model_path='models/scamshield_model.joblib',
                 scaler_path='models/scamshield_scaler.joblib',
                 features_path='models/feature_names.joblib'):
        """Initialize risk engine with trained model."""
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        # Load model if available
        if Path(model_path).exists():
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_names = joblib.load(features_path)
    
    def calculate_rule_score(self, features: Dict) -> Tuple[int, List[Dict]]:
        """
        Calculate transparent rule-based risk score.
        
        Returns:
            tuple: (total_score, list of triggered rules with details)
        """
        total_score = 0
        triggered_rules = []
        
        # Check: Active call
        if features.get('call_active', 0) == 1:
            points = self.RULE_WEIGHTS['call_active']
            total_score += points
            triggered_rules.append({
                'rule': 'call_active',
                'description': 'An active call was detected during this payment',
                'points': points
            })
        
        # Check: Remote access app
        if features.get('remote_app_present', 0) == 1:
            points = self.RULE_WEIGHTS['remote_app_present']
            total_score += points
            triggered_rules.append({
                'rule': 'remote_app_present',
                'description': 'A remote-access application appears to be active',
                'points': points
            })
        
        # Check: New payee
        if features.get('payee_is_new', 0) == 1:
            points = self.RULE_WEIGHTS['payee_is_new']
            total_score += points
            triggered_rules.append({
                'rule': 'payee_is_new',
                'description': 'This payee is new',
                'points': points
            })
        
        # Check: Payee age (if very recent)
        payee_age = features.get('payee_age_days', 999)
        if payee_age < 7:
            points = self.RULE_WEIGHTS['payee_age_recent']
            total_score += points
            triggered_rules.append({
                'rule': 'payee_age_recent',
                'description': f'Payee was added only {payee_age} day(s) ago',
                'points': points
            })
        
        # Check: High amount ratio
        amount_ratio = features.get('amount_ratio_to_usual', 1.0)
        if amount_ratio > 5.0:
            points = self.RULE_WEIGHTS['amount_high']
            total_score += points
            triggered_rules.append({
                'rule': 'amount_high',
                'description': f'Payment amount is {amount_ratio:.1f}x higher than your usual amount',
                'points': points
            })
        
        # Check: Long confirmation screen time
        seconds_on_screen = features.get('seconds_on_confirm_screen', 0)
        if seconds_on_screen > 15:
            points = self.RULE_WEIGHTS['long_confirmation']
            total_score += points
            triggered_rules.append({
                'rule': 'long_confirmation',
                'description': f'You have been on the confirmation screen for {seconds_on_screen} seconds',
                'points': points
            })
        
        # Check: Payee has reports
        reported_count = features.get('payee_reported_count', 0)
        if reported_count > 0:
            points = self.RULE_WEIGHTS['payee_reported']
            total_score += points
            triggered_rules.append({
                'rule': 'payee_reported',
                'description': f'This payee has {reported_count} previous report(s)',
                'points': points
            })
        
        return total_score, triggered_rules
    
    def get_ml_probability(self, features: Dict) -> float:
        """
        Get ML model prediction probability.
        
        Returns:
            float: Probability of scam (0.0 to 1.0)
        """
        if self.model is None:
            return 0.0
        
        # Convert features dict to array in correct order
        feature_array = np.array([[
            features.get(fname, 0) for fname in self.feature_names
        ]])
        
        # Scale features
        feature_array_scaled = self.scaler.transform(feature_array)
        
        # Get probability
        probability = self.model.predict_proba(feature_array_scaled)[0, 1]
        
        return float(probability)
    
    def determine_risk_tier(self, rule_score: int, ml_probability: float) -> str:
        """
        Determine risk tier based on rule score and ML probability.
        
        The rule score is the primary determinant, with ML probability
        as a secondary factor for borderline cases.
        """
        # Primary: use rule score
        for tier, (min_score, max_score) in self.RISK_TIERS.items():
            if min_score <= rule_score <= max_score:
                base_tier = tier
                break
        else:
            base_tier = 'PASS'
        
        # Secondary: adjust for very high ML probability
        # If ML is very confident (>0.8) and rule score is borderline, escalate
        if ml_probability > 0.8:
            if base_tier == 'PASS' and rule_score > 15:
                base_tier = 'SOFT_WARNING'
            elif base_tier == 'SOFT_WARNING' and rule_score > 35:
                base_tier = 'DELAY_AND_CONFIRM'
        
        return base_tier
    
    def get_top_reasons(self, triggered_rules: List[Dict], top_n: int = 3) -> List[str]:
        """
        Get top N reasons for risk assessment.
        Sorted by rule points (importance).
        """
        # Sort by points
        sorted_rules = sorted(triggered_rules, key=lambda x: x['points'], reverse=True)
        
        # Get top N descriptions
        top_reasons = [rule['description'] for rule in sorted_rules[:top_n]]
        
        return top_reasons
    
    def assess_risk(self, features: Dict) -> Dict:
        """
        Comprehensive risk assessment combining all signals.
        
        Args:
            features: Dictionary with transaction features
            
        Returns:
            Dictionary with complete risk assessment
        """
        # Calculate rule-based score
        rule_score, triggered_rules = self.calculate_rule_score(features)
        
        # Get ML probability
        ml_probability = self.get_ml_probability(features)
        
        # Determine risk tier
        risk_tier = self.determine_risk_tier(rule_score, ml_probability)
        
        # Get top reasons
        top_reasons = self.get_top_reasons(triggered_rules, top_n=3)
        
        # Compile assessment
        assessment = {
            'risk_tier': risk_tier,
            'rule_score': rule_score,
            'ml_probability': ml_probability,
            'ml_probability_pct': ml_probability * 100,
            'triggered_rules': triggered_rules,
            'top_reasons': top_reasons,
            'num_triggered_rules': len(triggered_rules)
        }
        
        return assessment


def load_risk_engine():
    """Helper function to load a configured risk engine."""
    return RiskEngine()


# Convenience function for direct risk assessment
def assess_transaction_risk(features: Dict) -> Dict:
    """
    Assess risk for a single transaction.
    
    Args:
        features: Dictionary with transaction features
        
    Returns:
        Complete risk assessment
    """
    engine = load_risk_engine()
    return engine.assess_risk(features)
