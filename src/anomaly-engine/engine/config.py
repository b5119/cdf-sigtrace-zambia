"""Default weights and thresholds for the 8-check anomaly engine.

All values are overridable via the Config table in the database (INC-017).
"""

DEFAULT_WEIGHTS: dict[str, float] = {
    "signing":     15.0,
    "standstill":  20.0,
    "time_gap":    15.0,
    "forensics":   15.0,
    "supplier_net":10.0,
    "score_var":    5.0,
    "amendment":   10.0,
    "debarment":   10.0,
}

DEFAULT_THRESHOLDS: dict[str, object] = {
    "standstill_days": 14,       # minimum days between award and signing
    "time_gap_min_days": 1,      # minimum days between tender close and award
    "amendment_cap_pct": 15.0,   # maximum % value increase via amendments
    "ghost_window_days": 180,    # days after disbursement before ghost-project signal
    "high_risk_threshold": 60,   # score above which a contract is "high risk"
}
