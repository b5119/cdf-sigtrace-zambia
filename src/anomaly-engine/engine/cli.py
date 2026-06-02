"""CLI: python -m engine.cli --ocid <ocid> [--sample]"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _load_sample_contract(ocid: str) -> dict | None:
    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "ingestion", "sample", "ocds_sample.json"
    )
    with open(sample_path) as f:
        package = json.load(f)
    for record in package.get("records", []):
        if record.get("ocid") == ocid:
            from ingestion.normalise import normalise_record
            contract, _ = normalise_record(record)
            return contract
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="CDF SigTrace anomaly engine CLI")
    parser.add_argument("--ocid", required=True, help="Contract OCID to analyse")
    parser.add_argument("--sample", action="store_true", help="Load contract from bundled sample")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.sample:
        contract = _load_sample_contract(args.ocid)
        if contract is None:
            print(f"OCID {args.ocid!r} not found in sample file.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Non-sample mode requires a DB connection (set DATABASE_URL).", file=sys.stderr)
        sys.exit(1)

    from engine.runner import run_checks, build_config
    config = build_config()
    output = run_checks(contract, config)

    if args.json:
        result = {
            "ocid": output.contract_ocid,
            "flag_count": output.flag_count,
            "raw_score": output.raw_score,
            "checks": [
                {
                    "id": o.check_id,
                    "key": o.check_key,
                    "result": o.result,
                    "evidence": o.evidence_note,
                    "weight_applied": o.weight_applied,
                }
                for o in output.outputs
            ],
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\nContract: {output.contract_ocid}")
        print(f"Flags: {output.flag_count}  Raw score: {output.raw_score:.1f}")
        print()
        for o in output.outputs:
            icon = "🚩" if o.result == "flag" else ("⏭️" if o.result == "skip" else "✅")
            print(f"  [{o.check_id}] {o.check_key:15s} {o.result.upper():6s}  {o.evidence_note}")


if __name__ == "__main__":
    main()
