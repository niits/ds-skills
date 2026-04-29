# Literature Search Strategies — Banking Domain

## Finding Evidence for Banking DS Hypotheses

In banking DS, the primary evidence base is internal. External literature is used to:
- Validate that a proposed mechanism is theoretically sound
- Find precedent for a methodology (required by model validators)
- Understand industry benchmarks and failure patterns
- Support regulatory filings (NHNN, Basel)

**Do not spend more than 30–60 minutes on external search for sprint-level investigations.** Reserve deep literature search for formal model validation documents, research initiatives, and methodology papers.

---

## Evidence Hierarchy in Banking DS

Rank evidence sources in this order. Higher is stronger.

| Tier | Source | Use |
|---|---|---|
| **1 — Internal primary data** | Model monitoring reports, vintage performance, PSI/CSI logs | First stop for any investigation |
| **2 — Internal historical** | Prior validation reports, model inventory, A/B test logs, credit committee minutes | Context on known model weaknesses and decisions |
| **3 — Regulatory guidance** | NHNN circulars, Basel III, IFRS 9, EBA guidelines | Methodology requirements, definitions |
| **4 — Industry methodology** | BIS working papers, Moody's Analytics, Oliver Wyman, McKinsey | Applied techniques, benchmarks |
| **5 — Academic literature** | SSRN, Journal of Credit Risk, Journal of Banking & Finance | Theoretical foundations, novel methods |

---

## Internal Sources — Search First

### Model Monitoring Reports

**What to look for:** PSI, CSI, Gini/KS trend, calibration drift, approval rate trend, vintage performance curves.

**Where to find:**
- Model Risk Management (MRM) team quarterly reports
- Risk MIS / BI dashboard (Databricks SQL, PowerBI)
- IFRS 9 ECL back-testing reports

**Search approach:**
- Pull PSI by feature for the last 6–12 months → identifies drifting features
- Pull KS/AUC by origination vintage → identifies when degradation started
- Compare score distribution (CSI) between training population and recent originations

### Model Inventory and Validation Reports

**What to look for:** Known limitations documented in prior validation, conditions for model use, approved feature list, monitoring thresholds.

**Why critical:** Validators will reference prior validation findings. If your hypothesis proposes a fix for a previously identified weakness, cite the original finding.

**Search approach:**
- Check model inventory for current model version, approval date, and outstanding conditions
- Read the "Model Limitations" and "Recommended Monitoring" sections of the last validation report
- Check if the current issue was flagged as a known risk in prior validation

### Credit Committee and Strategy Papers

**What to look for:** Policy changes that coincide with performance degradation (cutoff moves, new channel launches, product changes, collection strategy pivots).

**Why critical:** Many "model performance issues" are actually policy changes that altered the application population. The model is stable; the population shifted.

**Search approach:**
- Request credit strategy papers from the past 12 months
- Match dates of origination strategy changes to vintage performance degradation start dates

### Data Lineage and ETL Documentation

**What to look for:** Changes to source systems, field definitions, imputation logic, upstream ETL jobs, bureau product subscriptions.

**Why critical:** The most common cause of sudden performance degradation in production is an upstream data change that was not communicated to the model team.

**Search approach:**
- Check data quality reports for missing rate trends on key model features
- Query feature value distributions before and after the suspected change date
- Contact data engineering team for ETL change log around the degradation period

---

## Regulatory Sources

### NHNN / State Bank of Vietnam

**URL:** sbv.gov.vn / vbpl.vn

**Key documents for banking DS:**
- Circular 41/2016/TT-NHNN: Credit risk capital requirements (IRB approach, PD/LGD/EAD definitions)
- Circular 11/2021/TT-NHNN: Debt classification and provisioning (relevant for IFRS 9 alignment)
- Circular 13/2018/TT-NHNN: Internal capital adequacy assessment process (ICAAP)
- Decision 493/2005/QD-NHNN: Credit risk classification (5-group classification system)

**Search strategy:**
- Search "Circular [number]" on vbpl.vn for official Vietnamese text
- For English summaries: search "[circular number] NHNN English" on BIS website or law firm publications
- When citing in reports: use full circular number and issue date

### Basel Committee (BIS)

**URL:** bis.org/bcbs

**Key documents:**
- Basel III: Capital requirements for credit, market, and operational risk
- BCBS 239: Principles for effective risk data aggregation (model data quality)
- BCBS d445: Supervisory guidance on model risk management (direct equivalent of SR 11-7)
- CP 15: Climate-related financial risks (growing importance for ESG credit modeling)

