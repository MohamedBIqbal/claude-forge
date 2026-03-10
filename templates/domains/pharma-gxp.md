
---

## Pharma/GxP Compliance

### ALCOA+ Principles
All data and records must be:
- **Attributable**: Who performed the action, when
- **Legible**: Clear, readable, permanent
- **Contemporaneous**: Recorded at time of activity
- **Original**: First capture or certified copy
- **Accurate**: No errors, truthful
- **Complete**: All data, including repeat/reanalysis
- **Consistent**: Chronological, dated, no unexplained gaps
- **Enduring**: Durable for retention period
- **Available**: Accessible for review/audit

### Audit Trail Requirements
- Log all user actions with timestamp and user ID
- Record before/after values for changes
- Audit trails must be immutable
- Include reason for change where applicable

### Validation Considerations
- Document AI model versions used
- Track prompt versions (consider prompt versioning skill)
- Validate output quality against acceptance criteria
- Maintain traceability from input to output

### 21 CFR Part 11 Guidance
- Electronic signatures where required
- Access controls based on role
- System validation documentation (IQ/OQ/PQ)
- Periodic review of audit trails

### EMA-FDA 10 Guiding Principles for AI in Drug Development

| # | Principle | Requirements |
|---|-----------|--------------|
| 1 | **Human-centric by design** | AI aligns with ethical and human-centric values |
| 2 | **Risk-based approach** | Proportionate validation, risk mitigation, oversight based on context of use |
| 3 | **Adherence to standards** | Follow legal, ethical, technical, scientific, cybersecurity, regulatory standards including GxP |
| 4 | **Clear context of use** | Well-defined role and scope for why AI is being used |
| 5 | **Multidisciplinary expertise** | Integrated expertise covering AI technology and its context throughout lifecycle |
| 6 | **Data governance & documentation** | Provenance, processing steps, decisions documented traceably; privacy/protection maintained |
| 7 | **Model design & development** | Best practices in design and software engineering; fit-for-use data; interpretability, explainability |
| 8 | **Risk-based performance assessment** | Evaluate complete system including human-AI interactions with appropriate metrics |
| 9 | **Life cycle management** | Quality management throughout lifecycle; monitoring; periodic re-evaluation; address data drift |
| 10 | **Clear, essential information** | Plain language for users/patients: context, performance, limitations, data, updates |

**Source:** [EMA-FDA Guiding Principles (Jan 2026)](https://www.ema.europa.eu/en/documents/other/guiding-principles-good-ai-practice-drug-development_en.pdf)
