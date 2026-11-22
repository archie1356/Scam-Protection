"""
Synthetic UPI session generator for a coached-payment fraud prototype.

ALL DATA IS SYNTHETIC. Every number below is an assumption chosen by us to
make realistic, messy sessions. It is NOT real fraud data, so any results
on it are illustrative only.

Run:  python generate_sessions.py
Out:  synthetic_sessions.csv
"""
import numpy as np
import pandas as pd

SEED = 0
N_SESSIONS = 5000
SCAM_FRACTION = 0.10   # real-world scam share is far lower; see notes
rng = np.random.default_rng(SEED)

# ---------- helpers ----------------------------------------------------
def lognormal(median, sigma):
    return float(rng.lognormal(mean=np.log(median), sigma=sigma))

def chance(p):
    return bool(rng.random() < p)

def noisy_flag(true_value, miss_rate, false_rate):
    if true_value:
        return int(rng.random() >= miss_rate)
    return int(rng.random() < false_rate)

def normal_hour():
    peak = rng.choice([9, 13, 19, 21], p=[0.2, 0.25, 0.35, 0.2])
    return int(round(rng.normal(peak, 2.0))) % 24

def scam_hour():
    # fake bank/official callers mostly work business hours
    return int(np.clip(round(rng.normal(14, 3.0)), 0, 23))

def normal_recent_payments():
    return int(rng.choice([0, 1, 2], p=[0.90, 0.08, 0.02]))

def young_payee_age():
    """Scam payee accounts are usually days old, a few are older rented/hijacked ones."""
    if chance(0.85):
        return int(np.clip(rng.exponential(10), 0, 60))
    return int(lognormal(120, 0.8))

def reported(prob, extra_mean):
    return int(1 + rng.poisson(extra_mean)) if chance(prob) else 0

# ---------- users ------------------------------------------------------
AGE_GROUPS = ["18-30", "31-50", "51-65", "65+"]
NORMAL_AGE_P = [0.30, 0.35, 0.22, 0.13]
SCAM_AGE_P = [0.15, 0.25, 0.30, 0.30]     # ASSUMPTION: victims skew older
BASE_SECONDS = {"18-30": 5, "31-50": 7, "51-65": 10, "65+": 14}  # older = slower

def confirm_seconds(age, factor=1.0):
    return float(np.clip(lognormal(BASE_SECONDS[age] * factor, 0.5), 1.5, 180))

# ---------- NORMAL sessions (label 0) -----------------------------------
NORMAL_TYPES = ["known_routine", "new_merchant", "new_person_legit",
                "big_planned_payment", "on_call_unrelated",
                "legit_remote_or_screen_app", "odd_hours_legit"]
NORMAL_P = [0.52, 0.20, 0.09, 0.05, 0.08, 0.02, 0.04]

def make_normal(age):
    t = rng.choice(NORMAL_TYPES, p=NORMAL_P)
    s = dict(call=chance(0.04), remote=chance(0.002), new=0,
             payee_age=int(rng.integers(180, 2500)),
             ratio=lognormal(1.0, 0.6), secs=confirm_seconds(age),
             reported=reported(0.003, 0), recent=normal_recent_payments(),
             hour=normal_hour())
    if t == "new_merchant":            # first time at a shop/cab/restaurant QR
        s.update(new=1, payee_age=int(np.clip(lognormal(400, 1.2), 5, 4000)),
                 ratio=lognormal(0.8, 0.7), call=chance(0.05),
                 secs=confirm_seconds(age, 0.8), reported=reported(0.005, 0))
    elif t == "new_person_legit":      # new landlord, plumber, friend
        s.update(new=1, payee_age=int(np.clip(lognormal(300, 1.5), 1, 4000)),
                 ratio=lognormal(4.0, 0.7), call=chance(0.15),
                 remote=chance(0.005), secs=confirm_seconds(age, 1.5),
                 reported=reported(0.005, 0))
    elif t == "big_planned_payment":   # fees, premium, deposit: big but planned
        new = chance(0.5)
        s.update(new=int(new),
                 payee_age=int(np.clip(lognormal(500, 1.0), 5, 4000)) if new else 1000,
                 ratio=lognormal(15, 0.5), call=chance(0.12),
                 remote=chance(0.005), secs=confirm_seconds(age, 2.0),
                 reported=0)
    elif t == "on_call_unrelated":     # chatting with family while paying
        new = chance(0.25)
        s.update(call=True, new=int(new),
                 payee_age=int(np.clip(lognormal(300, 1.3), 1, 4000)) if new else 1000,
                 ratio=lognormal(1.2, 0.7), remote=chance(0.003), reported=0)
    elif t == "legit_remote_or_screen_app":  # work-from-home remote desktop, TV mirroring
        new = chance(0.3)
        s.update(remote=True, call=chance(0.10), new=int(new),
                 payee_age=int(np.clip(lognormal(300, 1.3), 1, 4000)) if new else 1000,
                 ratio=lognormal(1.5, 0.8), reported=0)
    elif t == "odd_hours_legit":       # night-shift workers, insomniacs
        s.update(hour=int(rng.integers(0, 6)), new=int(chance(0.15)))
    return t, s

