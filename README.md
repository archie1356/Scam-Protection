# ScamShield

### AI-Driven Scam Pattern Recognition for Coached-Payment Fraud

ScamShield is a proof-of-concept fraud risk detection system designed to identify **coached-payment scams**, where a scammer stays on a live call with a victim and guides them through a payment.

The system analyzes payment and session metadata to identify combinations of suspicious signals and provides a graduated response:

**PASS → SOFT WARNING → DELAY & CONFIRM → HUMAN REVIEW**

ScamShield is designed as a safety layer rather than an automatic blocking system. A single weak signal does not automatically block a payment.

---

## Problem

In coached-payment fraud, the victim may willingly initiate a payment while being manipulated by a scammer.

Examples include:

- Fake customer-care scams
- Remote-access assisted scams
- Digital-arrest-style coercion
- Scammers guiding victims through payment confirmation

Traditional transaction monitoring may not have enough context to distinguish between a normal payment and a payment made under active scammer guidance.

ScamShield addresses this problem by combining multiple contextual signals around the payment session.

---

## Objective

The objective of ScamShield is to:

1. Detect suspicious combinations of payment and session signals.
2. Identify potentially coached payments before confirmation.
3. Provide understandable explanations for risk decisions.
4. Apply graduated safety responses instead of immediately blocking users.
5. Escalate high-risk cases for human review.
6. Preserve user control over legitimate transactions.

---

## How ScamShield Works

```text
              PAYMENT / SESSION SIGNALS
                         │
                         ▼
              ┌──────────────────────┐
              │ Signal Collection &  │
              │ Feature Builder      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     Risk Analysis    │
              │                      │
              │ Rule-Based Scoring   │
              │          +           │
              │ Logistic Regression  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Risk / Policy Engine │
              └──────────┬───────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
        PASS       SOFT WARNING   DELAY & CONFIRM
                                          │
                                          ▼
                                   HUMAN REVIEW
```

The prototype also generates explanations based on the signals that contributed to the risk decision.

---

## Key Signals

The prototype uses eight metadata-based signals:

| Signal | Purpose |
|---|---|
| `call_active` | Indicates whether a call is active during payment |
| `remote_app_present` | Indicates whether a remote-access or screen-sharing application is active |
| `payee_is_new` | Identifies newly added payees |
| `payee_age_days` | Measures how recently the payee was created |
| `amount_ratio_to_usual` | Compares the payment amount with the user's usual transaction amount |
| `seconds_on_confirm_screen` | Measures time spent on the payment confirmation screen |
| `payee_reported_count` | Indicates whether the payee has previous reports |
| `time_of_day` | Provides transaction timing context |

The prototype intentionally uses **metadata rather than audio or voice recordings**.

---

## Detection Approach

ScamShield combines a transparent rule-based risk scorer with a machine learning model.

### 1. Rule-Based Risk Scoring

The rule engine assigns weights to suspicious signals.

| Signal | Weight |
|---|---:|
| Active call | +15 |
| Remote-access application | +25 |
| New payee | +15 |
| Payee age < 7 days | +10 |
| Amount > 5× usual amount | +20 |
| Confirmation screen > 15 seconds | +10 |
| Previously reported payee | +25 |

The rule score is mapped to a response tier:

| Rule Score | Response |
|---:|---|
| 0–24 | PASS |
| 25–44 | SOFT WARNING |
| 45–69 | DELAY & CONFIRM |
| 70+ | HUMAN REVIEW |

The rule-based layer is designed to be transparent, explainable, auditable, and easy to adjust.

### 2. Logistic Regression

A Logistic Regression model is trained using the same eight features.

The dataset uses an **80/20 stratified train/test split** with feature scaling using `StandardScaler`.

The model produces a probability between 0 and 1 representing its estimated probability of the transaction belonging to the scam class.

The ML model acts as a supporting signal rather than an automatic blocking mechanism.

