"""
Synthetic / Demonstration Dataset generator.

Prototype demonstration uses synthetic/anonymized safety-report data.
Production deployment would require authorized OIL data.

Plants deliberate patterns per spec section 27/28:
  Pattern A — Electrical Isolation (40-60 reports, INCREASING)
  Pattern B — Working at Height (30-40 reports, STABLE)
  Pattern C — Permit-to-Work (20-30 reports, DECREASING)
  Pattern D — Vehicle/Pedestrian Interaction (15-25 reports, NEWLY EMERGING)
  Pattern E — Confined Space (10-20 reports, INCREASING, smaller/newer)
  Plus unrelated noise reports so clustering is meaningful.

All sites, contractors, departments, and descriptions are fictional.
"""
import random
import datetime as dt
import csv
import sys
from pathlib import Path

random.seed(42)

SITES = ["Site Alpha", "Site Bravo", "Site Charlie", "Site Delta", "Site Echo", "Site Foxtrot"]
DEPARTMENTS = ["Maintenance", "Operations", "Drilling", "Pipeline Integrity", "Logistics", "HSE"]
CONTRACTORS = [f"Contractor-{c}" for c in
               ["Vantage Energy Services", "Northstar Industrial", "Meridian Fabrication",
                "Orion Field Services", "Atlas Mechanical", "Summit Rigging Co", "Beacon Electrical Works",
                "Ironclad Scaffolding", "Delta Wellsite Services", "Coastal Logistics", "Pinnacle Contractors",
                "Redline Maintenance Group"]]
REPORTER_ROLES = ["Technician", "Site Supervisor", "Safety Officer", "Operator", "Foreman", "Engineer"]
REPORT_TYPES = ["UNSAFE_ACT", "UNSAFE_CONDITION", "NEAR_MISS"]

TODAY = dt.date(2026, 8, 25)


def rand_date(start_days_ago, end_days_ago):
    d = random.randint(end_days_ago, start_days_ago)
    return TODAY - dt.timedelta(days=d)


# ---- Pattern A: Electrical Isolation (varied wording, same underlying event) ----
ELECTRICAL_TEMPLATES = [
    "Technician entered energized pump area before electrical isolation was verified.",
    "Maintenance was carried out without confirming equipment isolation on the panel.",
    "Electrical panel remained live during scheduled inspection.",
    "LOTO checklist was not verified before crew began work on the compressor.",
    "Equipment was not fully isolated before maintenance work began.",
    "Worker accessed switchgear room without confirming lockout status.",
    "Isolation certificate was missing when crew started work on the motor.",
    "Crew proceeded with repair before isolation verification was signed off.",
    "Panel door was opened while circuit remained energized.",
    "Technician bypassed LOTO procedure to save time during shift changeover.",
    "Energized cable was handled without confirming de-energization.",
    "Isolation tag was removed before work was actually complete.",
    "Maintenance team assumed isolation was done based on verbal confirmation only.",
    "Live wire was exposed during panel maintenance without proper lockout.",
    "Electrical isolation point was not physically verified with a multimeter.",
]

HEIGHT_TEMPLATES = [
    "Worker was observed on scaffold without a secured harness.",
    "Fall protection was not used while inspecting the flare stack platform.",
    "Ladder used for elevated work was damaged and not tagged out of service.",
    "Open edge on the platform lacked guardrails during maintenance.",
    "Technician climbed to elevated work area without anchor point confirmed.",
    "Unsecured harness was noted during rooftop inspection.",
    "Missing barricade at an open edge on the tank platform.",
    "Worker used an unsafe ladder that was not rated for the task.",
    "Fall arrest lanyard was not connected during crane basket operation.",
    "Scaffold inspection tag was expired but crew worked on it anyway.",
    "Elevated work platform was accessed without edge protection in place.",
    "Worker was seen without fall protection while cleaning the tank roof.",
]

PERMIT_TEMPLATES = [
    "Hot work began without a valid permit issued by the site safety officer.",
    "Permit-to-work was not verified before excavation started near the pipeline.",
    "Crew proceeded with hazardous confined work without a signed permit-to-work.",
    "Expired permit was used to authorize work on the process unit.",
    "Work was carried out without permit verification by the shift supervisor.",
    "Missing PTW was discovered during a routine safety walkdown.",
    "Permit conditions were not reviewed with the crew before work began.",
    "Contractor started grinding work without an approved hot work permit.",
]

VEHICLE_TEMPLATES = [
    "A near miss occurred when a reversing truck came close to a pedestrian walkway.",
    "Vehicle backed up without a spotter present near the loading bay.",
    "Pedestrian and forklift nearly collided in a blind spot near the warehouse.",
    "Reverse alarm on the site vehicle was found to be non-functional.",
    "Worker crossed the vehicle movement zone without using the designated walkway.",
    "Truck reversed into a restricted pedestrian zone without a signal.",
    "Poor visibility at the site gate led to a near miss between a light vehicle and a walker.",
]

