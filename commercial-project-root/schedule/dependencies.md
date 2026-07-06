Type: dependency-graph

task_id: framing-zone3
depends_on: []
relationship_type: root

task_id: framing-signoff-zone3
depends_on: [framing-zone3]
relationship_type: requires-signoff-from

task_id: electrical-roughin-zone3
depends_on: [framing-signoff-zone3]
relationship_type: blocks
notes: Cannot open walls for electrical rough-in until framing inspection passes

task_id: plumbing-roughin-zone3
depends_on: [framing-signoff-zone3]
relationship_type: blocks

task_id: electrical-roughin-signoff-zone3
depends_on: [electrical-roughin-zone3]
relationship_type: requires-signoff-from

task_id: plumbing-roughin-signoff-zone3
depends_on: [plumbing-roughin-zone3]
relationship_type: requires-signoff-from

task_id: drywall-hanging-zone3
depends_on: [electrical-roughin-signoff-zone3, plumbing-roughin-signoff-zone3]
relationship_type: blocks
notes: Drywall cannot close walls until BOTH rough-in trades pass inspection —
       single-trade failure blocks the whole task regardless of the other trade's status

---
# Chain 2: design-input-gating failure (separate from Chain 1 above)

task_id: geotech-report-zone3
depends_on: []
relationship_type: root

task_id: structural-design-zone3
depends_on: [geotech-report-zone3]
relationship_type: requires-input-from
cost_impact: 1500
notes: FAILURE CASE — this edge existed in reality but was not enforced.
       geotech-report-zone3 was reviewed=false when structural-design-zone3
       started. Report existed 2 days prior; no gate checked reviewed status
       before design work began. Result: $1,500 rework cost, fully avoidable
       had this edge been checked mechanically instead of relying on someone
       remembering to open the file.

---
# Chain 3: date-triggered delivery vs. real task status (separate from Chains 1 and 2)

task_id: foundation-zone3
depends_on: []
relationship_type: root

task_id: beam-delivery-zone3
depends_on: [foundation-zone3]
relationship_type: blocks
cost_impact: [fill in]
notes: FAILURE CASE — beam-delivery-zone3 fired on its scheduled_date
       (2026-06-05) without checking foundation-zone3.status. Foundation
       was still in-progress. Beams sat on an unready site for ~1 week
       (storage/remobilization cost). Root cause identical in shape to
       Chain 2: a date on a calendar was trusted instead of the actual
       status of the thing it depended on. This is the general rule the
       schema is built to catch — any depends_on edge should be checked
       against live status before a date-triggered action fires, not
       assumed satisfied because the calendar said so.
