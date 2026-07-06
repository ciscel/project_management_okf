Type: material-delivery
material: structural steel beams
zone: Zone3
scheduled_date: 2026-06-05
status: delivered
depends_on_task: structure/steel-erection-zone3.md (foundation must be complete)
cost_impact_if_early: [fill in — storage/crane remobilization/site congestion cost]
notes: FAILURE CASE — delivery was scheduled off the original calendar date,
  not off foundation completion status. Foundation was not complete on
  2026-06-05. Beams arrived anyway; no mechanism checked foundation status
  before triggering the delivery. Same root cause as the geotech case:
  date-triggered action fired without verifying the real status of what it
  depends on.
