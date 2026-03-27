---
name: deep-think
description: |
  Extended reasoning and deliberation for complex, ambiguous, or high-stakes problems. Use when standard analysis is insufficient — multi-dimensional trade-offs, philosophical questions, architectural decisions with long-term consequences, or problems where the first obvious answer is likely wrong. Forces slower, more thorough thinking with explicit reasoning chains.
---

# Deep Think

Extended deliberation skill for problems that resist quick answers. Forces multi-step reasoning, considers second-order effects, and produces well-justified conclusions.

## Trigger Words

- `/deep-think`
- "think deeply about"
- "reason through this"
- "what are the second-order effects"
- "this is a hard problem"
- "deliberate on"
- "think step by step"

## When to Use

- Architectural decisions with 6+ month consequences
- Trade-offs where multiple options seem equally valid
- Problems where the obvious answer might be wrong
- Multi-stakeholder decisions with conflicting interests
- Ethical or philosophical dimensions
- Debugging subtle, hard-to-reproduce issues
- Strategy formulation under uncertainty

## Core Process

```
Deep Think Progress:
- [ ] Step 1: Problem decomposition
- [ ] Step 2: Assumption surfacing
- [ ] Step 3: Multi-perspective analysis
- [ ] Step 4: Second-order effects mapping
- [ ] Step 5: Synthesis and conclusion
- [ ] Step 6: Confidence calibration
```

### Step 1: Problem Decomposition

Break the problem into its constituent parts:

```markdown
## Problem Statement
[Restate the problem in your own words]

## Sub-Problems
1. [Component A] — [why it matters]
2. [Component B] — [why it matters]
3. [Component C] — [why it matters]

## Dependencies
- [A] depends on [B] because...
- [C] is independent of [A/B]
```

### Step 2: Assumption Surfacing

Explicitly list every assumption:

```markdown
## Assumptions (must be stated explicitly)

| # | Assumption | Type | If Wrong, Impact |
|---|-----------|------|------------------|
| 1 | [assumption] | [factual/value/scope] | [consequence] |
| 2 | [assumption] | [factual/value/scope] | [consequence] |
```

**Challenge each assumption:**
- Is this actually true, or do we just believe it?
- What evidence supports/contradicts this?
- What if the opposite were true?

### Step 3: Multi-Perspective Analysis

Analyze from at least 3 different viewpoints:

```markdown
## Perspectives

### Perspective 1: [Role/Viewpoint]
- Sees the problem as: [framing]
- Prioritizes: [values]
- Would decide: [choice]
- Reasoning: [chain]

### Perspective 2: [Role/Viewpoint]
[same structure]

### Perspective 3: Devil's Advocate
- The strongest argument against the emerging consensus is: [argument]
- Evidence supporting this counter-view: [evidence]
- This matters because: [reason]
```

### Step 4: Second-Order Effects

```markdown
## Effects Cascade

### First-Order (Direct)
- If we choose X: [immediate consequence]

### Second-Order (Indirect)
- That consequence leads to: [downstream effect]
- Which in turn causes: [further downstream]

### Third-Order (Systemic)
- Over time, the system adapts by: [emergent behavior]

### Reversibility Assessment
- Can we undo this decision? [yes/partially/no]
- Cost of reversal: [low/medium/high/impossible]
- Time window for reversal: [timeframe]
```

### Step 5: Synthesis

```markdown
## Synthesis

### What the evidence tells us
[Integrate findings from all perspectives]

### What remains uncertain
[Honest assessment of unknowns]

### Recommended path
[Clear recommendation with reasoning chain]

### Key insight
[The single most important thing learned through this analysis]
```

### Step 6: Confidence Calibration

```markdown
## Confidence Assessment

| Aspect | Confidence | Basis |
|--------|-----------|-------|
| Problem understanding | [0-100%] | [why] |
| Solution correctness | [0-100%] | [why] |
| Implementation feasibility | [0-100%] | [why] |
| Overall recommendation | [0-100%] | [why] |

### What would change my mind
- If [condition], I would reconsider [aspect]
- New information about [topic] could shift the analysis
```

## Thinking Techniques

Use these when stuck:

| Technique | When to Use | How |
|-----------|-------------|-----|
| Inversion | "What would make this fail?" | Think about the opposite |
| First Principles | Assumptions feel shaky | Strip to fundamental truths |
| Pre-mortem | Before committing | "It's 6 months later and this failed — why?" |
| Steel Man | Considering alternatives | Make the strongest case for the opposing view |
| Regret Minimization | Long-term decisions | "Which choice minimizes regret in 10 years?" |
| Fermi Estimation | Quantifying unknowns | Order-of-magnitude estimates with reasoning |

## Output Format

Always produce:

1. **Problem restatement** (in your own words)
2. **Key assumptions** (explicit, numbered)
3. **Analysis** (multi-perspective, with reasoning chains)
4. **Second-order effects** (at least 2 levels deep)
5. **Conclusion** (with confidence level and what would change your mind)

## Anti-Patterns

- Do NOT rush to a conclusion — the point is thorough deliberation
- Do NOT ignore uncomfortable evidence
- Do NOT confuse complexity with depth
- Do NOT present analysis without stating confidence levels
- Do NOT skip the assumption-surfacing step
- Do NOT use this for simple questions that have clear answers
