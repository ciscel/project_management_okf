# Open Knowledge Format (OKF) — Zone 3 Reference Implementation

Reference implementation accompanying the paper *"Administrative Gating as a
Decision-Centric Degree of DTC Implementation"*, which applies the
decision-centric Digital Twin Construction (DTC) methodology of Yeung and
Sacks (ISARC2026/IGLC34) to administrative, document- and status-based
construction decisions. See the paper's Section 4 ("Case Study: Zone 3
Reference Implementation") for the full argument — this repo is the artifact
that section describes.

## What this is

A construction project structure represented as plain-text markdown records
— one file per instance (one task, one person, one inspection) — validated
by a constraint checker analogous in purpose to SHACL shape validation, but
requiring no RDF/OWL tooling. Three managerial decisions (D1–D3 in the
paper) are modeled as an explicit dependency graph:

- **D1** — downstream finishing work (drywall) gated on trade rough-in and
  inspection status
- **D2** — structural design start gated on geotechnical report review status
- **D3** — material delivery gated on foundation task completion status

`commercial-project-root/` is the full domain folder tree (30+ domains).
**Zone 3 is fully populated** as the working demo; other domains are
scaffolded as structural placeholders to show how the schema scales, not as
populated data.

Names in `people/roster/` are placeholders (`[PM Name]`, etc.) — no real
individuals are represented.

## Structure

```
commercial-project-root/
  schema/           Type registry, relationship vocabulary, spatial hierarchy
                     — the controlled vocabulary for the whole instance
  schedule/
    dependencies.md  The D1–D3 dependency graph (task_id / depends_on /
                     relationship_type)
  compliance/        Inspection and trade-signoff records (Zone 3)
  design/            Geotech report + structural design task (D2 incident)
  procurement/       Material delivery record (D3 incident)
  framing/, mep/, finishes/   Trade task records feeding D1
  people/, schema/index.md    Directory + controlled-vocabulary index
  okf_validate.py    The constraint checker
```

Every content file declares a `Type:` field defined in `schema/types.md`.
One record per file is a hard rule — a roster listing four people is not
valid OKF; it's four person files. This is what makes the format
mechanically parseable without an entity-relationship parser per file.

## Running the validator

```
cd commercial-project-root
python3 okf_validate.py .
```

On the populated Zone 3 structure this checks, on every run:

1. every record satisfies its declared type's required fields (and any
   enum-constrained fields use an allowed value) — `schema/types.md`
2. every status field matches the shared status vocabulary or the
   type-specific enum
3. every `depends_on` reference in `schedule/dependencies.md` resolves to
   an existing `task_id` — no dangling references
4. the dependency graph contains no cycles
5. every `zone` reference resolves to a node declared in
   `schema/spatial-hierarchy.md`

No server, database, or network dependency. Expected output on a clean run:

```
OKF Validation Report — .
Files checked: 34 | Dependency graph nodes: 11
----------------------------------------------------------------------
✔ No errors found. All files satisfy schema/types.md; dependency graph has
  no dangling references or cycles.
----------------------------------------------------------------------
```

## Relationship vocabulary

Defined in `schema/relationships.md`:

- **blocks** — predecessor task must complete before the dependent task can start
- **requires-signoff-from** — dependent task references a compliance-evidence
  record; cannot close until that record's `result = passed`
- **requires-input-from** — dependent task cannot start until a referenced
  document exists *and* carries a `reviewed = true` status with a named
  reviewer. Existence alone does not satisfy the edge — this is the specific
  distinction the D2 incident violated (the geotechnical report existed on
  file but was never marked reviewed before design work began).

`schedule/dependencies.md` contains both the D1 chain (framing →
inspection → rough-in → inspection → drywall) and the D2 chain
(geotech report → structural design, with the $1,500 rework cost noted
inline as `cost_impact`).

## License

MIT — see `LICENSE`.