**Search strategy:**
- Use BIS search: `site:bis.org [topic]` or bis.org/search
- Filter by "BCBS" (Basel Committee documents) vs "BIS Research" (working papers)
- Working papers (BIS WP series) are pre-publication research — cite with "forthcoming" or paper number

### SR 11-7 Equivalent (US Federal Reserve — widely adopted as industry standard)

**SR 11-7:** "Guidance on Model Risk Management" — the de facto global standard for banking model governance, widely referenced in Vietnamese bank model risk policies.

**Key principles for hypothesis work:**
- Models require documented conceptual soundness (literature support for the methodology)
- Champion-challenger is the standard for model comparison
- Ongoing monitoring requires documented thresholds and escalation procedures

**Where to find:** federalreserve.gov/supervisionreg/srletters/sr1107.htm

### IFRS 9 (for credit provisioning models)

**Key documents:**
- IFRS 9 Financial Instruments (IASB) — the standard itself
- EBA Guidelines on PD estimation, LGD estimation, and treatment of defaulted exposures
- Basel BCBS d350: Guidance on credit risk and accounting for expected credit losses

---

## Industry Methodology Sources

### BIS Working Papers (bis.org/research)

**What to find here:**
- Central bank research on credit risk through the cycle
- PD/LGD estimation methodologies
- Macro-financial models and stress testing frameworks
- Digital finance and algorithmic credit scoring research

**Search strategy:**
- bis.org/research → Working Papers → search by keyword
- Good search terms: `credit scoring machine learning`, `PD estimation Basel`, `behavioral scoring`, `IFRS 9 ECL methodology`, `fraud detection neural network`
- Filter by year (last 3 years for current methods)

### SSRN — Social Science Research Network

**URL:** ssrn.com

**Relevant networks:**
- Financial Economics Network → Banking & Financial Institutions
- Econometrics → Applied Econometrics
- Operations Research → Risk Management

**What to find here:**
- Pre-publication versions of academic papers (free, before journal paywall)
- Industry practitioner papers
- Conference presentations from RiskMinds, GARP, CRO Forum

**Search strategy:**
- `"credit scoring" machine learning` — current ML methods for credit
- `"probability of default" estimation Vietnam` — local market evidence
- `"champion challenger" model validation` — methodology papers
- `fraud detection XGBoost banking` — applied fraud methods
- `SHAP credit risk explanation` — explainability in regulated models

### Moody's Analytics and S&P Global

**What to find here:**
- Methodology papers for RiskCalc, CreditEdge (commercial PD models)
- Annual default studies with empirical PD benchmarks by rating, industry, region
- Stress testing frameworks and ECL methodology guides

**Access:** Moody's research hub (moodysanalytics.com) — may require subscription. Key free resource: Annual Default Study (published each year, widely cited).

**Useful for:** Benchmarking your PD model against observed industry default rates. "Is a 3.5% predicted PD for this segment reasonable?" → check Moody's default study for comparable obligors.

### Oliver Wyman, McKinsey Global Banking Practice, BCG

**What to find here:**
- Industry benchmarks for credit model performance
- Best practice papers on digital lending, fraud, AML
- Market-level data on default rates, NPA ratios, credit growth

**Access:** Reports published on firm websites (free) or through industry association partnerships.

**Search strategy:** Google `"Oliver Wyman" credit risk model 2024` or `"McKinsey" banking fraud detection report`

**Note:** These are practitioner reports, not peer-reviewed. Cite as "industry practice" not "academic evidence." Validators accept them for benchmarking, not for methodology justification.

---

## Academic Literature

### Key Journals for Banking DS

| Journal | Focus | Access |
|---|---|---|
| Journal of Credit Risk | Credit risk models, PD/LGD, stress testing | Subscription (Incisive Media) |
| Journal of Banking & Finance | Empirical banking, credit markets, financial stability | Subscription (Elsevier); free via SSRN often |
| Journal of Financial Economics | Corporate finance, credit theory | Subscription; papers on SSRN |
| Review of Financial Studies | Asset pricing, credit risk | Subscription |
| Expert Systems with Applications | Applied ML in finance, fraud detection | Subscription (Elsevier) |
| Decision Support Systems | ML models in banking decisions | Subscription (Elsevier) |

**For ML/AI in banking specifically:**
- KDD, NeurIPS, ICML proceedings — methodological papers on tree models, neural nets, SHAP
- AAAI FinSI workshop — AI in financial services
- ACM FAccT — algorithmic fairness (relevant for fair lending)

### How to Access Without Subscription

1. **SSRN pre-print:** Search author + paper title on ssrn.com
2. **Google Scholar:** Often links to free PDF versions hosted by authors or institutions
3. **Unpaywall browser extension:** Automatically finds legal free versions
4. **ResearchGate:** Authors often post their papers; message author directly if not available

