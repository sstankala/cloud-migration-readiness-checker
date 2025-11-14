#!/usr/bin/env python3
import json
import datetime
from typing import List, Dict, Any

import streamlit as st
import pandas as pd

# -------------------------
# Question & scoring logic
# -------------------------

SCALE_HELP = """
**Scale (1–5):**

1 = Strongly Disagree / Not in place  
2 = Partially in place, ad-hoc  
3 = Defined, but inconsistently followed  
4 = Well-established and usually followed  
5 = Fully mature, measured and continuously improved
"""

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


def compute_scores(answers: Dict[str, int]) -> Dict[str, Any]:
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

    overall = round(sum(answers.values()) / len(answers), 2)

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


def identify_gaps(scores: Dict[str, float], threshold: float = 3.0):
    return [dim for dim, score in scores.items() if score < threshold]


def build_migration_wave_plan(scores: Dict[str, float]):
    overall = sum(scores.values()) / len(scores) if scores else 0
    plan = []

    plan.append("**Wave 0: Foundational work**")
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

    plan.append("**Wave 1: Low-risk / non-critical workloads**")
    plan.append(
        "- Migrate dev/test or internal, low-criticality apps using rehost/replatform patterns."
    )
    plan.append(
        "- Use these as pilots to validate landing zone, operations, and security controls."
    )

    plan.append("**Wave 2: Business-critical workloads**")
    if overall >= 3:
        plan.append(
            "- Migrate customer-facing or revenue-critical systems with clear rollback and DR plans."
        )
        plan.append(
            "- Introduce refactoring where there is clear business value (managed DBs, autoscaling, etc.)."
        )
    else:
        plan.append(
            "- Defer business-critical workloads until foundational gaps are addressed and Wave 1 lessons are incorporated."
        )

    plan.append("**Wave 3: Optimization & modernization**")
    plan.append(
        "- Optimize cost (right-sizing, Savings Plans/RIs) and reliability (multi-AZ, backups, chaos testing)."
    )
    plan.append(
        "- Modernize legacy components where justified (serverless, containers, event-driven architectures)."
    )

    return plan


def recommend_aws_services(scores: Dict[str, float]) -> Dict[str, list]:
    recs: Dict[str, list] = {}

    if scores.get("security", 0) < 3.5:
        recs["Security"] = [
            "AWS Organizations & AWS Control Tower for multi-account governance",
            "AWS IAM Identity Center and IAM best practices",
            "AWS Security Hub and AWS Config for compliance visibility",
            "Amazon GuardDuty and AWS CloudTrail for threat detection and auditing",
        ]

    if scores.get("operations", 0) < 3.5:
        recs["Operations"] = [
            "Amazon CloudWatch (metrics, logs, alarms, dashboards)",
            "AWS Systems Manager (run command, patching, parameter store)",
            "AWS CloudTrail for API auditing and troubleshooting",
        ]

    if scores.get("cost", 0) < 3.5:
        recs["Cost"] = [
            "AWS Cost Explorer and AWS Budgets",
            "AWS Cost and Usage Report (CUR)",
            "Use tagging strategy for cost allocation and showback/chargeback",
        ]

    if scores.get("skills", 0) < 3.5:
        recs["Team Skills"] = [
            "AWS Skill Builder and AWS Training & Certification programs",
            "Hands-on labs and game days for core migration team",
        ]

    if scores.get("governance", 0) < 3.5 or scores.get("process", 0) < 3.5:
        recs["Governance & Process"] = [
            "Adopt AWS Cloud Adoption Framework (CAF) for holistic planning",
            "Define landing zone patterns (Control Tower / custom) and guardrails",
            "Use AWS Application Migration Service or Migration Hub for structured migrations",
        ]

    return recs


# -------------------------
# Streamlit UI
# -------------------------

st.set_page_config(
    page_title="Cloud Migration Readiness Analyzer",
    layout="wide",
)

st.title("☁️ Cloud Migration Readiness Analyzer")
st.caption("AWS CAF + Well-Architected–inspired readiness check")

