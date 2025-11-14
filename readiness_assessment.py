#!/usr/bin/env python3
"""
Cloud Migration Readiness Analyzer
- Based on AWS CAF perspectives + AWS Well-Architected pillars (lightweight)
- Simple interactive CLI
- Outputs JSON file with detailed results
"""

import json
import datetime
import os
from typing import List, Dict, Any

# 1–5 scale explanations (printed once at the top)
SCALE_HELP = """
Please answer each question on a scale from 1 to 5:

1 = Strongly Disagree / Not in place
2 = Partially in place, ad-hoc
3 = Defined, but inconsistently followed
4 = Well-established and usually followed
5 = Fully mature, measured and continuously improved
"""

# Questions mapped to dimensions + CAF perspectives + Well-Architected pillars
QUESTIONS: List[Dict[str, Any]] = [
    # SECURITY
    {
        "id": "sec_1",
        "text": "We have a clear security baseline and policies that would apply to workloads in AWS.",
        "dimension": "security",
        "caf_perspective": "Security",
        "well_arch_pillar": "Security",
    },
    {
        "id": "sec_2",
        "text": "We have a defined process for identity and access management (IAM) across teams.",
        "dimension": "security",
        "caf_perspective": "Security",
        "well_arch_pillar": "Security",
    },
    # OPERATIONS
    {
        "id": "ops_1",
        "text": "We have monitoring, logging, and alerting in place for our critical workloads.",
        "dimension": "operations",
        "caf_perspective": "Operations",
        "well_arch_pillar": "Operational Excellence",
    },
    {
        "id": "ops_2",
        "text": "We have repeatable runbooks and incident response procedures.",
        "dimension": "operations",
        "caf_perspective": "Operations",
        "well_arch_pillar": "Reliability",
    },
    # COST
    {
        "id": "cost_1",
        "text": "We actively track and review IT infrastructure costs today.",
        "dimension": "cost",
        "caf_perspective": "Business",
        "well_arch_pillar": "Cost Optimization",
    },
    {
        "id": "cost_2",
        "text": "We use budgets/forecasts to plan and optimize future infrastructure spend.",
        "dimension": "cost",
        "caf_perspective": "Business",
        "well_arch_pillar": "Cost Optimization",
    },
    # TEAM SKILLS / PEOPLE
    {
        "id": "skills_1",
        "text": "Our teams have hands-on experience with AWS or other public clouds.",
        "dimension": "skills",
        "caf_perspective": "People",
        "well_arch_pillar": "Operational Excellence",
    },
    {
        "id": "skills_2",
        "text": "We have a defined plan to upskill staff on cloud architecture, security, and operations.",
        "dimension": "skills",
        "caf_perspective": "People",
        "well_arch_pillar": "Operational Excellence",
    },
    # GOVERNANCE / PLATFORM / STRATEGY
    {
        "id": "gov_1",
        "text": "We have executive sponsorship and a clear business case for moving to AWS.",
        "dimension": "governance",
        "caf_perspective": "Business",
        "well_arch_pillar": "Operational Excellence",
    },
    {
        "id": "gov_2",
        "text": "We have documented standards for networking, accounts, and environments (e.g., dev/test/prod).",
        "dimension": "governance",
        "caf_perspective": "Platform",
        "well_arch_pillar": "Reliability",
    },
    # MIGRATION PROCESS / OPERATING MODEL
    {
        "id": "process_1",
        "text": "We have an inventory of applications and dependencies to plan migration waves.",
        "dimension": "process",
        "caf_perspective": "Platform",
        "well_arch_pillar": "Reliability",
    },
    {
        "id": "process_2",
        "text": "We have defined criteria for which apps to rehost, replatform, or refactor.",
        "dimension": "process",
        "caf_perspective": "Governance",
        "well_arch_pillar": "Operational Excellence",
    },
]


def ask_question(q: Dict[str, Any]) -> int:
    """Prompt the user for a numeric answer between 1 and 5."""
    while True:
        try:
            answer = input(f"\n{q['text']}\n[1-5]: ").strip()
            value = int(answer)
            if 1 <= value <= 5:
                return value
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")


def compute_scores(answers: Dict[str, int]) -> Dict[str, Any]:
    """Aggregate scores per dimension and overall."""
    dim_totals: Dict[str, int] = {}
    dim_counts: Dict[str, int] = {}

    for q in QUESTIONS:
        dim = q["dimension"]
        score = answers[q["id"]]
        dim_totals[dim] = dim_totals.get(dim, 0) + score
        dim_counts[dim] = dim_counts.get(dim, 0) + 1

    dim_scores = {
        dim: round(dim_totals[dim] / dim_counts[dim], 2) for dim in dim_totals
    }

    # Overall is simple average of all questions
    overall = round(sum(answers.values()) / len(answers), 2)

    # Readiness level based on overall score
    if overall < 2.0:
        level = "Not Ready"
    elif overall < 3.0:
        level = "Partially Ready"
    elif overall < 4.0:
        level = "Ready with Some Gaps"
    else:
        level = "Well Prepared"

    return {
        "dimension_scores": dim_scores,
        "overall_score": overall,
        "readiness_level": level,
    }


def identify_gaps(scores: Dict[str, float], threshold: float = 3.0) -> List[str]:
    """Return list of dimension names that are below the threshold."""
    return [dim for dim, score in scores.items() if score < threshold]