# ---------- SCAM sessions (label 1) -------------------------------------
SCAM_TYPES = ["fake_support_remote", "digital_arrest", "refund_collect",
              "split_payments", "investment_task_no_call"]
SCAM_P = [0.35, 0.25, 0.15, 0.12, 0.13]

def make_scam(age):
    t = rng.choice(SCAM_TYPES, p=SCAM_P)
    if t == "fake_support_remote":     # fake bank care + AnyDesk, victim guided on a call
        rushed = chance(0.5)
        s = dict(call=chance(0.97), remote=chance(0.85), new=int(chance(0.95)),
                 payee_age=young_payee_age(), ratio=lognormal(15, 0.8),
                 secs=lognormal(3.5, 0.3) if rushed else lognormal(30, 0.5),
                 reported=reported(0.35, 1.5),
                 recent=int(rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1])),
                 hour=scam_hour())
    elif t == "digital_arrest":        # fake officials; often a WhatsApp/Skype video call
        s = dict(call=chance(0.85), remote=chance(0.15), new=int(chance(0.90)),
                 payee_age=young_payee_age(), ratio=lognormal(30, 0.9),
                 secs=lognormal(35, 0.5), reported=reported(0.30, 1.5),
                 recent=int(rng.choice([0, 1, 2], p=[0.6, 0.25, 0.15])),
                 hour=scam_hour())
    elif t == "refund_collect":        # "you'll receive money" / collect-request trick
        s = dict(call=chance(0.60), remote=chance(0.05), new=int(chance(0.90)),
                 payee_age=young_payee_age(), ratio=lognormal(3, 0.8),
                 secs=lognormal(5, 0.4), reported=reported(0.30, 1.5),
                 recent=int(rng.choice([0, 1], p=[0.8, 0.2])), hour=scam_hour())
    elif t == "split_payments":        # scammer splits money so each payment looks normal
        s = dict(call=chance(0.90), remote=chance(0.50), new=int(chance(0.40)),
                 payee_age=young_payee_age(), ratio=lognormal(2.5, 0.4),
                 secs=lognormal(9, 0.4), reported=reported(0.25, 1.0),
                 recent=int(rng.integers(1, 6)), hour=scam_hour())
    else:                              # investment/task scam from Telegram, no live call
        s = dict(call=chance(0.10), remote=chance(0.02), new=1,
                 payee_age=int(rng.integers(1, 60)), ratio=lognormal(3, 0.7),
                 secs=lognormal(8, 0.4), reported=reported(0.55, 3.0),
                 recent=int(rng.choice([0, 1, 2], p=[0.6, 0.25, 0.15])),
                 hour=normal_hour())
    return t, s

# ---------- build dataset -----------------------------------------------
def build(n=N_SESSIONS, scam_fraction=SCAM_FRACTION):
    rows = []
    for i in range(n):
        is_scam = int(chance(scam_fraction))
        age = rng.choice(AGE_GROUPS, p=SCAM_AGE_P if is_scam else NORMAL_AGE_P)
        t, s = make_scam(age) if is_scam else make_normal(age)
        rows.append(dict(
            session_id=f"S{i:05d}", age_group=age, session_type=t, is_scam=is_scam,
            call_active=noisy_flag(s["call"], miss_rate=0.10, false_rate=0.01),
            remote_app_present=noisy_flag(s["remote"], miss_rate=0.15, false_rate=0.005),
            payee_is_new=int(s["new"]),
            payee_age_days=int(s["payee_age"]),
            amount_ratio_to_usual=round(s["ratio"], 2),
            seconds_on_confirm_screen=round(s["secs"], 1),
            payee_reported_count=int(s["reported"]),
            payments_last_hour=int(s["recent"]),
            hour_of_day=int(s["hour"]),
        ))
    return pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)

if __name__ == "__main__":
    df = build()
    df.to_csv("synthetic_sessions.csv", index=False)
    print(f"Saved {len(df)} sessions, scam share = {df.is_scam.mean():.1%}\n")
    print("Session types:\n", df.session_type.value_counts(), "\n")
    feats = ["call_active", "remote_app_present", "payee_is_new"]
    print("Share of sessions with each flag set (messiness check):")
    print(df.groupby("is_scam")[feats].mean().round(3), "\n")
    print("Median amount ratio / confirm seconds:")
    print(df.groupby("is_scam")[["amount_ratio_to_usual",
                                  "seconds_on_confirm_screen"]].median().round(1))