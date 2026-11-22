"""
ScamShield Complete Demo Pipeline

Runs the complete demonstration:
1. Generate dataset
2. Train model
3. Evaluate model
4. Run demo cases
5. Show results
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_dataset import main as generate_data
from train_model import main as train_model
from evaluate import evaluate_demo_cases


def main():
    """Run complete demo pipeline."""
    print("\n" + "="*80)
    print(" " * 25 + "SCAMSHIELD DEMO PIPELINE")
    print("="*80 + "\n")
    
    print("This demo will:")
    print("  1. Generate 3,000 synthetic transaction records")
    print("  2. Train a Logistic Regression model")
    print("  3. Evaluate model performance")
    print("  4. Generate and evaluate 25 demo cases")
    print("  5. Show comprehensive results")
    
    input("\nPress Enter to start...")
    
    # Step 1: Generate dataset
    print("\n" + "="*80)
    print("STEP 1: GENERATING SYNTHETIC DATASET")
    print("="*80 + "\n")
    
    try:
        generate_data()
    except Exception as e:
        print(f"Error generating dataset: {e}")
        return
    
    # Step 2 & 3: Train and evaluate model
    print("\n" + "="*80)
    print("STEP 2 & 3: TRAINING AND EVALUATING MODEL")
    print("="*80 + "\n")
    
    try:
        train_model()
    except Exception as e:
        print(f"Error training model: {e}")
        return
    
    # Step 4: Run demo cases
    print("\n" + "="*80)
    print("STEP 4: EVALUATING DEMO CASES")
    print("="*80 + "\n")
    
    try:
        evaluate_demo_cases()
    except Exception as e:
        print(f"Error evaluating demo cases: {e}")
        return
    
    # Final summary
    print("\n" + "="*80)
    print("DEMO PIPELINE COMPLETE!")
    print("="*80 + "\n")
    
    print("Generated files:")
    print("  ✓ data/scamshield_synthetic_3000.csv  - Training dataset")
    print("  ✓ data/demo_cases.csv                 - Demo cases")
    print("  ✓ data/demo_results.csv               - Demo evaluation results")
    print("  ✓ models/scamshield_model.joblib      - Trained model")
    print("  ✓ models/scamshield_scaler.joblib     - Feature scaler")
    print("  ✓ models/feature_names.joblib         - Feature names")
    
    print("\nNext steps:")
    print("  • Run the web demo: python -m uvicorn app.main:app --reload")
    print("  • Open browser: http://localhost:8000")
    print("  • Try different payment scenarios!")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
