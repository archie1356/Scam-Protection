"""
ScamShield Policy Engine

Determines appropriate response based on risk assessment.
Never automatically blocks transactions - always provides user options.
"""

from typing import Dict


class PolicyEngine:
    """
    Policy engine that determines user-facing response based on risk tier.
    
    Four response tiers:
    1. PASS - Allow with no warning
    2. SOFT_WARNING - Show warning, allow to continue
    3. DELAY_AND_CONFIRM - Require explicit confirmation
    4. HUMAN_REVIEW - Strongly recommend review, but still allow continuation
    """
    
    @staticmethod
    def get_policy_response(risk_assessment: Dict) -> Dict:
        """
        Generate policy response based on risk assessment.
        
        Args:
            risk_assessment: Output from risk_engine.assess_risk()
            
        Returns:
            Dictionary with policy decision and user messaging
        """
        risk_tier = risk_assessment['risk_tier']
        top_reasons = risk_assessment['top_reasons']
        rule_score = risk_assessment['rule_score']
        ml_probability_pct = risk_assessment['ml_probability_pct']
        
        if risk_tier == 'PASS':
            return {
                'action': 'PASS',
                'title': 'Payment Appears Normal',
                'message': 'This payment looks safe to proceed.',
                'severity': 'low',
                'show_warning': False,
                'require_confirmation': False,
                'recommend_review': False,
                'reasons': [],
                'primary_button': 'Continue Payment',
                'secondary_button': None,
                'ui_color': 'green'
            }
        
        elif risk_tier == 'SOFT_WARNING':
            return {
                'action': 'SOFT_WARNING',
                'title': 'Unusual Payment Detected',
                'message': 'This payment has some unusual signals. Please review the details carefully before proceeding.',
                'severity': 'medium',
                'show_warning': True,
                'require_confirmation': False,
                'recommend_review': False,
                'reasons': top_reasons,
                'risk_score': rule_score,
                'primary_button': 'Continue Payment',
                'secondary_button': 'Cancel Payment',
                'ui_color': 'yellow',
                'additional_info': 'If you recognize this payee and initiated this payment yourself, you may proceed.'
            }
        
        elif risk_tier == 'DELAY_AND_CONFIRM':
            return {
                'action': 'DELAY_AND_CONFIRM',
                'title': 'High-Risk Payment Detected',
                'message': 'This payment shows multiple suspicious signals. Please take a moment to verify.',
                'severity': 'high',
                'show_warning': True,
                'require_confirmation': True,
                'recommend_review': False,
                'reasons': top_reasons,
                'risk_score': rule_score,
                'confirmation_questions': [
                    'Are you currently on a phone call where someone is telling you what to do?',
                    'Did someone ask you to install a screen-sharing or remote-access app?',
                    'Are you being told this is urgent and must be done immediately?'
                ],
                'primary_button': 'I Verify This Payment',
                'secondary_button': 'Cancel Payment',
                'ui_color': 'orange',
                'additional_info': 'If you answered YES to any question above, this may be a scam. Consider ending the call and contacting your bank directly.',
                'safety_tips': [
                    'Banks never ask you to transfer money to "safe" accounts',
                    'Customer care will never ask you to install remote access apps',
                    'Take time to verify - legitimate requests can wait'
                ]
            }
        
        elif risk_tier == 'HUMAN_REVIEW':
            return {
                'action': 'HUMAN_REVIEW',
                'title': '⚠️ Critical Risk Alert',
                'message': 'This payment has multiple high-risk indicators commonly associated with fraud.',
                'severity': 'critical',
                'show_warning': True,
                'require_confirmation': True,
                'recommend_review': True,
                'reasons': top_reasons,
                'risk_score': rule_score,
                'ml_confidence': ml_probability_pct,
                'confirmation_questions': [
                    'Are you currently on a phone call where someone is guiding you through this payment?',
                    'Is someone using remote-access software to control your device?',
                    'Are you being told this is an emergency (digital arrest, account freezing, etc.)?'
                ],
                'primary_button': 'Request Human Review',
                'secondary_button': 'Cancel Payment',
                'tertiary_button': 'I Still Want To Proceed',
                'ui_color': 'red',
                'additional_info': 'STOP: This transaction pattern is commonly used in coached-payment fraud. We strongly recommend independent verification.',
                'safety_tips': [
                    'End any active calls immediately',
                    'Close any remote-access applications',
                    'Contact your bank directly using the official number',
                    'Do NOT use contact information provided by the caller',
                    'Legitimate organizations will never pressure you like this'
                ],
                'warning_banner': 'This appears to be a coached-payment scam. Your money may be at risk.'
            }
        
        else:
            # Fallback
            return {
                'action': 'SOFT_WARNING',
                'title': 'Please Review',
                'message': 'Please review this payment carefully.',
                'severity': 'medium',
                'show_warning': True,
                'require_confirmation': False,
                'recommend_review': False,
                'reasons': top_reasons,
                'primary_button': 'Continue',
                'secondary_button': 'Cancel',
                'ui_color': 'yellow'
            }
    
    @staticmethod
    def format_response_for_display(policy_response: Dict) -> str:
        """
        Format policy response as human-readable text.
        Useful for CLI or debugging.
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"POLICY DECISION: {policy_response['action']}")
        lines.append("=" * 60)
        lines.append(f"\n{policy_response['title']}")
        lines.append(f"{policy_response['message']}")
        
        if policy_response.get('reasons'):
            lines.append("\nReasons:")
            for i, reason in enumerate(policy_response['reasons'], 1):
                lines.append(f"  {i}. {reason}")
        
        if policy_response.get('risk_score') is not None:
            lines.append(f"\nRisk Score: {policy_response['risk_score']}")
        
        if policy_response.get('safety_tips'):
            lines.append("\nSafety Tips:")
            for tip in policy_response['safety_tips']:
                lines.append(f"  • {tip}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


def get_policy_decision(risk_assessment: Dict) -> Dict:
    """
    Convenience function to get policy decision.
    
    Args:
        risk_assessment: Output from risk_engine.assess_risk()
        
    Returns:
        Policy response dictionary
    """
    engine = PolicyEngine()
    return engine.get_policy_response(risk_assessment)
