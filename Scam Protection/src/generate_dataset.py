"""
ScamShield Synthetic Dataset Generator

This script generates 3,000 synthetic transaction/session records for training
and evaluating the coached-payment fraud detection system.

IMPORTANT: This data is entirely synthetic and does not contain any real
customer, payment, or financial information.
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path


def generate_synthetic_dataset(n_samples=3000, random_seed=42):
    """
    Generate synthetic transaction records with realistic, messy patterns.
    
    Target distribution:
    - ~2000 normal transactions (67%)
    - ~1000 scam transactions (33%)
    
    The data is intentionally NOT perfectly separable to simulate real-world complexity.
    """
    np.random.seed(random_seed)
    
    # Determine labels first (approximately 2:1 ratio normal:scam)
    # Use binomial to get natural variation around 33% scam rate
    n_scams = int(n_samples * 0.33)
    n_normal = n_samples - n_scams
    
    labels = np.concatenate([
        np.zeros(n_normal, dtype=int),  # 0 = normal
        np.ones(n_scams, dtype=int)      # 1 = scam
    ])
    
    # Shuffle labels
    np.random.shuffle(labels)
    
    # Initialize feature arrays
    data = {
        'call_active': np.zeros(n_samples, dtype=int),
        'remote_app_present': np.zeros(n_samples, dtype=int),
        'payee_is_new': np.zeros(n_samples, dtype=int),
        'payee_age_days': np.zeros(n_samples, dtype=int),
        'amount_ratio_to_usual': np.zeros(n_samples, dtype=float),
        'seconds_on_confirm_screen': np.zeros(n_samples, dtype=int),
        'payee_reported_count': np.zeros(n_samples, dtype=int),
        'time_of_day': np.zeros(n_samples, dtype=int),
        'label': labels
    }
    
    # Generate features based on whether transaction is normal or scam
    for i in range(n_samples):
        is_scam = labels[i] == 1
        
        if is_scam:
            # SCAM TRANSACTION PATTERNS
            # Not all scams have all signals - realistic variation
            
            # Call active: 85% of scams have active call
            data['call_active'][i] = 1 if np.random.random() < 0.85 else 0
            
            # Remote app: 60% of scams have remote access app
            data['remote_app_present'][i] = 1 if np.random.random() < 0.60 else 0
            
            # Payee is new: 75% of scams target new payees
            data['payee_is_new'][i] = 1 if np.random.random() < 0.75 else 0
            
            # Payee age: if new, very recent (0-14 days); if not new, older
            if data['payee_is_new'][i] == 1:
                # New payees in scams are typically very recent
                data['payee_age_days'][i] = np.random.randint(0, 8)
            else:
                # Some scams target older payees
                data['payee_age_days'][i] = np.random.randint(15, 365)
            
            # Amount ratio: 70% of scams involve unusual amounts
            if np.random.random() < 0.70:
                # Large payment: 2x to 20x usual
                data['amount_ratio_to_usual'][i] = np.random.uniform(3.0, 15.0)
            else:
                # Some scams use normal amounts to avoid detection
                data['amount_ratio_to_usual'][i] = np.random.uniform(0.5, 2.5)
            
            # Seconds on confirm screen: scammers often rush or guide slowly
            # Bimodal: either very quick or suspiciously long
            if np.random.random() < 0.6:
                # Longer hesitation (being coached)
                data['seconds_on_confirm_screen'][i] = np.random.randint(15, 60)
            else:
                # Rushed through
                data['seconds_on_confirm_screen'][i] = np.random.randint(2, 12)
            
            # Payee reported: 40% of scam payees have previous reports
            if np.random.random() < 0.40:
                data['payee_reported_count'][i] = np.random.randint(1, 15)
            else:
                data['payee_reported_count'][i] = 0
            
            # Time of day: scams can happen anytime but slightly more during day
            # Peak hours: 9 AM - 9 PM
            if np.random.random() < 0.7:
                data['time_of_day'][i] = np.random.randint(9, 22)
            else:
                data['time_of_day'][i] = np.random.randint(0, 24)
        
        else:
            # NORMAL TRANSACTION PATTERNS
            # Some normal transactions have suspicious-looking signals
            
            # Call active: 10% of normal transactions happen during unrelated calls
            data['call_active'][i] = 1 if np.random.random() < 0.10 else 0
            
            # Remote app: 2% of normal transactions (maybe work-related)
            data['remote_app_present'][i] = 1 if np.random.random() < 0.02 else 0
            
            # Payee is new: 25% of normal transactions are to new legitimate payees
            data['payee_is_new'][i] = 1 if np.random.random() < 0.25 else 0
            
            # Payee age: if new, relatively recent; if not new, well-established
            if data['payee_is_new'][i] == 1:
                # New but legitimate payees
                data['payee_age_days'][i] = np.random.randint(0, 30)
            else:
                # Established payees
                data['payee_age_days'][i] = np.random.randint(30, 1000)
            
            # Amount ratio: most normal transactions are within usual range
            # 90% within 0.3x to 3x usual
            if np.random.random() < 0.90:
                data['amount_ratio_to_usual'][i] = np.random.uniform(0.3, 3.0)
            else:
                # 10% are legitimate large payments (annual insurance, etc.)
                data['amount_ratio_to_usual'][i] = np.random.uniform(3.0, 10.0)
            
            # Seconds on confirm screen: normal behavior is quick
            # Most people spend 2-15 seconds
            if np.random.random() < 0.85:
                data['seconds_on_confirm_screen'][i] = np.random.randint(2, 15)
            else:
                # Some people are careful and take longer
                data['seconds_on_confirm_screen'][i] = np.random.randint(15, 45)
            
            # Payee reported: 5% of normal payees have had false reports
            if np.random.random() < 0.05:
                data['payee_reported_count'][i] = np.random.randint(1, 3)
            else:
                data['payee_reported_count'][i] = 0
            
            # Time of day: normal transactions throughout the day
            # Slight peak during business hours
            if np.random.random() < 0.6:
                data['time_of_day'][i] = np.random.randint(8, 23)
            else:
                data['time_of_day'][i] = np.random.randint(0, 24)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Round amount_ratio to 2 decimal places for readability
    df['amount_ratio_to_usual'] = df['amount_ratio_to_usual'].round(2)
    
    return df


def save_dataset(df, output_path='data/scamshield_synthetic_3000.csv'):
    """Save the dataset to CSV file."""
    # Create directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"✓ Dataset saved to {output_path}")


def print_dataset_summary(df):
    """Print summary statistics for the generated dataset."""
    print("\n" + "="*60)
    print("SCAMSHIELD SYNTHETIC DATASET SUMMARY")
    print("="*60)
    
    print(f"\nTotal Records: {len(df)}")
    print(f"\nClass Distribution:")
    print(f"  Normal (0):  {(df['label'] == 0).sum():4d}  ({(df['label'] == 0).sum() / len(df) * 100:.1f}%)")
    print(f"  Scam (1):    {(df['label'] == 1).sum():4d}  ({(df['label'] == 1).sum() / len(df) * 100:.1f}%)")
    
    print(f"\nFeature Statistics by Class:")
    print("-" * 60)
    
    for label, label_name in [(0, "NORMAL"), (1, "SCAM")]:
        subset = df[df['label'] == label]
        print(f"\n{label_name} Transactions (n={len(subset)}):")
        
        print(f"  call_active:           {(subset['call_active'] == 1).sum() / len(subset) * 100:5.1f}% have active call")
        print(f"  remote_app_present:    {(subset['remote_app_present'] == 1).sum() / len(subset) * 100:5.1f}% have remote app")
        print(f"  payee_is_new:          {(subset['payee_is_new'] == 1).sum() / len(subset) * 100:5.1f}% are new payees")
        print(f"  payee_age_days:        mean={subset['payee_age_days'].mean():6.1f}, median={subset['payee_age_days'].median():5.1f}")
        print(f"  amount_ratio_to_usual: mean={subset['amount_ratio_to_usual'].mean():5.2f}, median={subset['amount_ratio_to_usual'].median():4.2f}")
        print(f"  seconds_on_confirm:    mean={subset['seconds_on_confirm_screen'].mean():5.1f}, median={subset['seconds_on_confirm_screen'].median():4.1f}")
        print(f"  payee_reported_count:  {(subset['payee_reported_count'] > 0).sum() / len(subset) * 100:5.1f}% have reports")
    
    print("\n" + "="*60)
    print("DATASET CHARACTERISTICS")
    print("="*60)
    print("✓ Data is intentionally messy and realistic")
    print("✓ Not all scams have all suspicious signals")
    print("✓ Some normal transactions have suspicious-looking features")
    print("✓ Distribution reflects real-world complexity")
    print("="*60 + "\n")


def main():
    """Main execution function."""
    print("Generating ScamShield Synthetic Dataset...")
    print("This may take a few moments...\n")
    
    # Generate dataset
    df = generate_synthetic_dataset(n_samples=3000, random_seed=42)
    
    # Save to file
    save_dataset(df)
    
    # Print summary
    print_dataset_summary(df)
    
    print("✓ Dataset generation complete!")


if __name__ == "__main__":
    main()