---

## Search Strategies by Investigation Type

### Investigating Model Performance Degradation

**Internal search (do first):**
- PSI report by feature → identify drifting features
- Vintage KS chart → identify when degradation started
- Credit strategy papers from degradation period → identify policy changes

**External search (if mechanism is unclear after internal):**
- SSRN: `credit score drift population shift` → methods for drift detection
- BIS working papers: `credit cycle application scorecard` → cyclical PD behavior
- Journal of Credit Risk: `model stability through the cycle`

### Investigating Fraud Model Improvement

**Internal search:**
- Current model SHAP values → what features are driving scores
- False positive/negative analysis by fraud type (card fraud vs. account takeover vs. synthetic identity)
- Transaction pattern analysis in confirmed fraud cases vs. FP cases

**External search:**
- SSRN: `card fraud detection ensemble` or `account takeover detection graph neural network`
- KDD / NeurIPS: applied fraud detection papers
- FICO World conference papers (available online): industry fraud methodology

### Investigating Credit Limit / Collections Policy

**Internal search:**
- A/B test logs from prior experiments
- Vintage performance by credit limit band
- Collections cure rate by contact strategy

**External search:**
- SSRN: `credit limit effects default probability` — academic evidence on limit-default relationship
- BIS: `revolving credit behavioral scoring` — behavioral data in credit decisions
- Journal of Banking & Finance: `collections strategy field experiment`

### Investigating AML / Transaction Monitoring

**Internal search:**
- SAR (Suspicious Activity Report) patterns in confirmed cases
- Alert rate trends by rule and customer segment
- False positive analysis by alert type

**External search:**
- FATF (fatf-gafi.org): guidance papers on risk-based AML approach
- Wolfsberg Group principles (wolfsberg-principles.com): correspondent banking, transaction monitoring
- SSRN: `anti-money laundering machine learning` — applied ML for AML

---

## Citation Standards for Banking Reports

### In Model Validation Documents (formal reports)

- Always cite full document: Author, Year, Title, Source, Section number if applicable
- For regulatory documents: cite circular number and article number
- For internal documents: cite document name, version number, date, owner department
- Format: `(BCBS d239, 2013, Principle 2)` or `(NHNN Circular 41/2016, Article 7)`

### In Investigation Notebooks (Databricks %md cells)

Lighter format is acceptable:
- External: `(BIS WP 735, Fuster et al. 2022)` 
- Internal: `(Model Monitoring Report Q3 2024)` or `(Mortgage Scorecard v3.1 Validation Report, 2023)`
- When citing industry benchmarks: `(Moody's Annual Default Study 2024, Global speculative grade)`

### Citation volume targets

| Document type | Minimum citations |
|---|---|
| Sprint investigation notebook | 0–3 (internal evidence dominant; external only if needed for methodology) |
| Formal model validation report | 10–20 (methodology citations, regulatory references, benchmark sources) |
| Research / methodology paper | 20–40 (full academic grounding) |

---

## Time Allocation for Literature Search

| Investigation type | Internal search | External search | Total |
|---|---|---|---|
| Production incident (urgent) | 30–60 min | 0–15 min | < 90 min |
| Sprint feature investigation | 1–2 hours | 30–60 min | 2–3 hours |
| Formal model validation (methodology section) | 2–3 hours | 2–4 hours | 4–7 hours |
| Research initiative | 3–5 hours | 5–10 hours | Full day+ |

**Stop external search when:** You have found 2–3 sources supporting the mechanism and 1 source discussing potential pitfalls. More search beyond that has diminishing returns for sprint-level work.

---

## Common Pitfalls

### Skipping Internal Evidence
Starting with academic papers before checking the PSI report wastes time. The answer is almost always in the internal data.

### Citing Practitioner Reports as Methodology Justification
Oliver Wyman and McKinsey reports can establish benchmarks but cannot justify a methodology choice. For methodology, use academic papers or Basel/NHNN guidance.

### Using Out-of-Date Regulatory References
NHNN circulars are updated regularly. Always check the current version on vbpl.vn. Citing a superseded circular in a regulatory submission is a compliance risk.

### Over-Citing
A 2-page investigation notebook does not need 15 citations. Cite only what you actually used. Padding citations is noticed by validators and undermines credibility.

### Misinterpreting US/European Research for Vietnamese Market
US/European default rates, LGD estimates, and behavioral patterns may not apply to Vietnamese borrowers. Always note when adapting foreign research and validate assumptions against internal data.
