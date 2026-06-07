"""Local dev bootstrap — creates SQLite tables and seeds demo data.
Run from the backend dir:  python scripts/local_seed.py
"""
import asyncio
import os
import sys
import uuid
from datetime import date, datetime, timezone

# Add the backend root (parent of scripts/) to the path so `import app` works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./cdf_local.db")
os.environ.setdefault("MFA_ENFORCE", "false")
os.environ.setdefault("DEBUG", "true")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
import app.models  # register all models
from app.models.user import Role, User, Institution
from app.models.contract import Contract, Supplier
from app.models.anomaly import CheckDefinition
from app.models.monitor import Disbursement
from app.models.case import Case
from app.core.security import hash_password

ROLES = [
    ("anonymous", "Anonymous", ["read_public", "verify_document"]),
    ("community_monitor", "Community Monitor", ["read_public", "verify_document", "create_submission"]),
    ("inst_confirmer", "Institutional Confirmer", ["read_public", "verify_document", "read_named", "confirm_submission", "ghost_action"]),
    ("oversight_officer", "Oversight Officer", ["read_public", "verify_document", "read_named", "read_audit", "action_anomaly", "confirm_submission", "ghost_action", "case_mgmt"]),
    ("analyst", "Analyst", ["read_public", "verify_document", "read_named", "read_audit"]),
    ("system_admin", "System Administrator", ["read_public", "verify_document", "read_named", "read_audit", "action_anomaly", "confirm_submission", "ghost_action", "case_mgmt", "manage_users", "configure_weights", "ledger_governance", "system_admin"]),
]
CHECKS = [
    (1, "signing", "Missing signing date", 15.0), (2, "standstill", "Standstill violation", 20.0),
    (3, "time_gap", "Timeline compression", 15.0), (4, "forensics", "Forensic pricing", 15.0),
    (5, "supplier_net", "Supplier network", 10.0), (6, "score_var", "Score variance", 5.0),
    (7, "amendment", "Amendment cap", 10.0), (8, "debarment", "Debarment", 10.0),
]

