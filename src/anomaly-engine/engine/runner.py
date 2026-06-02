"""Engine runner — applies all enabled checks to a contract dict (INC-003)."""
import logging

from engine.checks.check_01_signing import SigningCheck
from engine.checks.check_02_standstill import StandstillCheck
from engine.checks.check_03_time_gap import TimeGapCheck
from engine.checks.check_04_forensics import ForensicsCheck
from engine.checks.check_05_supplier_network import SupplierNetworkCheck
from engine.checks.check_06_score_variance import ScoreVarianceCheck
from engine.checks.check_07_amendment import AmendmentCheck
from engine.checks.check_08_debarment import DebarmentCheck
from engine.config import DEFAULT_THRESHOLDS, DEFAULT_WEIGHTS
from engine.models import CheckOutput, CheckResult, EngineOutput

log = logging.getLogger(__name__)

# Full ordered registry of all 8 checks
ALL_CHECKS = [
    SigningCheck(),
    StandstillCheck(),
    TimeGapCheck(),
    ForensicsCheck(),
    SupplierNetworkCheck(),
    ScoreVarianceCheck(),
    AmendmentCheck(),
    DebarmentCheck(),
]


def build_config(
    weight_overrides: dict | None = None,
    threshold_overrides: dict | None = None,
    enabled_check_ids: set[int] | None = None,
) -> dict:
    """Build the runtime config dict passed into each check's run()."""
    weights = {**DEFAULT_WEIGHTS, **(weight_overrides or {})}
    thresholds = {**DEFAULT_THRESHOLDS, **(threshold_overrides or {})}
    return {
        "weights": weights,
        "thresholds": thresholds,
        "enabled": enabled_check_ids,  # None = all enabled
    }


def run_checks(contract: dict, config: dict | None = None) -> EngineOutput:
    """
    Run all registered checks against a normalised contract dict.

    Args:
        contract: normalised contract dict (from ingestion.normalise or DB row).
        config:   runtime config from build_config(); defaults used if None.

    Returns:
        EngineOutput with per-check results and aggregate raw_score.
    """
    if config is None:
        config = build_config()

    enabled = config.get("enabled")  # None = all
    output = EngineOutput(contract_ocid=contract.get("ocid", "unknown"))

    for check in ALL_CHECKS:
        if enabled is not None and check.id not in enabled:
            continue
        try:
            result: CheckOutput = check.run(contract, config)
            output.outputs.append(result)
            log.debug(
                "Contract %s | Check %d (%s): %s",
                output.contract_ocid, check.id, check.key, result.result,
            )
        except Exception as e:
            log.error(
                "Check %d (%s) failed on contract %s: %s",
                check.id, check.key, output.contract_ocid, e,
            )

    return output
