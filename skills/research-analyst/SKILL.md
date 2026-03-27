---
name: research-analyst
description: |
  Structured research analysis with hypothesis formation, evidence evaluation, and actionable recommendations. Use when users need systematic analysis of a topic, technology evaluation, feasibility studies, literature synthesis, or evidence-based decision support. Complements deep-research by focusing on analytical reasoning rather than report formatting.
---

# Research Analyst

Systematic research analysis skill that forms hypotheses, evaluates evidence, and produces structured analytical assessments.

## Trigger Words

- `/research-analyst`
- "analyze this topic"
- "evaluate the evidence"
- "what does the research say about"
- "feasibility analysis"
- "systematic analysis"

## Quick Start

1. Define the research question and analytical scope
2. Form initial hypotheses or analytical framework
3. Gather and evaluate evidence (quality, relevance, recency)
4. Synthesize findings into structured analysis
5. Produce actionable recommendations with confidence levels

## Core Workflow

```
Research Analyst Progress:
- [ ] Step 1: Define research question and scope
- [ ] Step 2: Establish analytical framework
- [ ] Step 3: Evidence gathering and evaluation
- [ ] Step 4: Cross-reference and validate findings
- [ ] Step 5: Synthesize analysis with confidence ratings
- [ ] Step 6: Produce recommendations
```

### Step 1: Define Research Question

- Clarify the specific question or problem to analyze
- Identify constraints: time, domain, depth
- Determine the decision this analysis will inform
- Identify key stakeholders and their information needs

### Step 2: Analytical Framework

Choose and apply one or more frameworks:

| Framework | Best For |
|-----------|----------|
| SWOT | Strategic positioning, competitive analysis |
| PESTEL | Macro-environment, policy impact |
| Porter's Five Forces | Industry/market dynamics |
| Root Cause Analysis | Problem diagnosis |
| Cost-Benefit | Investment/decision justification |
| Comparative Matrix | Technology/tool evaluation |
| Literature Synthesis | Academic/research topics |

### Step 3: Evidence Gathering

For each piece of evidence, record:

```markdown
| # | Source | Type | Quality | Relevance | Key Finding |
|---|--------|------|---------|-----------|-------------|
| 1 | [source] | [primary/secondary/tertiary] | [H/M/L] | [H/M/L] | [finding] |
```

**Quality Assessment Criteria:**
- **High**: Peer-reviewed, primary data, recent (< 2 years), reputable source
- **Medium**: Industry reports, established blogs, conference papers
- **Low**: Anecdotal, outdated (> 5 years), unverified claims

### Step 4: Cross-Reference and Validate

- Triangulate findings across multiple sources
- Identify contradictions and resolve them
- Note gaps in available evidence
- Flag assumptions that cannot be verified

### Step 5: Synthesis

Structure the analysis as:

```markdown
## Analysis Summary

### Key Findings
1. [Finding with confidence level: HIGH/MEDIUM/LOW]
2. [Finding with confidence level]

### Evidence Strength
- Strong evidence supports: [claims]
- Moderate evidence suggests: [claims]
- Weak/insufficient evidence for: [claims]

### Contradictions and Uncertainties
- [Area of disagreement and possible explanations]

### Limitations
- [Scope limitations, data gaps, methodology constraints]
```

### Step 6: Recommendations

```markdown
## Recommendations

| Priority | Recommendation | Confidence | Evidence Basis | Risk if Ignored |
|----------|---------------|------------|----------------|-----------------|
| P1 | [action] | HIGH | [refs] | [risk] |
| P2 | [action] | MEDIUM | [refs] | [risk] |
```

## Output Format

Always produce a structured document with:

1. **Executive Summary** (2-3 sentences)
2. **Research Question** (explicit statement)
3. **Methodology** (frameworks used, sources consulted)
4. **Findings** (organized by theme or hypothesis)
5. **Analysis** (synthesis with confidence levels)
6. **Recommendations** (prioritized, actionable)
7. **Appendix** (evidence table, source list)

## Integration with Other Skills

- Use `deep-research` for initial evidence collection
- Use `deep-think` for complex reasoning about ambiguous findings
- Use `tech-scout` for technology-specific evaluations
- Feed results to `brainstorm` for solution ideation

## Anti-Patterns

- Do NOT present opinions as findings
- Do NOT cherry-pick evidence to support a predetermined conclusion
- Do NOT ignore contradictory evidence
- Do NOT conflate correlation with causation
- Do NOT make recommendations without stating confidence level
