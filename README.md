# cloud-migration-readiness-checker

# Cloud Migration Readiness Analyzer
- You can try the deployed version of the tool at https://sstankala-cloud-migration-readiness-checker.streamlit.app/

A lightweight CLI tool that helps assess **cloud migration readiness** using ideas from the **AWS Cloud Adoption Framework (CAF)** and the **AWS Well-Architected Framework**.

You answer a short set of questions (1–5 scale) across:

- Security  
- Operations  
- Cost maturity  
- Team skills  
- Governance & migration process  

The tool outputs:

- Overall readiness score  
- Readiness level (Not Ready → Well Prepared)  
- Gaps & risks by dimension  
- A simple migration wave plan  
- Recommended AWS services/features to explore  
- A JSON file with all results  

---

## How it works

### 1. Question model

Each question is tagged with:

- `dimension` – security, operations, cost, skills, governance, process  
- `caf_perspective` – e.g., Business, People, Platform, Security, Operations  
- `well_arch_pillar` – e.g., Security, Operational Excellence, Cost Optimization  

Internally, the tool:

1. Prompts you for a score from **1 to 5** for each question.
2. Computes average scores per dimension.
3. Computes an overall readiness score.
4. Classifies readiness:

   - `< 2.0` → **Not Ready**  
   - `2.0–2.99` → **Partially Ready**  
   - `3.0–3.99` → **Ready with Some Gaps**  
   - `≥ 4.0` → **Well Prepared**  

5. Flags any dimensions with a score **below 3.0** as gaps.
6. Builds a simple **migration wave plan**.
7. Suggests **AWS services** to investigate for weaker areas.

---

## Installation & Usage

### Prerequisites

- Python 3.8+  
- `git` (optional, if you want to clone a repo)

### Run the CLI

```bash
python readiness_assessment.py
