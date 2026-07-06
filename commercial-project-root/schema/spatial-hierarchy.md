# Spatial Hierarchy

building: [Project Name]
├── level: L1
├── level: L2
└── level: L3
    ├── zone: Zone1
    ├── zone: Zone2
    └── zone: Zone3   ← populated for demo

Zone3 parent: L3
Zone3 adjacent: Zone2 (shared MEP riser)

## Scaling to multi-family / hotel
For projects with repeatable units (apartments, hotel rooms), the hierarchy
extends one level deeper: building > level > zone (optional, e.g. a wing) >
unit. Each unit is its own `Type: unit` file (see schema/types.md), and every
task/compliance/finishes file for that unit references its unit_id the same
way Zone3 files reference "Zone3" today — one file per unit per task, not
one file covering "all 18 units." An 18-unit building's drywall domain is 18
files, not 1, exactly like Zone3's drywall file wouldn't also cover Zone4.

Every task file's `zone` (or `unit_id`) field must resolve to a node defined
here, not a free-text string. This is what allows "everything in Zone3,"
"everything on L3," or "everything in Unit 214" queries without parsing
filenames.