For high ML probability cases, the current prototype can escalate a borderline rule-based decision.

For example:

```text
Rule score = 20
ML probability = 85%

Rule score alone → PASS

ML probability > 80%
AND rule score > 15

Final prototype response → SOFT WARNING
```

This allows the ML model to identify potentially suspicious combinations while retaining the transparency and control of the rule engine.

---

## Risk Response

### PASS

The transaction appears low risk.

The user can continue normally.

### SOFT WARNING

The system detects some suspicious signals.

The user receives a warning explaining why the payment may require additional attention.

### DELAY & CONFIRM

The system detects stronger risk.

The user is given additional time to review the recipient and payment details before continuing.

### HUMAN REVIEW

The system detects a high-risk combination.

The case can be escalated for human review.

The prototype does **not automatically block a payment solely because of one weak signal**.

---

## Synthetic Dataset

The prototype generates a synthetic dataset containing:

- **3,000** transaction/session records
- **2,010** normal records
- **990** scam records
- **8** input features

The generated data intentionally contains variation and noise.

Examples include:

- Legitimate transactions using new payees
- Legitimate transactions involving unusually large amounts
- Legitimate transactions occurring during active calls
- Scam transactions where not every suspicious signal is present

This prevents the prototype from relying on one deterministic pattern.

**Important:** The dataset is synthetic and does not contain real customer or victim information.

---

## Model Evaluation

The Logistic Regression model was evaluated on a held-out synthetic test set.

### Synthetic Test Results

| Metric | Result |
|---|---:|
| Accuracy | **95.50%** |
| Precision | **91.71%** |
| Recall | **94.95%** |
| F1 Score | **93.30%** |
| ROC-AUC | **98.74%** |
| False Positive Rate | **4.23%** |

### Confusion Matrix

```text
                 Predicted
                 Normal   Scam

Actual Normal      385      17
Actual Scam         10     188
```

These results demonstrate feasibility on the generated synthetic dataset.

They should **not** be interpreted as real-world fraud detection accuracy.

Real-world performance would require validation using appropriately authorised and representative banking or payment data.

---

## Feature Analysis

The trained model identified several signals as important predictors within the synthetic dataset.

```text
payee_age_days              -2.1687
payee_reported_count         2.1470
call_active                  2.0202
remote_app_present           1.6822
amount_ratio_to_usual        1.6422
seconds_on_confirm_screen    0.9900
time_of_day                 -0.0217
payee_is_new                  0.0001
```

These coefficients are specific to the generated synthetic dataset and should not be treated as real-world fraud weights.

---

## Demo

The project includes **25 demonstration scenarios**:

- 10 normal cases
- 10 scam cases
- 5 tricky or borderline cases

The demo produces:

- ML scam probability
- Rule score
- Risk tier
- Explanation/reasons
- Final recommended response

Example:

```text
Scenario:
Active call
New payee
Large payment

ML probability: 99.81%
Rule score: 70

Response:
HUMAN REVIEW
```

The demo also contains legitimate high-value and borderline cases to demonstrate the importance of handling false positives.

---

## Web Application

ScamShield includes a local FastAPI web application that allows users to simulate payment scenarios and observe the resulting risk assessment.

Start the application with:

```bash
python -m uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000
```

The application provides API endpoints for scenario analysis, including:

```text
GET /api/scenario/{scenario_id}
POST /api/analyze
```

The API accepts payment/session metadata and returns the risk assessment generated by the prototype.

---

## Project Structure

```text
ScamShield/
│
├── .gitignore
├── README.md
├── requirements.txt
├── run_demo.py
├── start_demo.bat
├── verify_project.py
│
├── app/
│   ├── main.py
│   ├── templates/
│   │   ├── index.html
│   │   └── about.html
│   └── static/
│
├── data/
│   ├── demo_cases.csv
│   ├── demo_results.csv
│   └── scamshield_synthetic_3000.csv
│
├── models/
│   ├── feature_names.joblib
│   ├── scamshield_model.joblib
│   └── scamshield_scaler.joblib
│
├── src/
│   ├── generate_dataset.py
│   ├── train_model.py
│   ├── evaluate.py
│   ├── risk_engine.py
│   └── policy_engine.py
│
└── tests/
    ├── test_policy_engine.py
    └── test_risk_engine.py
```

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn

