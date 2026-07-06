# People
organizations/ — one file per company (GC, subs, AHJ), linked via parent_org
  to show the contracting chain (e.g. framing sub reports to org-gc-01).
roster/ — one file per individual, linked via employer_org to their company
  and (optionally) supervisor to their manager. This is how "who works for
  whom" — GC to subs, subs to their own employees — is queryable without a
  separate org-chart tool: walk employer_org and parent_org together.
