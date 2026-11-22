"""
Project Verification Script

Run this before pushing to GitHub to ensure all components are present.
"""

import os
from pathlib import Path


def check_file(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size
        print(f"✅ {description}: {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"❌ MISSING: {description}: {filepath}")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists."""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        files = list(Path(dirpath).glob('*'))
        print(f"✅ {description}: {dirpath} ({len(files)} items)")
        return True
    else:
        print(f"❌ MISSING: {description}: {dirpath}")
        return False


def main():
    """Run project verification checks."""
    print("="*70)
    print(" "*20 + "SCAMSHIELD PROJECT VERIFICATION")
    print("="*70 + "\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check core directories
    print("📁 DIRECTORIES")
    print("-" * 70)
    checks_total += 1
    if check_directory("src", "Source code"): checks_passed += 1
    checks_total += 1
    if check_directory("app", "Web application"): checks_passed += 1
    checks_total += 1
    if check_directory("data", "Generated data"): checks_passed += 1
    checks_total += 1
    if check_directory("models", "Trained models"): checks_passed += 1
    checks_total += 1
    if check_directory("tests", "Unit tests"): checks_passed += 1
    print()
    
    # Check source files
    print("🐍 SOURCE CODE")
    print("-" * 70)
    checks_total += 1
    if check_file("src/generate_dataset.py", "Dataset generator"): checks_passed += 1
    checks_total += 1
    if check_file("src/train_model.py", "Model trainer"): checks_passed += 1
    checks_total += 1
    if check_file("src/risk_engine.py", "Risk engine"): checks_passed += 1
    checks_total += 1
    if check_file("src/policy_engine.py", "Policy engine"): checks_passed += 1
    checks_total += 1
    if check_file("src/evaluate.py", "Evaluator"): checks_passed += 1
    print()
    
    # Check web application
    print("🌐 WEB APPLICATION")
    print("-" * 70)
    checks_total += 1
    if check_file("app/main.py", "FastAPI backend"): checks_passed += 1
    checks_total += 1
    if check_file("app/templates/index.html", "Main page"): checks_passed += 1
    checks_total += 1
    if check_file("app/templates/about.html", "About page"): checks_passed += 1
    print()
    
    # Check data files
    print("📊 GENERATED DATA")
    print("-" * 70)
    checks_total += 1
    if check_file("data/scamshield_synthetic_3000.csv", "Training dataset"): checks_passed += 1
    checks_total += 1
    if check_file("data/demo_cases.csv", "Demo cases"): checks_passed += 1
    checks_total += 1
    if check_file("data/demo_results.csv", "Demo results"): checks_passed += 1
    print()
    
    # Check models
    print("🤖 TRAINED MODELS")
    print("-" * 70)
    checks_total += 1
    if check_file("models/scamshield_model.joblib", "ML model"): checks_passed += 1
    checks_total += 1
    if check_file("models/scamshield_scaler.joblib", "Feature scaler"): checks_passed += 1
    checks_total += 1
    if check_file("models/feature_names.joblib", "Feature names"): checks_passed += 1
    print()
    
    # Check tests
    print("🧪 TESTS")
    print("-" * 70)
    checks_total += 1
    if check_file("tests/test_risk_engine.py", "Risk engine tests"): checks_passed += 1
    checks_total += 1
    if check_file("tests/test_policy_engine.py", "Policy engine tests"): checks_passed += 1
    print()
    
    # Check configuration files
    print("⚙️  CONFIGURATION")
    print("-" * 70)
    checks_total += 1
    if check_file("requirements.txt", "Dependencies"): checks_passed += 1
    checks_total += 1
    if check_file("README.md", "Documentation"): checks_passed += 1
    checks_total += 1
    if check_file(".gitignore", "Git ignore"): checks_passed += 1
    checks_total += 1
    if check_file("run_demo.py", "Demo runner"): checks_passed += 1
    print()
    
    # Summary
    print("="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print(f"\nPassed: {checks_passed}/{checks_total} checks")
    
    if checks_passed == checks_total:
        print("\n✅ ALL CHECKS PASSED! Project is ready for GitHub.")
        print("\nNext steps:")
        print("  1. Review README.md")
        print("  2. Test web application: uvicorn app.main:app --reload")
        print("  3. Run tests: pytest tests/")
        print("  4. Initialize git: git init")
        print("  5. Add files: git add .")
        print("  6. Commit: git commit -m 'Initial commit'")
        print("  7. Push to GitHub")
        return True
    else:
        print(f"\n⚠️  {checks_total - checks_passed} checks failed.")
        print("\nPlease ensure all required files are present before pushing to GitHub.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
