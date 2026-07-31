---
name: pi-progress-synthesis
description: "Create or revise PI-, collaborator-, or lab-facing scientific progress updates, slide narratives, and research briefs that connect goals, evidence, caveats, and decisions. Use when an agent must synthesize experiments for a scientific audience, prepare a lab meeting or progress review, or turn results into a decision-focused story."
---

# PI Progress Synthesis

## Establish The Audience Question

- Identify the scientific decision, ambiguity, or reframing the audience can help with.
- Assume the audience is scientifically sophisticated but does not remember project-local jargon, run names, or benchmark contracts.
- Define the goal, data or model setup, constraints, and what would count as progress before presenting results.
- Keep the update science-facing. Omit scheduler details, agent operations, debugging chronology, and other process breadcrumbs unless operations are the subject.

## Build The Story In Causal Order

Use this sequence unless the evidence requires a different one:

1. Problem: why the project exists and which failure matters.
2. Baseline: the nearest fair reference or control.
3. Mechanism: what changed and why it might address the failure.
4. Evidence: quantitative readouts plus representative positive and negative examples.
5. Interpretation: what the evidence supports and what remains ambiguous.
6. Decision: what should continue, stop, or be tested next.

Put the motivating failure before the proposed solution. When a simpler explanation such as more data, more capacity, or longer training is plausible, name it and explain what evidence separates it from the proposed mechanism.

## Make Claims Proportional To Evidence

- Separate observation from interpretation.
- State why the selected baseline is the nearest fair comparison.
- Report denominators, split or source boundaries, and important cohort differences.
- Include negative and broken paths when they changed the decision.
- Name the strongest confound and one observation that would weaken the current interpretation.
- Do not imply that one failed extension falsifies an unchanged successful parent method.
- Prefer “suggests” or “falsifies this mechanism” over a stronger claim unless the evidence supports it.

## Put Evidence Next To The Claim

- Use a plot-rich default. Include several representative plots or image examples for every major empirical result, not a single hero example.
- Cover multiple independent participants or sources and the major scientific strata when artifacts allow. Show typical, strong, borderline, and failure cases; state the selection rule and denominator so the gallery is not mistaken for a random or exhaustive sample.
- Prefer compact small multiples or successive gallery slides when the representative set does not fit legibly on one slide. Do not drop visual evidence merely to keep the update short.
- If a result has no eligible representative plots, say why and identify the exact visualization gap rather than presenting a plot-free claim as complete.
- Typically include a detailed architecture diagram of the current system. Keep it faithful to the implementation and show the input contract, major representations and tensor shapes where useful, module boundaries, conditioning paths, objectives, outputs, and any material difference between training and inference.
- Label proposed or inactive components distinctly from the executed path, and update or replace stale diagrams rather than presenting a historical architecture as current.
- Show representative visual evidence inline when the claim is spatial, temporal, structural, or qualitative.
- Include both a current positive example and a consequential failure example when sample quality affects the decision.
- State clearly when a positive example is an upper bound, diagnostic bypass, or manually assisted result rather than the deployable path.
- Describe what each figure actually demonstrates; do not substitute the expected theoretical failure for the visible artifact.
- Put a short interpretation beside or below every result figure: what changed, what improved or worsened, and which decision it affects.
- Include artifact paths only when they help the audience inspect the evidence. Omit logs, manifests, configs, and run roots unless audit provenance was requested.

## Choose The Right Medium

- Preserve the user’s requested format. If no format is specified, use a short slide deck for visually driven updates and a concise prose brief for primarily conceptual decisions.
- Use the `quarto-presentations` skill when creating or revising a Quarto deck.
- Prefer one claim per slide, speaker notes for talk track, and plots over dense metric tables.
- Use tables only when exact mappings or comparisons are clearer than prose or a figure.
- Avoid meta headings about the intended audience or document-making process.
- Translate acronyms and project-local benchmark names into plain language before using them.

## Invite Scientific Reframing

- Describe the observed problem, constraints, evidence, and remaining ambiguity before recommending a path.
- Do not present a narrow menu of agent-generated options as though it exhausts the scientific possibilities.
- End with a small set of direct questions, decisions, or falsifiers whose answers would change the plan.

## Final Check

Before delivery, verify that the update:

- explains why the work matters before describing the method;
- connects every major claim to evidence;
- distinguishes measured results from interpretation;
- includes the nearest baseline, caveats, and negative evidence;
- makes the decision impact explicit;
- removes low-information process detail; and
- leaves the audience with one memorable status and one clear scientific question.
