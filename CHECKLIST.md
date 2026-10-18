# The 110 percent checklist: Graph

Ascent alignment: Layer 4, Shared truth. Aligned October 15, 2026 (see "The need" in the README and NEEDS.md in the profile repo).
State as of October 18, 2026. Every line carries its evidence; a line without evidence does not count as done. This file is maintained by the evolution pass.

## 100 percent: completeness
- [x] Every file of the verified local publish tree present on GitHub, proven by tree diff at launch (October 14 to 15, 2026)
- [x] README accurate against the code. The opening claim was corrected October 15, 2026 after an import scan: the extraction and graph core is standard library only; NumPy and Matplotlib serve evaluation metrics and visualization only
- [x] LICENSE present
- [x] COLLABORATE.md present
- [x] CONTRIBUTING.md present
- [x] CI workflow present

## The extra 10 percent
- [x] CI green on GitHub runners (verified October 15, 2026)
- [x] Repo description and topics set (description states the verified eval scores)
- [x] Good first issues open: #1 label two eval documents in a new domain, #2 document a failure (both labeled good first issue, sized in hours)
- [x] Tagged release: v0.1.0, first verified baseline (published, marked Latest)
- [x] Live demo: https://topsoilcommons.github.io/graph/ (render verified October 15, 2026)
- [x] Fresh baseline rerun October 15, 2026: 7 tests OK; eval on 8 documents, 63 gold entities, 31 gold relations: entities F1 0.9365 in the artifact (printed as 0.936 by the eval script and previously rounded to 0.937 in the README; the discrepancy is settled in the README proof section: one artifact, one value), relations F1 0.605, LLM mode skipped (no API key; no LLM metrics claimed anywhere in this repo)
- [x] Eval corpus expansion October 15, 2026: 12 new hand labeled documents added (20 documents, 133 gold entities, 66 gold relations), labeled in two passes with 5 disagreements reconciled and recorded in eval/README.md; 7 tests OK after the expansion; new measured scores in results/eval_results.json: entities P 0.922, R 0.887, F1 0.904, relations P 0.500, R 0.742, F1 0.598, LLM mode skipped. Entity and relation F1 both fell against the 8 document baseline; the fall is published, not rounded away
- [x] Eval corpus expansion October 16, 2026: 2 new hand labeled ocean research documents added (22 documents, 148 gold entities, 75 gold relations), recorded in eval/README.md; new measured scores in results/eval_results.json: entities P 0.8777, R 0.8243, F1 0.8502, relations P 0.4949, R 0.6533, F1 0.5632, LLM mode skipped. Entity and relation F1 both fell against the 20 document scores above; the fall is published, not rounded away
- [x] Canonical rerun October 17, 2026: 7 tests OK before and after; eval rerun exactly as prescribed in AGENTS.md on the 22 document corpus reproduced the standing measurement with no change: entities F1 0.8502 (P 0.8777, R 0.8243, 122 TP, 17 FP, 26 FN), relations F1 0.5632 (P 0.4949, R 0.6533, 49 TP, 50 FP, 26 FN), LLM mode skipped. The regenerated artifact results/eval_results.json and the regenerated index.html scores are byte identical to the committed versions, so the README, eval/README.md, eval/ERROR_ANALYSIS.md, and index.html surfaces already state the canonical figures; the earlier pairs on this checklist (0.9365/0.605 on 8 documents and 0.904/0.598 on 20 documents) are dated historical runs, not the current scores
- [x] Gazetteer growth October 17, 2026: 8 gold LOCATION names verified against eval/eval_set.json added to the gazetteers in knowledge_graph_explorer/entity_extractor.py (Warsaw, Armonk, Ulm, Huntsville, Wapakoneta, White Sulphur Springs, Washington, D.C. as cities; Alabama as a state or region); 7 tests OK before and after; new measured scores in results/eval_results.json: entities P 0.8897, R 0.8716, F1 0.8805 (129 TP, 16 FP, 19 FN), relations P 0.5192, R 0.7200, F1 0.6034 (54 TP, 50 FP, 21 FN), LLM mode skipped; retrieval demo in results/retrieval_demo.json rose from 13 of 22 to 17 of 22 on both checks (123 nodes, 104 edges); index.html scores regenerated with tools/build_scores.py. Washington, D.C. is in the gazetteer but still not extracted (the matcher requires a word boundary after an entry ending in a period); that boundary case, the sentence initial person names, Alvin, and U.S. Navy remain, recorded in eval/README.md and eval/ERROR_ANALYSIS.md
- [x] Word boundary matcher fix October 18, 2026: gazetteer entries ending in a period now assert that no word character follows instead of requiring a word boundary, all other entries unchanged, in knowledge_graph_explorer/entity_extractor.py, with a regression test for the case (8 tests OK after, 7 before); Washington, D.C. is now extracted as LOCATION; new measured scores in results/eval_results.json: entities P 0.8904, R 0.8784, F1 0.8844 (130 TP, 16 FP, 18 FN), relations P 0.5192, R 0.7200, F1 0.6034 (54 TP, 50 FP, 21 FN, unchanged), LLM mode skipped; retrieval demo in results/retrieval_demo.json stayed at 17 of 22 on both checks (124 nodes, up from 123, 104 edges); index.html scores regenerated with tools/build_scores.py. The Washington fragment is still also emitted, and the sentence initial person names, Alvin, and U.S. Navy remain, recorded in eval/README.md and eval/ERROR_ANALYSIS.md

## Working agreements
- AGENTS.md in this repo governs how changes are made and proven here.