st.markdown(SCALE_HELP)

with st.sidebar:
    st.header("Settings")
    threshold = st.slider(
        "Gap threshold (min score before it's considered a gap)",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5,
    )
    st.markdown(
        """
        This app is a **lightweight, educational tool** inspired by the  
        AWS Cloud Adoption Framework (CAF) and Well-Architected pillars.
        """
    )

st.markdown("---")

with st.form("readiness_form"):
    st.subheader("Readiness Questions")

    answers: Dict[str, int] = {}
    # Group questions by dimension visually
    dims_order = ["security", "operations", "cost", "skills", "governance", "process"]
    dim_labels = {
        "security": "Security",
        "operations": "Operations",
        "cost": "Cost Maturity",
        "skills": "Team Skills",
        "governance": "Governance & Platform",
        "process": "Migration Process",
    }

    for dim in dims_order:
        dim_questions = [q for q in QUESTIONS if q["dimension"] == dim]
        if not dim_questions:
            continue
        st.markdown(f"### {dim_labels.get(dim, dim.title())}")
        for q in dim_questions:
            answers[q["id"]] = st.slider(
                q["text"],
                min_value=1,
                max_value=5,
                value=3,
                step=1,
                key=q["id"],
            )

    submitted = st.form_submit_button("Run Assessment")

if submitted:
    # Compute results
    score_result = compute_scores(answers)
    dim_scores = score_result["dimension_scores"]
    gaps = identify_gaps(dim_scores, threshold=threshold)
    wave_plan = build_migration_wave_plan(dim_scores)
    aws_recs = recommend_aws_services(dim_scores)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    result = {
        "timestamp_utc": timestamp,
        "answers": answers,
        "dimension_scores": dim_scores,
        "overall_score": score_result["overall_score"],
        "readiness_level": score_result["readiness_level"],
        "gaps_below_threshold": {
            "threshold": threshold,
            "dimensions": gaps,
        },
        "migration_wave_plan": wave_plan,
        "aws_recommendations": aws_recs,
        "metadata": {
            "frameworks": {
                "aws_caf": [
                    "Business",
                    "People",
                    "Governance",
                    "Platform",
                    "Security",
                    "Operations",
                ],
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

    st.success("Assessment complete")

    # Top KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Readiness Score", f"{score_result['overall_score']:.2f} / 5")
    with col2:
        st.metric("Readiness Level", score_result["readiness_level"])
    with col3:
        st.metric("Number of Gaps", len(gaps))

    st.markdown("### Dimension Scores")
    dim_df = pd.DataFrame(
        {
            "Dimension": [dim_labels.get(d, d.title()) for d in dim_scores.keys()],
            "Score": list(dim_scores.values()),
        }
    ).set_index("Dimension")
    st.bar_chart(dim_df)

    if gaps:
        st.markdown("### Gaps & Risks")
        for g in gaps:
            st.warning(
                f"{dim_labels.get(g, g.title())} is below the threshold ({threshold}).",
                icon="⚠️",
            )
    else:
        st.markdown("### Gaps & Risks")
        st.info("No dimensions are below the selected threshold.", icon="✅")

    st.markdown("### Migration Wave Plan")
    for line in wave_plan:
        if line.startswith("**Wave"):
            st.markdown(line)
        else:
            st.markdown(line)

    st.markdown("### Recommended AWS Services & Focus Areas")
    if aws_recs:
        for category, rec_list in aws_recs.items():
            with st.expander(category, expanded=True):
                for item in rec_list:
                    st.markdown(f"- {item}")
    else:
        st.info("No specific AWS recommendations – your scores are strong across all areas.")

    st.markdown("### JSON Output")
    json_str = json.dumps(result, indent=2)
    st.code(json_str, language="json")

    st.download_button(
        label="Download JSON result",
        data=json_str.encode("utf-8"),
        file_name=f"readiness_result_{timestamp}.json",
        mime="application/json",
    )
else:
    st.info("Fill in the sliders above and click **Run Assessment** to see your readiness dashboard.")
