# OKF Relationship Types

Used in `schedule/dependencies.md` to link tasks across domain files.

- **blocks** — task A must complete before task B can start
- **requires-signoff-from** — task references a compliance-evidence file; task cannot close without result=passed
- **located-in** — task belongs to a spatial-hierarchy node (zone/level/building)
- **supersedes** — a revised file replaces an earlier one (e.g. re-inspection supersedes a failed signoff)
- **requires-input-from** — task cannot start until a referenced document
  exists AND carries a reviewed status with a named reviewer. Existing-but-
  unreviewed does not satisfy this edge — this is the distinction that
  catches "the report was on the drive, nobody checked it before design started"

## Query patterns this enables
- "Why is [task] blocked?" → walk `blocks` edges backward until you hit a
  task with status != complete, or a `requires-signoff-from` edge pointing
  at a compliance-evidence file with result != passed
- "What can start today?" → tasks with all `blocks` predecessors complete
  and all `requires-signoff-from` targets passed
