# Parent action required: reserved_usd schema contradiction

Publisher writes `reserved_usd: null` per STATE-CONTRACTS.md §비용·실패 (v2 no reservation). Fresh real schema still has `$defs.compilation.properties.cost_events.items.properties.reserved_usd = {type:number,minimum:0}`; research_review duplicates it. Happy publication now fails before any writes via candidate-state JSON Schema validation. Raw failure preserved in green-04.txt (this is a FAILED attempt, not GREEN).

Please repair the canonical schema to the existing v2 null/no-reservation contract (while retaining number allowance only if historical reservation events need compatibility), then tell this child. This child owns only publisher/test and will not edit schema or relax tests. cost unknown remains charged_usd=null; actual positive charged costs also must pass. Live AGENTS timeout remains a separate gate.
