"""
ScamShield Web Application

FastAPI backend for the coached-payment fraud detection demo.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from risk_engine import RiskEngine
from policy_engine import PolicyEngine

# Initialize FastAPI app
app = FastAPI(
    title="ScamShield Pay",
    description="AI-Driven Coached-Payment Fraud Detection (Prototype)",
    version="1.0.0"
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize risk and policy engines
risk_engine = RiskEngine()
policy_engine = PolicyEngine()

# Predefined scenarios for demo
DEMO_SCENARIOS = {
    "normal": {
        "name": "Normal Payment",
        "payee_name": "City Electric Utility",
        "payee_id": "CITYELECTRIC123",
        "amount": "₹1,250.00",
        "purpose": "Monthly electricity bill",
        "features": {
            "call_active": 0,
            "remote_app_present": 0,
            "payee_is_new": 0,
            "payee_age_days": 180,
            "amount_ratio_to_usual": 1.1,
            "seconds_on_confirm_screen": 5,
            "payee_reported_count": 0,
            "time_of_day": 14
        }
    },
    "new_payee_large": {
        "name": "New Payee + Large Amount",
        "payee_name": "Premium Insurance Corp",
        "payee_id": "PREMIUMINS456",
        "amount": "₹42,000.00",
        "purpose": "Annual insurance premium",
        "features": {
            "call_active": 0,
            "remote_app_present": 0,
            "payee_is_new": 1,
            "payee_age_days": 2,
            "amount_ratio_to_usual": 6.5,
            "seconds_on_confirm_screen": 12,
            "payee_reported_count": 0,
            "time_of_day": 11
        }
    },
    "call_new_payee": {
        "name": "Active Call + New Payee",
        "payee_name": "SafeAccount Transfer",
        "payee_id": "SAFEACCT789",
        "amount": "₹35,000.00",
        "purpose": "Account verification",
        "features": {
            "call_active": 1,
            "remote_app_present": 0,
            "payee_is_new": 1,
            "payee_age_days": 0,
            "amount_ratio_to_usual": 8.5,
            "seconds_on_confirm_screen": 28,
            "payee_reported_count": 0,
            "time_of_day": 15
        }
    },
    "remote_access": {
        "name": "Remote Access + Coaching",
        "payee_name": "CustomerCare Help",
        "payee_id": "CUSTCARE001",
        "amount": "₹50,000.00",
        "purpose": "Security verification",
        "features": {
            "call_active": 1,
            "remote_app_present": 1,
            "payee_is_new": 1,
            "payee_age_days": 0,
            "amount_ratio_to_usual": 12.0,
            "seconds_on_confirm_screen": 35,
            "payee_reported_count": 3,
            "time_of_day": 13
        }
    },
    "high_risk": {
        "name": "High-Risk Coached Payment",
        "payee_name": "Digital Arrest Clearance",
        "payee_id": "DIGARREST999",
        "amount": "₹75,000.00",
        "purpose": "Legal clearance fee",
        "features": {
            "call_active": 1,
            "remote_app_present": 1,
            "payee_is_new": 1,
            "payee_age_days": 0,
            "amount_ratio_to_usual": 18.0,
            "seconds_on_confirm_screen": 45,
            "payee_reported_count": 12,
            "time_of_day": 20
        }
    },
    "legitimate_large": {
        "name": "Legitimate Large Payment",
        "payee_name": "Home Loan Services",
        "payee_id": "HOMELOAN456",
        "amount": "₹85,000.00",
        "purpose": "EMI payment",
        "features": {
            "call_active": 0,
            "remote_app_present": 0,
            "payee_is_new": 0,
            "payee_age_days": 400,
            "amount_ratio_to_usual": 9.2,
            "seconds_on_confirm_screen": 10,
            "payee_reported_count": 0,
            "time_of_day": 10
        }
    }
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main payment interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "scenarios": DEMO_SCENARIOS
    })


@app.get("/api/scenarios")
async def get_scenarios():
    """Get all available demo scenarios."""
    return {"scenarios": DEMO_SCENARIOS}


@app.get("/api/scenario/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get specific scenario details."""
    if scenario_id not in DEMO_SCENARIOS:
        return JSONResponse(
            status_code=404,
            content={"error": "Scenario not found"}
        )
    return DEMO_SCENARIOS[scenario_id]


@app.post("/api/analyze")
async def analyze_payment(request: Request):
    """
    Analyze a payment transaction for fraud risk.
    
    Expects JSON with transaction features.
    Returns risk assessment and policy decision.
    """
    try:
        data = await request.json()
        features = data.get("features", {})
        
        # Assess risk
        risk_assessment = risk_engine.assess_risk(features)
        
        # Get policy decision
        policy_response = policy_engine.get_policy_response(risk_assessment)
        
        # Combine response
        response = {
            "success": True,
            "risk_assessment": {
                "risk_tier": risk_assessment["risk_tier"],
                "rule_score": risk_assessment["rule_score"],
                "ml_probability": round(risk_assessment["ml_probability"], 4),
                "ml_probability_pct": round(risk_assessment["ml_probability_pct"], 2),
                "top_reasons": risk_assessment["top_reasons"],
                "num_triggered_rules": risk_assessment["num_triggered_rules"]
            },
            "policy": policy_response
        }
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    model_loaded = risk_engine.model is not None
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "version": "1.0.0"
    }


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page with project information."""
    return templates.TemplateResponse("about.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