def build_migration_wave_plan(scores: Dict[str, float]) -> List[str]:
    """
    Very simple wave guidance based on readiness.
    In a real ProServe-type engagement, this would be elaborated with app inventory.
    """
    overall = sum(scores.values()) / len(scores) if scores else 0

    plan = []
    plan.append("Wave 0: Foundational work")
    if scores.get("security", 0) < 3 or scores.get("governance", 0) < 3:
        plan.append(
            "- Establish landing zone (accounts, org structure, networking, IAM, baseline security controls)."
        )
    if scores.get("skills", 0) < 3:
        plan.append(
            "- Run focused training for core team (AWS Fundamentals, Architecting on AWS, security/ops)."
        )
    if scores.get("process", 0) < 3:
        plan.append(
            "- Build application inventory, dependency mapping, and define migration decision framework (7 Rs)."
        )

    plan.append("Wave 1: Low-risk / non-critical workloads")
    plan.append(
        "- Migrate dev/test or internal, low-criticality apps using rehost/replatform patterns."
    )
    plan.append(
        "- Use these as pilots to validate landing zone, operations, and security controls."
    )

    plan.append("Wave 2: Business-critical workloads")
    if overall >= 3:
        plan.append(
            "- Migrate customer-facing or revenue-critical systems with clear rollback and DR plans."
        )
        plan.append(
            "- Introduce refactoring where there is clear business value (e.g., managed databases, autoscaling)."
        )
    else:
        plan.append(
            "- Defer business-critical workloads until foundational gaps are addressed and Wave 1 lessons are incorporated."
        )

    plan.append("Wave 3: Optimization & modernization")
    plan.append(
        "- Optimize cost (right-sizing, Savings Plans/RIs) and reliability (multi-AZ, backups, chaos testing)."
    )
    plan.append(
        "- Modernize legacy components where justified (serverless, containers, event-driven architectures)."
    )

    return plan


def recommend_aws_services(scores: Dict[str, float]) -> Dict[str, List[str]]:
    """
    Simple mapping of low-scorings to suggested AWS services/features.
    This is intentionally high-level for a portfolio/learning project.
    """
    recs: Dict[str, List[str]] = {}

    if scores.get("security", 0) < 3.5:
        recs["security"] = [
            "AWS Organizations & AWS Control Tower for multi-account governance",
            "AWS IAM Identity Center and IAM best practices",
            "AWS Security Hub and AWS Config for compliance visibility",
            "Amazon GuardDuty and AWS CloudTrail for threat detection and auditing",
        ]

    if scores.get("operations", 0) < 3.5:
        recs["operations"] = [
            "Amazon CloudWatch (metrics, logs, alarms, dashboards)",
            "AWS Systems Manager (run command, patching, parameter store)",
            "AWS CloudTrail for API auditing and troubleshooting",
        ]

    if scores.get("cost", 0) < 3.5:
        recs["cost"] = [
            "AWS Cost Explorer and AWS Budgets",
            "AWS Cost and Usage Report (CUR)",
            "Use tagging strategy for cost allocation and showback/chargeback",
        ]

    if scores.get("skills", 0) < 3.5:
        recs["skills"] = [
            "AWS Skill Builder and AWS Training & Certification programs",
            "Hands-on labs and game days for core migration team",
        ]

    if scores.get("governance", 0) < 3.5 or scores.get("process", 0) < 3.5:
        recs["governance_process"] = [
            "Adopt AWS Cloud Adoption Framework (CAF) for holistic planning",
            "Define landing zone patterns (Control Tower / custom) and guardrails",
            "Use AWS Application Migration Service or Migration Hub for structured migrations",
        ]

    return recs


def main() -> None:
    print("=== Cloud Migration Readiness Analyzer ===")
    print(SCALE_HELP)

    answers: Dict[str, int] = {}
    for q in QUESTIONS:
        answers[q["id"]] = ask_question(q)

    score_result = compute_scores(answers)
    dim_scores = score_result["dimension_scores"]
    gaps = identify_gaps(dim_scores, threshold=3.0)
    wave_plan = build_migration_wave_plan(dim_scores)
    aws_recs = recommend_aws_services(dim_scores)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_filename = f"readiness_result_{timestamp}.json"

    result = {
        "timestamp_utc": timestamp,
        "answers": answers,
        "dimension_scores": dim_scores,
        "overall_score": score_result["overall_score"],
        "readiness_level": score_result["readiness_level"],
        "gaps_below_threshold_3": gaps,
        "migration_wave_plan": wave_plan,
        "aws_recommendations": aws_recs,
        "metadata": {
            "frameworks": {
                "aws_caf": ["Business", "People", "Governance", "Platform", "Security", "Operations"],
                "aws_well_architected": [
                    "Operational Excellence",
                    "Security",
                    "Reliability",
                    "Performance Efficiency",
                    "Cost Optimization",
                    "Sustainability",
                ],
            }
        },
    }

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Simple console summary
    print("\n=== Assessment Complete ===")
    print(f"Overall readiness score: {score_result['overall_score']} / 5")
    print(f"Readiness level        : {score_result['readiness_level']}")
    print("\nDimension scores:")
    for dim, score in dim_scores.items():
        print(f"  - {dim}: {score}/5")

    if gaps:
        print("\nKey gaps (score < 3.0):")
        for g in gaps:
            print(f"  - {g}")
    else:
        print("\nNo major gaps under threshold 3.0 detected.")

    print(f"\nDetailed JSON output saved to: {os.path.abspath(output_filename)}")


if __name__ == "__main__":
    main()
