# Pauling Golden Set Status

Version: `v0.2-evidence-pass-1`

This file tracks which parts of the first Pauling ResearchMind dataset are directly evidenced, which are reconstructed from archival synthesis, and which still require primary-object inspection.

## Why this exists

ResearchMind is designed to distill research judgment, not merely summarize published conclusions. That makes process provenance critical. A published paper can establish what was claimed, but it often cannot establish exactly how a decision was reached. Therefore every Episode is kept below `high` confidence until the relevant contemporaneous process records are directly inspected.

## Episode 1 — Alpha helix (`LP-1951-ALPHA-HELIX`)

### Inspected evidence

- 1951 Pauling–Corey–Branson PNAS paper.
  - Stable locator: PNAS 37(4):205–211; DOI `10.1073/pnas.37.4.205`.
  - Directly supports the long-running program of using accurate amino-acid/peptide crystal structures to establish interatomic distances, bond angles and configurational parameters before constructing admissible polypeptide structures.
- Linus Pauling Caltech oral history.
  - Stable locator: `CaltechOH:OH_Pauling_L`, around transcript marker `Pauling-23`.
  - First-person retrospective evidence about the delay in discovering the alpha helix and the role of sustained effort.
- OSU SCARC archival reconstruction, “The Alpha Helix.”
  - Supports the March 1948 paper-folding reconstruction, the 5.4 Å model versus 5.1 Å diffraction discrepancy, and the later synthetic-polypeptide evidence that weakened the universality of the 5.1 Å constraint.

### Still required for high confidence

- Direct inspection of the surviving March 1948 alpha-helix drawing/paper reconstruction provenance and any contemporaneous notes.
- Relevant 1948–1951 correspondence with Corey, Branson, Perutz/Kendrew or other collaborators that clarifies chronology and decision ownership.

## Episode 2 — DNA triple helix (`LP-1953-DNA-TRIPLE-HELIX`)

### Inspected evidence

- 1953 Pauling–Corey PNAS paper.
  - Stable locator: PNAS 39(2):84–97; DOI `10.1073/pnas.39.2.84`; PMCID `PMC1063734`.
  - Directly supports that the structure was presented as precise but not proved: detailed intensity calculations had not yet been made.
- OSU SCARC archival reconstruction, “The Pauling-Corey Structure of DNA.”
  - Supports limited X-ray evidence, repeated core-packing difficulty, Corey's calculations showing insufficient room, and submission on 31 December 1952 despite acknowledged model tightness.
- Peter Pauling interview, Cold Spring Harbor Laboratory DNA Learning Center, item `15333`.
  - Participant retrospective evidence that Linus Pauling lacked good information on water content and diameter and later acknowledged the acid-state mistake as an error.

### Primary objects located but not directly inspected

- Linus Pauling to Watson and Crick, 27 March 1953.
  - OSU item: `sci9.001.34`.
  - Exact archive URL is registered in `source_registry.json`, but the object was not retrievable in this build session.

### Still required for high confidence

- Late-November and December 1952 research notebook pages containing the actual model-building sequence.
- Correspondence around sodium ions, phosphate packing, water content, diameter and the decision to publish.
- Direct inspection of the March 1953 correspondence after Pauling received the Watson–Crick model.

## Episode 3 — Sickle-cell anemia (`LP-1949-SICKLE-CELL`)

### Inspected evidence

- 1949 Science paper by Pauling, Itano, Singer and Wells.
  - Stable locator: Science 110(2865):543–548; DOI `10.1126/science.110.2865.543`.
  - Directly establishes the team-authored molecular-disease result and identifies sample suppliers.
- Melinda Gormley, 2003 OSU thesis based heavily on the Pauling Papers.
  - Used only as an archive map and secondary reconstruction.
  - Identifies process-level primary sources including Itano's April 1948 research report and Pauling–Burch correspondence.

### Primary object located bibliographically but not directly inspected

- Harvey A. Itano, “Research Report for Admission to Candidacy,” April 1948, p.10.
  - Archive locator: Ava Helen and Linus Pauling Papers, `I: Individual Correspondence, Harvey A. Itano`.
  - Secondary archival scholarship reports that the document proposed electrophoretic study of normal hemoglobin as the comparison basis for sickle-cell hemoglobin.

### Still required for high confidence

- Direct scan/transcript of Itano's 1948 report.
- Itano dissertation process notes.
- Pauling–Burch correspondence, especially 10–25 May 1949, concerning reliable blood-sample supply.

## Heuristic validation status

### `LP-H01-HARD-CONSTRAINT-FIRST`

Status: `provisional`

The first contrastive test is now meaningful:

- Positive case: alpha helix — strong local chemical constraints were privileged while a conflicting empirical repeat was treated as an unresolved scope question rather than automatically imposed on the model.
- Negative case: DNA triple helix — persistent core constraint violations and incomplete discriminating evidence were not allowed to overturn the preferred global topology before publication.

This is enough to strengthen the heuristic, but not enough to mark it `validated`. The remaining blocker is process-level contemporaneous evidence.

### `LP-H02-CROSS-SCALE-MECHANISM`

Status: `candidate`

The sickle-cell Episode supports the pattern of translating a visible phenotype into a lower-level discriminating measurement. It remains a candidate because it currently lacks a strong counter-episode and because the process-level Itano records have not yet been directly inspected.

## Release rule

Do not upgrade an Episode to `high` or a Heuristic to `validated` solely because multiple later historians tell the same story. At least one relevant contemporaneous process source must be directly inspected, and the model must retain plausible alternative interpretations rather than collapsing history into a single heroic narrative.
