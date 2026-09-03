# Transfer Validator

Cross-domain use is allowed only after structural comparison.

## Required fields

### source_structure
Describe the original decision problem without domain decoration.

Example: "many candidate global configurations, but a small number of high-confidence local constraints."

### target_structure
Describe the user's problem at the same abstraction level.

### preserved_constraints
List what is genuinely shared.

### broken_assumptions
List what changes across domains: physical laws vs strategic behavior, controlled measurement vs observational data, deterministic constraints vs institutional adaptation, etc.

### transfer_confidence
- `high`: decision structure and key constraints are strongly analogous.
- `medium`: useful diagnostic analogy, but important assumptions differ.
- `low`: only partial resemblance; use as a question generator, not a recommendation.
- `reject`: analogy is decorative or structurally misleading.

## Social-science examples

Potentially defensible:

- instrument resolution ↔ measurement resolution / data granularity
- artifact vs signal ↔ coding change / confounding vs real behavioral response
- competing mechanisms ↔ rival causal explanations

Potentially dangerous:

- physical energy minimization ↔ firms "minimize cost" in all strategic settings
- molecular equilibrium ↔ social equilibrium without specifying actors/institutions
- deterministic structural constraints ↔ human preferences as fixed laws
