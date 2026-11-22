"""
ScamShield Model Evaluation

Evaluates the complete pipeline on test cases and demo scenarios.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from risk_engine import RiskEngine
from policy_engine import PolicyEngine


def generate_demo_cases():
    """
    Generate 25 carefully selected demo cases for showcasing.
    
    Mix of:
    - 10 normal cases
    - 10 scam cases
    - 5 edge cases
    """
    cases = []
    
    # === NORMAL CASES (10) ===
    
    # 1. Typical normal payment
    cases.append({
        'case_id': 'N001',
        'description': 'Regular payment to known merchant',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 180,
        'amount_ratio_to_usual': 1.2,
        'seconds_on_confirm_screen': 5,
        'payee_reported_count': 0,
        'time_of_day': 14,
        'expected_label': 0
    })
    
    # 2. Payment to established payee
    cases.append({
        'case_id': 'N002',
        'description': 'Monthly bill payment',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 365,
        'amount_ratio_to_usual': 0.95,
        'seconds_on_confirm_screen': 3,
        'payee_reported_count': 0,
        'time_of_day': 10,
        'expected_label': 0
    })
    
    # 3. New legitimate payee
    cases.append({
        'case_id': 'N003',
        'description': 'First payment to new utility company',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 2,
        'amount_ratio_to_usual': 1.5,
        'seconds_on_confirm_screen': 8,
        'payee_reported_count': 0,
        'time_of_day': 16,
        'expected_label': 0
    })
    
    # 4. Legitimate large payment
    cases.append({
        'case_id': 'N004',
        'description': 'Annual insurance premium',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 400,
        'amount_ratio_to_usual': 8.5,
        'seconds_on_confirm_screen': 12,
        'payee_reported_count': 0,
        'time_of_day': 11,
        'expected_label': 0
    })
    
    # 5. Payment during unrelated call
    cases.append({
        'case_id': 'N005',
        'description': 'Normal payment while on call with friend',
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 90,
        'amount_ratio_to_usual': 1.1,
        'seconds_on_confirm_screen': 4,
        'payee_reported_count': 0,
        'time_of_day': 19,
        'expected_label': 0
    })
    
    # 6-10: More normal cases
    for i in range(6, 11):
        cases.append({
            'case_id': f'N{i:03d}',
            'description': f'Normal transaction variant {i}',
            'call_active': 0,
            'remote_app_present': 0,
            'payee_is_new': 0 if i % 3 != 0 else 1,
            'payee_age_days': np.random.randint(30, 500),
            'amount_ratio_to_usual': np.random.uniform(0.5, 2.5),
            'seconds_on_confirm_screen': np.random.randint(3, 12),
            'payee_reported_count': 0,
            'time_of_day': np.random.randint(8, 22),
            'expected_label': 0
        })
    
    # === SCAM CASES (10) ===
    
    # 11. Classic coached payment scam
    cases.append({
        'case_id': 'S001',
        'description': 'Active call + new payee + large amount',
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 0,
        'amount_ratio_to_usual': 12.0,
        'seconds_on_confirm_screen': 25,
        'payee_reported_count': 0,
        'time_of_day': 15,
        'expected_label': 1
    })
    
    # 12. Remote access scam
    cases.append({
        'case_id': 'S002',
        'description': 'Remote app + new payee + coaching',
        'call_active': 1,
        'remote_app_present': 1,
        'payee_is_new': 1,
        'payee_age_days': 0,
        'amount_ratio_to_usual': 7.5,
        'seconds_on_confirm_screen': 35,
        'payee_reported_count': 3,
        'time_of_day': 13,
        'expected_label': 1
    })
    
    # 13. Reported payee scam
    cases.append({
        'case_id': 'S003',
        'description': 'Known scammer payee',
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 1,
        'amount_ratio_to_usual': 5.5,
        'seconds_on_confirm_screen': 18,
        'payee_reported_count': 12,
        'time_of_day': 10,
        'expected_label': 1
    })
    
    # 14. High-risk multiple signals
    cases.append({
        'case_id': 'S004',
        'description': 'All risk signals present',
        'call_active': 1,
        'remote_app_present': 1,
        'payee_is_new': 1,
        'payee_age_days': 0,
        'amount_ratio_to_usual': 15.0,
        'seconds_on_confirm_screen': 45,
        'payee_reported_count': 8,
        'time_of_day': 20,
        'expected_label': 1
    })
    
    # 15. Subtle scam - fewer signals
    cases.append({
        'case_id': 'S005',
        'description': 'Scam with normal amount',
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 1,
        'amount_ratio_to_usual': 2.0,
        'seconds_on_confirm_screen': 22,
        'payee_reported_count': 0,
        'time_of_day': 14,
        'expected_label': 1
    })
    
    # 16-20: More scam variations
    scam_configs = [
        {'call': 1, 'remote': 1, 'new': 1, 'amount': 10.0},
        {'call': 1, 'remote': 0, 'new': 1, 'amount': 8.5},
        {'call': 0, 'remote': 1, 'new': 1, 'amount': 6.0},
        {'call': 1, 'remote': 1, 'new': 0, 'amount': 7.0},
        {'call': 1, 'remote': 0, 'new': 1, 'amount': 4.5},
    ]
    
    for i, config in enumerate(scam_configs, start=6):
        cases.append({
            'case_id': f'S{i:03d}',
            'description': f'Scam variant {i}',
            'call_active': config['call'],
            'remote_app_present': config['remote'],
            'payee_is_new': config['new'],
            'payee_age_days': np.random.randint(0, 5),
            'amount_ratio_to_usual': config['amount'],
            'seconds_on_confirm_screen': np.random.randint(15, 40),
            'payee_reported_count': np.random.choice([0, 0, 0, 1, 3, 5]),
            'time_of_day': np.random.randint(9, 21),
            'expected_label': 1
        })
    
    # === EDGE CASES (5) ===
    
    # 21. Legitimate but looks suspicious
    cases.append({
        'case_id': 'E001',
        'description': 'New payee + large amount (but legitimate)',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 3,
        'amount_ratio_to_usual': 6.0,
        'seconds_on_confirm_screen': 15,
        'payee_reported_count': 0,
        'time_of_day': 11,
        'expected_label': 0
    })
    
    # 22. Careful user, long review time
    cases.append({
        'case_id': 'E002',
        'description': 'Careful user taking time (legitimate)',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 200,
        'amount_ratio_to_usual': 1.8,
        'seconds_on_confirm_screen': 35,
        'payee_reported_count': 0,
        'time_of_day': 16,
        'expected_label': 0
    })
    
    # 23. False report on legitimate payee
    cases.append({
        'case_id': 'E003',
        'description': 'Legitimate payee with false report',
        'call_active': 0,
        'remote_app_present': 0,
        'payee_is_new': 0,
        'payee_age_days': 450,
        'amount_ratio_to_usual': 1.2,
        'seconds_on_confirm_screen': 6,
        'payee_reported_count': 1,
        'time_of_day': 13,
        'expected_label': 0
    })
    
    # 24. Borderline case
    cases.append({
        'case_id': 'E004',
        'description': 'Borderline - hard to classify',
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 10,
        'amount_ratio_to_usual': 3.5,
        'seconds_on_confirm_screen': 12,
        'payee_reported_count': 0,
        'time_of_day': 17,
        'expected_label': 0  # Could go either way
    })
    
    # 25. Low-sophistication scam
    cases.append({
        'case_id': 'E005',
        'description': 'Simple scam with few obvious signals',
        'call_active': 1,
        'remote_app_present': 0,
        'payee_is_new': 1,
        'payee_age_days': 0,
        'amount_ratio_to_usual': 3.0,
        'seconds_on_confirm_screen': 18,
        'payee_reported_count': 0,
        'time_of_day': 14,
        'expected_label': 1
    })
    
    return pd.DataFrame(cases)


def evaluate_demo_cases(save_results=True):
    """
    Evaluate all demo cases through the complete pipeline.
    """
    print("\n" + "="*80)
    print("EVALUATING DEMO CASES")
    print("="*80 + "\n")
    
    # Generate cases
    demo_df = generate_demo_cases()
    print(f"✓ Generated {len(demo_df)} demo cases")
    
    # Save raw demo cases
    if save_results:
        demo_df.to_csv('data/demo_cases.csv', index=False)
        print(f"✓ Demo cases saved to data/demo_cases.csv\n")
    
    # Initialize engines
    risk_engine = RiskEngine()
    policy_engine = PolicyEngine()
    
    # Evaluate each case
    results = []
    
    for idx, row in demo_df.iterrows():
        # Extract features
        features = {
            'call_active': row['call_active'],
            'remote_app_present': row['remote_app_present'],
            'payee_is_new': row['payee_is_new'],
            'payee_age_days': row['payee_age_days'],
            'amount_ratio_to_usual': row['amount_ratio_to_usual'],
            'seconds_on_confirm_screen': row['seconds_on_confirm_screen'],
            'payee_reported_count': row['payee_reported_count'],
            'time_of_day': row['time_of_day']
        }
        
        # Assess risk
        risk_assessment = risk_engine.assess_risk(features)
        
        # Get policy
        policy_response = policy_engine.get_policy_response(risk_assessment)
        
        # Compile result
        result = {
            'case_id': row['case_id'],
            'description': row['description'],
            'expected_label': row['expected_label'],
            'ml_prediction': 1 if risk_assessment['ml_probability'] > 0.5 else 0,
            'ml_probability': risk_assessment['ml_probability'],
            'rule_score': risk_assessment['rule_score'],
            'risk_tier': risk_assessment['risk_tier'],
            'policy_action': policy_response['action'],
            'top_reason_1': risk_assessment['top_reasons'][0] if len(risk_assessment['top_reasons']) > 0 else '',
            'top_reason_2': risk_assessment['top_reasons'][1] if len(risk_assessment['top_reasons']) > 1 else '',
            'top_reason_3': risk_assessment['top_reasons'][2] if len(risk_assessment['top_reasons']) > 2 else '',
        }
        
        results.append(result)
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    if save_results:
        results_df.to_csv('data/demo_results.csv', index=False)
        print(f"✓ Results saved to data/demo_results.csv\n")
    
    # Print summary
    print_evaluation_summary(results_df)
    
    return results_df


def print_evaluation_summary(results_df):
    """Print summary of evaluation results."""
    print("="*80)
    print("DEMO EVALUATION SUMMARY")
    print("="*80 + "\n")
    
    # ML Performance
    correct_predictions = (results_df['expected_label'] == results_df['ml_prediction']).sum()
    accuracy = correct_predictions / len(results_df)
    
    print(f"ML Model Performance:")
    print(f"  Correct predictions: {correct_predictions}/{len(results_df)}")
    print(f"  Accuracy: {accuracy:.2%}")
    
    # Risk Tier Distribution
    print(f"\nRisk Tier Distribution:")
    tier_counts = results_df['risk_tier'].value_counts()
    for tier in ['PASS', 'SOFT_WARNING', 'DELAY_AND_CONFIRM', 'HUMAN_REVIEW']:
        count = tier_counts.get(tier, 0)
        print(f"  {tier:20s}: {count:2d}")
    
    # Policy Action Distribution
    print(f"\nPolicy Action Distribution:")
    action_counts = results_df['policy_action'].value_counts()
    for action in action_counts.index:
        count = action_counts[action]
        print(f"  {action:20s}: {count:2d}")
    
    print("\n" + "="*80)
    print("Selected Case Examples:")
    print("="*80 + "\n")
    
    # Show a few interesting cases
    interesting_cases = ['N001', 'N004', 'S001', 'S002', 'S004', 'E001', 'E004']
    
    for case_id in interesting_cases:
        if case_id in results_df['case_id'].values:
            case = results_df[results_df['case_id'] == case_id].iloc[0]
            print(f"{case_id}: {case['description']}")
            print(f"  → Risk Tier: {case['risk_tier']}")
            print(f"  → ML Probability: {case['ml_probability']:.2%}")
            print(f"  → Rule Score: {case['rule_score']}")
            if case['top_reason_1']:
                print(f"  → Top Reason: {case['top_reason_1']}")
            print()


if __name__ == "__main__":
    evaluate_demo_cases()
