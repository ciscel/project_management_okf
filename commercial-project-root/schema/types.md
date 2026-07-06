# OKF Type Registry

Every content file declares a `Type:` field. This registry defines required
and optional fields per type. Unlisted types are not yet ratified — do not
invent new Type values without adding them here first.

## File convention: one record per file
Every file represents exactly one instance of a Type — one task, one person,
one organization, one unit, one milestone. This is non-negotiable and holds
regardless of project scale: a single-family renovation and a 300-unit hotel
tower use the same rule, just with more files. Multi-record files (a roster
listing four crews, a directory listing four contacts) are not valid OKF —
split them. This is what makes the format mechanically parseable/validatable
without an entity-relationship parser per file, and what makes it scale
cleanly from "zone3" to "unit 214" to "employee of subcontractor of GC"
without changing the rule.

## organization
Required: org_id, org_type (gc|general-contractor|contractor|subcontractor|owner|design-firm|ahj), name
Optional: parent_org (org_id of the org this reports to/is contracted under), trade, contact_method

## person
Required: person_id, name, role, employer_org (org_id)
Optional: cert_status, trade, supervisor (person_id)

## framing-installation
Required: zone, trade, start_date, end_date, status, percent_complete
Optional: crew_ref, notes

## mep-roughin
Required: zone, subtrade (electrical|plumbing|hvac|fire-protection), start_date, end_date, status, percent_complete
Optional: crew_ref, permit_ref

## compliance-evidence
Required: zone, trade, inspection_date, inspector, result (pending|passed|failed|reinspection-required)
Optional: reinspection_date, notes, photo_ref

## drywall-installation
Required: zone, start_date, end_date, status, percent_complete
Optional: crew_ref, blocked_by (see relationships.md)

## master-schedule
Required: milestone_name, target_date, status

## lookahead-schedule
Required: window_start, window_end, tasks (list of task refs)

## site-investigation-report
Required: zone, report_type, date_completed, reviewed (true|false), reviewed_by
Optional: notes, findings_summary

## design-task
Required: zone, discipline, start_date, status (not-started|in-progress|rework-required|blocked|complete)
Optional: cost_impact_if_rework (dollars), rework_reason

## material-delivery
Required: material, zone, scheduled_date, status (scheduled|delivered|held)
Optional: depends_on_task, cost_impact_if_early (storage/remobilization dollars), notes

## dependency-graph
Required: task_id, depends_on (list of task_ids), relationship_type
Optional: notes, cost_impact

## unit
Required: unit_id, zone (or building/level if no zone tier), unit_type (room|apartment-unit|suite)
Optional: floor_plan_ref, notes

## Status values (shared vocabulary across types)
not-started | in-progress | blocked | complete