### Machine Learning

- scikit-learn
- Logistic Regression
- StandardScaler
- Joblib

### Data Processing

- NumPy
- Pandas

### Frontend

- HTML
- CSS
- Jinja2

### Testing

- Pytest

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ScamShield
```

### 2. Create a virtual environment

On Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Complete Demo

Run:

```bash
python run_demo.py
```

This runs the synthetic data generation, model training, evaluation, and demonstration scenarios.

The project also includes:

```text
start_demo.bat
```

for convenient startup on Windows.

---

## Run the Web Application

```bash
python -m uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

---

## Run Tests

Run the test suite with:

```bash
python -m pytest
```

Individual test files can also be executed directly if required.

---

## Verify the Project Before Deployment

The repository includes:

```text
verify_project.py
```

Run:

```bash
python verify_project.py
```

This performs a basic project readiness check to confirm that the required files and project components are present.

---

## Safety and Privacy

ScamShield follows several safety principles.

### Metadata Only

The prototype does not collect or analyse:

- Voice recordings
- Call audio
- Private conversations
- Real banking credentials
- UPI PINs
- Passwords
- Real customer identity information

### No Automatic Blocking

A single weak signal does not automatically block a payment.

### Explainable Decisions

Risk decisions are supported by identifiable signals and explanations.

### User Control

Legitimate users should retain the ability to review and proceed with their payment.

### Human Oversight

High-risk cases can be escalated to human review rather than relying entirely on an automated decision.

---

## Prototype Limitations

This project is a proof of concept.

The current implementation does not have direct integration with:

- Banks
- UPI applications
- NPCI systems
- Operating system call-state APIs
- Real remote-access detection services
- Production payee reputation databases

Some of these signals are simulated through the synthetic dataset.

In a real deployment, access to these signals would require appropriate cooperation, permissions, APIs, privacy controls, security review, and regulatory considerations.

---

## Future Work

Potential future improvements include:

1. Validation with authorised real-world transaction data.
2. Integration with banking or payment-service risk systems.
3. OS or PSP-supported detection of active calls and remote-access applications.
4. Real-time payee reputation integration.
5. Personalised transaction baselines.
6. More robust anomaly detection.
7. Bias and fairness evaluation across user groups.
8. Adversarial testing against evolving scam patterns.
9. Human review workflows.
10. Post-payment reporting and evidence generation.
11. Multilingual warning generation.
12. Continuous model monitoring and evaluation.

---

## Responsible AI

ScamShield is designed as a decision-support and safety layer.

The model should not be treated as an unquestionable source of truth.

Important considerations include:

- False positives can inconvenience legitimate users.
- False negatives can allow scams to proceed.
- Attackers may adapt their behaviour to avoid detection.
- User privacy must be protected.
- Production deployment requires authorised data and appropriate governance.
- Model performance should be continuously monitored.

---

## AI and Third-Party Disclosure

AI-assisted development tools were used during the development process for code assistance, documentation, ideation, and project presentation.

All generated outputs were reviewed and integrated into the final prototype by the project team.

Synthetic data was generated programmatically for experimentation.

Third-party libraries and dependencies are listed in `requirements.txt`.

---

## Disclaimer

This project is an **academic and hackathon proof of concept**.

All reported experimental results are based on synthetic data generated specifically for this prototype.

The reported metrics do not represent guaranteed real-world fraud detection performance.

No real customer, victim, banking, or payment data is used.

---

## License

This project is intended for academic, demonstration, and hackathon purposes.