async def main():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as db:
        roles = {}
        for key, name, perms in ROLES:
            r = Role(key=key, name=name, permissions=perms)
            db.add(r); roles[key] = r
        await db.flush()

        # Three institutions with distinct mandates.
        oag = Institution(id=uuid.uuid4(), name="Office of the Auditor General", type="OAG",
                          data_sharing_agreement_ref="DSA-2026-01")
        acc = Institution(id=uuid.uuid4(), name="Anti-Corruption Commission", type="ACC",
                          data_sharing_agreement_ref="DSA-2026-02")
        zppa = Institution(id=uuid.uuid4(), name="Zambia Public Procurement Authority", type="ZPPA",
                           data_sharing_agreement_ref="DSA-2026-03")
        db.add_all([oag, acc, zppa])
        await db.flush()
        inst = oag  # kept for back-compat below

        # Admin user — login: admin@cdf.zm / AdminPass123!
        db.add(User(id=uuid.uuid4(), name="System Admin", email="admin@cdf.zm",
                    password_hash=hash_password("AdminPass123!"), role_id=roles["system_admin"].id,
                    institution_id=oag.id, active=True))
        # One oversight officer per institution (all password Officer123!).
        oag_officer = User(id=uuid.uuid4(), name="A. Banda (OAG)", email="officer@oag.gov.zm",
                           password_hash=hash_password("Officer123!"), role_id=roles["oversight_officer"].id,
                           institution_id=oag.id, active=True)
        acc_officer = User(id=uuid.uuid4(), name="C. Phiri (ACC)", email="officer@acc.gov.zm",
                           password_hash=hash_password("Officer123!"), role_id=roles["oversight_officer"].id,
                           institution_id=acc.id, active=True)
        zppa_officer = User(id=uuid.uuid4(), name="M. Tembo (ZPPA)", email="officer@zppa.gov.zm",
                            password_hash=hash_password("Officer123!"), role_id=roles["oversight_officer"].id,
                            institution_id=zppa.id, active=True)
        db.add_all([oag_officer, acc_officer, zppa_officer])
        # Monitor — monitor@cdf.zm / Monitor123!
        db.add(User(id=uuid.uuid4(), name="Field Monitor", email="monitor@cdf.zm",
                    password_hash=hash_password("Monitor123!"), role_id=roles["community_monitor"].id, active=True))
        await db.flush()

        for cid, key, name, w in CHECKS:
            db.add(CheckDefinition(id=cid, key=key, name=name, basis="Public Procurement Act",
                                   severity="high", weight=w, enabled=True))

        # A few contracts with varying risk
        sup = Supplier(id=uuid.uuid4(), name="Acme Construction Ltd", tpin="1000012345", address="Plot 15, Lusaka")
        db.add(sup); await db.flush()
        db.add(Contract(ocid="ocds-zm-zppa-001", procuring_entity="Ministry of Health", supplier_id=sup.id,
                        value=4_500_000, currency="ZMW", award_date=date(2024, 3, 15),
                        signing_date=date(2024, 4, 2), status="active", risk_score=18, raw_ocds={}))
        db.add(Contract(ocid="ocds-zm-zppa-003", procuring_entity="Ministry of Roads", supplier_id=sup.id,
                        value=35_000_000, currency="ZMW", award_date=date(2024, 6, 25),
                        signing_date=date(2024, 6, 26), status="active", risk_score=72, raw_ocds={}))
        db.add(Contract(ocid="ocds-zm-zppa-002", procuring_entity="Ministry of Education", supplier_id=sup.id,
                        value=12_000_000, currency="ZMW", award_date=date(2024, 5, 20),
                        signing_date=None, status="active", risk_score=55, raw_ocds={}))

        # A disbursement with no completion → ghost candidate
        db.add(Disbursement(id=str(uuid.uuid4()), constituency_id="LPV-002", project_id="proj-001",
                            contract_ocid="ocds-zm-zppa-001", amount=285_000, date=date(2024, 1, 10), source="IFMIS"))

        # Sample cases — institution-segregated, incl. one OAG→ACC escalation.
        db.add_all([
            Case(id=str(uuid.uuid4()), subject_type="contract", subject_ref="ocds-zm-zppa-003",
                 title="Signing gap — Ministry of Roads", status="open", priority="high",
                 owner_institution="OAG", created_by=str(oag_officer.id), assignee_id=str(oag_officer.id)),
            Case(id=str(uuid.uuid4()), subject_type="contract", subject_ref="ocds-zm-zppa-002",
                 title="Procurement irregularity — Ministry of Education", status="escalated", priority="high",
                 owner_institution="OAG", escalated_to="ACC",
                 created_by=str(oag_officer.id), assignee_id=str(acc_officer.id)),
            Case(id=str(uuid.uuid4()), subject_type="ghost_project", subject_ref="proj-001",
                 title="Ghost project — Milenge borehole", status="in_review", priority="medium",
                 owner_institution="OAG", created_by=str(oag_officer.id), assignee_id=str(oag_officer.id)),
            Case(id=str(uuid.uuid4()), subject_type="contract", subject_ref="ocds-zm-zppa-001",
                 title="Standstill compliance check", status="open", priority="low",
                 owner_institution="ZPPA", created_by=str(zppa_officer.id), assignee_id=str(zppa_officer.id)),
        ])

        await db.commit()
    await engine.dispose()
    print("✓ Seeded cdf_local.db")
    print("  Logins:")
    print("    admin@cdf.zm     / AdminPass123!  (system_admin)")
    print("    officer@oag.gov.zm / Officer123!  (oversight_officer)")
    print("    monitor@cdf.zm   / Monitor123!    (community_monitor)")

if __name__ == "__main__":
    asyncio.run(main())
