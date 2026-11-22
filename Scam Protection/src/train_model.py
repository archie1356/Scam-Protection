"""
ScamShield Model Training

Trains a Logistic Regression model for coached-payment fraud detection.
Uses explainable ML with feature scaling and stratified train-test split.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, classification_report
)


def load_dataset(data_path='data/scamshield_synthetic_3000.csv'):
    """Load the synthetic dataset."""
    if not Path(data_path).exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. "
            f"Please run generate_dataset.py first."
        )
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded dataset: {len(df)} records")
    return df


def prepare_features(df):
    """
    Prepare features for training.
    Separate features from labels.
    """
    # Feature columns (exclude label)
    feature_cols = [
        'call_active',
        'remote_app_present',
        'payee_is_new',
        'payee_age_days',
        'amount_ratio_to_usual',
        'seconds_on_confirm_screen',
        'payee_reported_count',
        'time_of_day'
    ]
    
    X = df[feature_cols].values
    y = df['label'].values
    
    return X, y, feature_cols


def split_and_scale_data(X, y, test_size=0.2, random_seed=42):
    """
    Split data into train/test sets with stratification.
    Scale numerical features.
    """
    # Stratified split to maintain class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_seed,
        stratify=y  # Maintain class proportions
    )
    
    print(f"\n✓ Train set: {len(X_train)} samples")
    print(f"  - Normal: {(y_train == 0).sum()} ({(y_train == 0).sum() / len(y_train) * 100:.1f}%)")
    print(f"  - Scam:   {(y_train == 1).sum()} ({(y_train == 1).sum() / len(y_train) * 100:.1f}%)")
    
    print(f"\n✓ Test set: {len(X_test)} samples")
    print(f"  - Normal: {(y_test == 0).sum()} ({(y_test == 0).sum() / len(y_test) * 100:.1f}%)")
    print(f"  - Scam:   {(y_test == 1).sum()} ({(y_test == 1).sum() / len(y_test) * 100:.1f}%)")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n✓ Features scaled using StandardScaler")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def train_logistic_regression(X_train, y_train, random_seed=42):
    """
    Train Logistic Regression model.
    Simple, interpretable, and effective for this use case.
    """
    print("\nTraining Logistic Regression model...")
    
    # Logistic Regression with balanced class weights
    # This helps handle class imbalance
    model = LogisticRegression(
        random_state=random_seed,
        max_iter=1000,
        class_weight='balanced',  # Handle class imbalance
        solver='lbfgs'
    )
    
    model.fit(X_train, y_train)
    
    print("✓ Model training complete")
    
    return model


def evaluate_model(model, X_test, y_test, feature_names):
    """
    Evaluate model performance on test set.
    Calculate comprehensive metrics.
    """
    print("\n" + "="*60)
    print("MODEL EVALUATION ON TEST SET")
    print("="*60)
    
    # Get predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]  # Probability of scam class
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # False positive rate
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    # Print metrics
    print(f"\nOverall Metrics:")
    print(f"  Accuracy:  {accuracy:.4f}  ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f}  ({precision*100:.2f}%)")
    print(f"  Recall:    {recall:.4f}  ({recall*100:.2f}%)")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {roc_auc:.4f}")
    
    print(f"\nConfusion Matrix:")
    print(f"                  Predicted")
    print(f"                Normal  Scam")
    print(f"  Actual Normal    {tn:4d}  {fp:4d}")
    print(f"         Scam      {fn:4d}  {tp:4d}")
    
    print(f"\nError Analysis:")
    print(f"  True Positives (correct scam detection):  {tp:4d}")
    print(f"  True Negatives (correct normal approval): {tn:4d}")
    print(f"  False Positives (false alarm):            {fp:4d}")
    print(f"  False Negatives (missed scam):            {fn:4d}")
    print(f"  False Positive Rate:                      {fpr:.4f}  ({fpr*100:.2f}%)")
    
    # Feature importance (coefficients)
    print(f"\nFeature Importance (Logistic Regression Coefficients):")
    print(f"  (Positive = increases scam probability)")
    coefficients = model.coef_[0]
    feature_importance = list(zip(feature_names, coefficients))
    feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for feature, coef in feature_importance:
        direction = "↑" if coef > 0 else "↓"
        print(f"  {feature:30s} {direction}  {coef:+7.4f}")
    
    print("\n" + "="*60)
    print("IMPORTANT: These results are from SYNTHETIC DATA.")
    print("Real-world performance may differ significantly.")
    print("="*60 + "\n")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'fpr': fpr
    }


def save_model_and_scaler(model, scaler, feature_names, 
                          model_path='models/scamshield_model.joblib',
                          scaler_path='models/scamshield_scaler.joblib',
                          features_path='models/feature_names.joblib'):
    """Save trained model, scaler, and feature names."""
    # Create directory if it doesn't exist
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(model, model_path)
    print(f"✓ Model saved to {model_path}")
    
    # Save scaler
    joblib.dump(scaler, scaler_path)
    print(f"✓ Scaler saved to {scaler_path}")
    
    # Save feature names
    joblib.dump(feature_names, features_path)
    print(f"✓ Feature names saved to {features_path}")


def main():
    """Main training pipeline."""
    print("="*60)
    print("SCAMSHIELD MODEL TRAINING")
    print("="*60 + "\n")
    
    # Load dataset
    df = load_dataset()
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    print(f"✓ Features prepared: {len(feature_names)} features")
    
    # Split and scale
    X_train, X_test, y_train, y_test, scaler = split_and_scale_data(X, y)
    
    # Train model
    model = train_logistic_regression(X_train, y_train)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, feature_names)
    
    # Save model and scaler
    save_model_and_scaler(model, scaler, feature_names)
    
    print("\n✓ Training pipeline complete!")
    
    return model, scaler, metrics


if __name__ == "__main__":
    main()
