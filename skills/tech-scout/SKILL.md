---
name: tech-scout
description: |
  Technology scouting and evaluation for tools, frameworks, libraries, and technical approaches. Use when users need to evaluate technology options, compare frameworks, assess technical feasibility, scout emerging technologies, or make build-vs-buy decisions. Produces structured comparison matrices with objective criteria scoring.
---

# Tech Scout

Technology scouting and evaluation skill. Systematically discovers, evaluates, and compares technical options to support informed technology decisions.

## Trigger Words

- `/tech-scout`
- "evaluate this technology"
- "compare these frameworks"
- "what are the options for"
- "build vs buy"
- "technology assessment"
- "find alternatives to"
- "scout technologies"

## Quick Start

1. Define the technical need and constraints
2. Discover candidate technologies
3. Establish evaluation criteria with weights
4. Evaluate each candidate against criteria
5. Produce comparison matrix and recommendation

## Core Workflow

```
Tech Scout Progress:
- [ ] Step 1: Define need and constraints
- [ ] Step 2: Candidate discovery
- [ ] Step 3: Evaluation criteria
- [ ] Step 4: Deep evaluation
- [ ] Step 5: Comparison matrix
- [ ] Step 6: Recommendation
```

### Step 1: Define Need and Constraints

```markdown
## Technical Need
- Problem to solve: [description]
- Current solution (if any): [what exists today]
- Why change is needed: [pain points]

## Constraints
| Constraint | Value | Flexibility |
|-----------|-------|-------------|
| Budget | [amount] | [hard/soft] |
| Timeline | [timeframe] | [hard/soft] |
| Team skills | [languages/frameworks] | [hard/soft] |
| Scale requirements | [users/requests/data] | [hard/soft] |
| Integration needs | [systems to integrate with] | [hard/soft] |
| Compliance/Security | [requirements] | [hard/soft] |
```

### Step 2: Candidate Discovery

Search strategy:
1. **Known options**: Technologies the team already knows about
2. **Market leaders**: Top solutions by adoption/market share
3. **Rising contenders**: Newer options gaining traction
4. **Open-source alternatives**: Community-driven options
5. **Unconventional approaches**: Different paradigms that solve the same problem

For each candidate, capture:

```markdown
| # | Technology | Category | Maturity | License | Last Release |
|---|-----------|----------|----------|---------|-------------|
| 1 | [name] | [category] | [early/growth/mature/declining] | [license] | [date] |
```

### Step 3: Evaluation Criteria

Standard criteria (customize per evaluation):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Functionality fit | 25% | Does it solve the stated problem? |
| Performance | 15% | Speed, throughput, latency |
| Developer experience | 15% | Docs, tooling, debugging, learning curve |
| Community & ecosystem | 10% | Activity, packages, support channels |
| Maintenance & longevity | 10% | Release cadence, backing, bus factor |
| Security | 10% | CVE history, security practices, audit status |
| Integration ease | 10% | APIs, SDKs, compatibility |
| Cost (TCO) | 5% | License, infrastructure, training, migration |

**Customization rules:**
- Weights must sum to 100%
- Minimum 5 criteria, maximum 10
- At least one criterion must address risk/security
- Weights should reflect the specific decision context

### Step 4: Deep Evaluation

For each candidate, evaluate:

```markdown
## [Technology Name]

### Overview
- What it is: [one sentence]
- Primary use case: [intended purpose]
- Architecture: [key design decisions]

### Strengths
1. [strength with evidence]
2. [strength with evidence]

### Weaknesses
1. [weakness with evidence]
2. [weakness with evidence]

### Scores
| Criterion | Score (1-5) | Justification |
|-----------|-------------|---------------|
| Functionality fit | [1-5] | [why] |
| Performance | [1-5] | [why] |
| ... | ... | ... |

### Risk Assessment
- Vendor lock-in risk: [low/medium/high]
- Technology obsolescence risk: [low/medium/high]
- Migration difficulty (if switching later): [low/medium/high]

### Notable
- [Any standout feature or concern not captured above]
```

### Step 5: Comparison Matrix

```markdown
## Comparison Matrix

| Criterion (Weight) | Option A | Option B | Option C |
|-------------------|----------|----------|----------|
| Functionality (25%) | 4 (1.00) | 3 (0.75) | 5 (1.25) |
| Performance (15%) | 3 (0.45) | 5 (0.75) | 4 (0.60) |
| Dev Experience (15%) | 5 (0.75) | 3 (0.45) | 3 (0.45) |
| Community (10%) | 4 (0.40) | 5 (0.50) | 2 (0.20) |
| Maintenance (10%) | 4 (0.40) | 4 (0.40) | 3 (0.30) |
| Security (10%) | 3 (0.30) | 4 (0.40) | 4 (0.40) |
| Integration (10%) | 4 (0.40) | 3 (0.30) | 3 (0.30) |
| Cost (5%) | 5 (0.25) | 2 (0.10) | 3 (0.15) |
| **Weighted Total** | **3.95** | **3.65** | **3.65** |
```

Format: `raw_score (weighted_score)` where `weighted_score = raw_score × weight`

### Step 6: Recommendation

```markdown
## Recommendation

### Primary Recommendation: [Technology]
- Weighted score: [X.XX]
- Key reasons: [top 2-3 differentiators]
- Risk mitigation: [how to address top risks]

### Runner-Up: [Technology]
- When to choose this instead: [specific conditions]

### Not Recommended: [Technology]
- Why not: [key disqualifiers]

### Implementation Considerations
- Migration path from current solution: [approach]
- Estimated adoption timeline: [timeframe]
- Key risks to monitor: [risks]
- Success metrics: [how to know it's working]
```

## Build vs Buy Decision Template

When the evaluation is specifically build-vs-buy:

```markdown
## Build vs Buy Analysis

| Factor | Build | Buy |
|--------|-------|-----|
| Upfront cost | [estimate] | [estimate] |
| Annual maintenance | [estimate] | [estimate] |
| Time to production | [estimate] | [estimate] |
| Customization | Full control | [level] |
| Competitive advantage | [yes/no - why] | N/A |
| Team capacity | [impact on team] | [minimal] |
| 3-year TCO | [total] | [total] |

### Recommendation: [Build/Buy]
[Reasoning]
```

## Integration with Other Skills

- Use `deep-research` for in-depth background on specific technologies
- Use `research-analyst` for market and ecosystem analysis
- Use `deep-think` for complex architectural trade-offs
- Feed results to `brainstorm` for implementation approaches

## Anti-Patterns

- Do NOT evaluate only one option (minimum 2 candidates)
- Do NOT use subjective scoring without justification
- Do NOT ignore total cost of ownership (focus only on license cost)
- Do NOT skip risk assessment
- Do NOT recommend based on hype or popularity alone
- Do NOT ignore the team's existing skills and constraints