CONFINED_TEMPLATES = [
    "Gas testing was skipped before confined space entry into the tank.",
    "Entry permit for the vessel was not verified prior to confined space work.",
    "Standby attendant was absent during confined space entry at the separator.",
    "Rescue equipment was unavailable at the confined space work site.",
    "Oxygen levels inside the storage vessel were not checked before confined space entry.",
    "Crew proceeded with confined space entry without completing the required gas test.",
    "Confined space permit was missing when workers entered the vessel for cleaning.",
]

NOISE_TEMPLATES = [
    "Minor lubricant drip on the workshop floor was cleaned up promptly with no injury.",
    "Housekeeping issue noted in the tool storage area.",
    "Fire extinguisher inspection tag found out of date in the break room.",
    "Signage for emergency assembly point was faded and needs replacement.",
    "First aid kit in the workshop was found short a few items.",
    "Noise levels in the compressor room exceeded comfort during routine operation.",
    "Trip hazard from a loose cable was reported and fixed same day.",
    "Waste segregation bins were not properly labeled at the site office.",
    "Minor vehicle scratch reported during routine parking maneuver, no injury.",
    "A dripping faucet was reported in the site canteen and referred to facilities.",
    "Temporary lighting was insufficient in the storage yard at night.",
    "Employee suggestion box was full and needs regular clearing.",
]


def make_reports(templates, category, report_type_bias, n, date_range, pattern_label,
                  trend="stable", contractor_pool=None, dept_pool=None):
    reports = []
    contractor_pool = contractor_pool or CONTRACTORS
    dept_pool = dept_pool or DEPARTMENTS
    start_days, end_days = date_range

    for i in range(n):
        template = random.choice(templates)
        if trend == "increasing":
            # weight dates toward recent (small end_days)
            weight = random.random() ** 2
            days_ago = int(end_days + weight * (start_days - end_days))
        elif trend == "decreasing":
            weight = random.random() ** 2
            days_ago = int(start_days - weight * (start_days - end_days))
        elif trend == "new":
            days_ago = random.randint(end_days, min(end_days + 20, start_days))
        else:
            days_ago = random.randint(end_days, start_days)

        reports.append({
            "report_date": TODAY - dt.timedelta(days=days_ago),
            "report_type": random.choice(report_type_bias),
            "location": random.choice(SITES),
            "site": random.choice(SITES),
            "department": random.choice(dept_pool),
            "contractor": random.choice(contractor_pool),
            "reporter_role": random.choice(REPORTER_ROLES),
            "description": template,
            "severity": random.choice(["LOW", "MODERATE", "HIGH"]),
            "planted_pattern": pattern_label,
        })
    return reports


def generate(n_total_target=1000, out_path=None):
    all_reports = []

    all_reports += make_reports(ELECTRICAL_TEMPLATES, "Electrical",
                                 ["UNSAFE_ACT", "UNSAFE_CONDITION", "NEAR_MISS"],
                                 n=52, date_range=(120, 0), pattern_label="electrical_isolation",
                                 trend="increasing")

    all_reports += make_reports(HEIGHT_TEMPLATES, "Working at Height",
                                 ["UNSAFE_CONDITION", "UNSAFE_ACT"],
                                 n=36, date_range=(150, 0), pattern_label="working_at_height",
                                 trend="stable")

    all_reports += make_reports(PERMIT_TEMPLATES, "Permit to Work",
                                 ["UNSAFE_ACT", "UNSAFE_CONDITION"],
                                 n=26, date_range=(150, 30), pattern_label="permit_to_work",
                                 trend="decreasing")

    all_reports += make_reports(VEHICLE_TEMPLATES, "Vehicle / Mobile Equipment",
                                 ["NEAR_MISS", "UNSAFE_CONDITION"],
                                 n=20, date_range=(35, 0), pattern_label="vehicle_pedestrian",
                                 trend="new")

    all_reports += make_reports(CONFINED_TEMPLATES, "Confined Space",
                                 ["UNSAFE_CONDITION", "NEAR_MISS"],
                                 n=16, date_range=(90, 0), pattern_label="confined_space",
                                 trend="increasing")

    # Noise: unrelated reports so clustering is meaningful (spec section 27)
    n_noise = max(n_total_target - len(all_reports), 0)
    all_reports += make_reports(NOISE_TEMPLATES, "Other",
                                 REPORT_TYPES, n=n_noise, date_range=(180, 0),
                                 pattern_label=None, trend="stable")

    random.shuffle(all_reports)

    if out_path:
        fieldnames = ["report_date", "report_type", "location", "site", "department",
                      "contractor", "reporter_role", "description", "severity", "planted_pattern"]
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in all_reports:
                row = dict(r)
                row["report_date"] = row["report_date"].isoformat()
                writer.writerow(row)

    return all_reports


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "samples" / "synthetic_reports.csv")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    reports = generate(out_path=out)
    print(f"Generated {len(reports)} synthetic reports -> {out}")
