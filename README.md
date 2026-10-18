<style>
.commons-bar{font:inherit;padding:1em 0;line-height:2}
.commons-bar a,.commons-bar span{margin-right:1rem}
.commons-bar span{font-weight:700}
.commons-footer{margin-top:3em;font:inherit;line-height:1.6}
</style>
<nav class="commons-bar" aria-label="Topsoil Commons sites">
  <a href="https://topsoilcommons.github.io/topsoilcommons/"><svg class="bar-mark" viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" focusable="false" style="flex:none;align-self:center;margin-right:7px"><g fill="currentColor"><rect x="4" y="2.5" width="16" height="2"/><rect x="4" y="5.5" width="16" height="2"/><rect x="4" y="8.5" width="16" height="2"/><rect x="4" y="11.5" width="4.5" height="8"/><rect x="15.5" y="11.5" width="4.5" height="8"/><rect x="2" y="20.5" width="20" height="2.2"/></g></svg>Topsoil Commons</a>
  <a href="https://topsoilcommons.github.io/topsoilcommons/foundations.html">Foundations</a>
  <a href="https://topsoilcommons.github.io/ground/">Ground</a>
  <a href="https://topsoilcommons.github.io/still/">Still</a>
  <a href="https://topsoilcommons.github.io/atlas/">Atlas</a>
  <a href="https://topsoilcommons.github.io/cohort/">Cohort</a>
  <span aria-current="page">Graph</span>
  <a href="https://topsoilcommons.github.io/machine/">Machine</a>
  <a href="https://topsoilcommons.github.io/lumen/">Lumen</a>
</nav>

# Graph

First step: read [the measured result and its misses](#the-proof), then run the [quick start](#quick-start) to try the tool on your own text.

Graph is a tool that shows what a text actually says, and shows its
work. You give it plain text. It finds the people, groups, places,
dates, and tools the text names, and the links between them that the
text states. It then puts those names and links in a map you can
search and check.

Measured on the current labeled set (22 documents, in results/eval_results.json): entities F1 0.903, relations F1 0.6316.

The tool is written in Python. Its main work runs with no added code
libraries. NumPy and Matplotlib are used only to score the tests and
draw pictures. We do not claim the tool is good. We test it on texts
labeled by hand, and we publish the misses next to the scores.

## The need


This project serves Layer 4: Shared truth. "Knowledge organized well enough to argue with. Claims that carry their evidence. Errors published, not buried." This repo serves that need by measuring its extraction on a hand labeled eval set and publishing the misses next to the scores.

Unmet, it looks like: decisions made about communities from scattered and invented data, arguments with no floor of agreed fact, institutions that cannot tell what they know from what they assume.

The full map: [The Ascent, a map of human needs](https://github.com/topsoilcommons/topsoilcommons/blob/main/NEEDS.md)

The research under this layer: [Foundations, Truth and shared knowledge](https://topsoilcommons.github.io/topsoilcommons/foundations.html#truth-and-shared-knowledge)

## What it is

### Hybrid extraction, honestly staged


The design is hybrid: rule based extraction always runs, offline,
with no dependencies, and an LLM mode
(`knowledge_graph_explorer/llm_extractor.py`) extracts through the
same type system for comparison on the same eval set.

**The LLM mode has not produced numbers in this environment, and
this README claims none.** With no `OPENAI_API_KEY` set, the mode
records status "skipped" in every eval artifact and returns nothing.
That behavior is itself under test
(`tests/test_extractors.py`). Set the key and rerun
`scripts/evaluate_extraction.py` and the same artifact gains an LLM
section measured the same way; until then, any LLM score for this
project would be invented, and invented numbers are the one thing
this portfolio does not publish.

### Features


- **Entity extraction**: PERSON, ORGANIZATION, LOCATION, DATE, and
  TECHNOLOGY entities via gazetteers, patterns, and heuristics
- **Relation extraction**: founded_by, located_in, works_for,
  acquired, developed, born_in, partner_of, competes_with, via verb
  patterns plus a co-occurrence pass whose cost the eval measures
- **LLM extraction mode**: optional, same schema, skips cleanly
  without a key (see above)
- **Knowledge graph**: typed nodes and edges, CRUD, JSON
  serialization, deduplication
- **Graph algorithms**: PageRank, centrality (betweenness, degree,
  closeness), community detection (Louvain), shortest path,
  connected components
- **Query engine**: a simple query language, in plain words, for following links in the graph
- **Visualization**: force-directed layout from scratch, matplotlib
  rendering
- **Built-in corpus**: 25+ paragraphs on tech companies, AI,
  computing history, and science

### Quick start


```bash
pip install -r requirements.txt
python main.py                                  # build and visualize a graph
python -m unittest discover -s tests            # extractor + eval tests
python scripts/evaluate_extraction.py           # the measured eval
```

Running `main.py` produces `knowledge_graph.json`,
`knowledge_graph.png`, `communities.png`, and
`subgraph_google.png`.

### Query examples


```python
from knowledge_graph_explorer.query_engine import QueryEngine

qe = QueryEngine(graph)
qe.execute("find all entities connected to Google")
qe.execute("path between Elon Musk and Apple")
qe.execute("entities of type PERSON connected to ORGANIZATION")
qe.execute("relations of type founded_by")
qe.execute("info about Tesla")
```

### Project structure


```
knowledge_graph_explorer/
    tokenizer.py           - Sentence/word tokenizer, POS-like tagging
    entity_extractor.py    - Rule based named entity recognition
    relation_extractor.py  - Verb pattern + co-occurrence relations
    llm_extractor.py       - Optional LLM mode (skips without a key)
    knowledge_graph.py     - Graph data structure, CRUD, serialization
    graph_algorithms.py    - PageRank, communities, paths, centrality
    query_engine.py        - Query language for graph traversal
    visualization.py       - Force-directed layout and rendering
    datasets.py            - Built-in text corpus (25+ paragraphs)
    main.py                - Pipeline: extract, build, analyze, visualize
eval/                      - Hand labeled eval set and labeling rules
scripts/evaluate_extraction.py
tests/test_extractors.py
results/eval_results.json
```


### Requirements


- Python 3.8+
- NumPy, Matplotlib (the LLM mode needs only an API key and the
  standard library)

## The proof

### Measured extraction quality


From `scripts/evaluate_extraction.py`, run 2026-10-18 against the
hand labeled set in `eval/` (22 documents, 148 gold entities, 75
gold relations; labeling rules and the expansion record in
`eval/README.md`). Full artifact: `results/eval_results.json`,
which stores the scores to four decimals (entities F1 0.903,
relations F1 0.6316); the table below rounds them to three.

| | Precision | Recall | F1 |
| --- | --- | --- | --- |
| Entities (rule based) | 0.894 | 0.912 | 0.903 |
| Relations (rule based) | 0.522 | 0.800 | 0.632 |

The 0.937 versus 0.936 discrepancy is settled. On the original
8 documents, the eval artifact `results/eval_results.json`
produced one value, 0.9365, for entity precision, recall, and F1.
This README printed 0.937, that value rounded half up to three
decimals, while CHECKLIST.md printed 0.936, the value as formatted
by the eval script. There was never a second measurement; both
files described the same artifact and now use the same rounding.
The expanded corpus supersedes that headline figure in any case:
the current figure is 0.884, measured as above.

Read those numbers the way they were earned:

- **Entity extraction is the strong half**, and the eval improved
  it. The first run scored recall 0.889; the misses exposed two
  real bugs (dates before 1900 were invisible to the year patterns;
  the capitalized-name pattern required a connector word, so plain
  two-word names like Pierre Curie never matched). Both are fixed,
  with regression tests, and both runs are on record.
- **Relation precision is the honest weakness.** Recall is high
  because the co-occurrence pass proposes a relation for almost
  every nearby entity pair, and precision pays for it: roughly half
  of the proposed relations are not stated in the text. The eval's
  labeling rule (a relation counts only if the text states it) is
  what makes that cost visible instead of hiding it.
- **The October 15, 2026 expansion lowered the scores, and that
  is published as measured.** Twelve new documents (NASA
  biographies, the Nobel Prize summary for CRISPR, and Wikipedia
  articles, adapted; record in `eval/README.md`) took the set from
  8 to 20 documents. Entity F1 fell from 0.9365 to 0.9042
  (precision 0.9365 to 0.9219, recall 0.9365 to 0.8872). Relation
  F1 fell from 0.6047 to 0.5976: precision rose from 0.4727 to
  0.5000 while recall fell from 0.8387 to 0.7424, because gold
  relations whose endpoint entities are missed cannot be found.
- **The October 16, 2026 expansion lowered them again, printed
  the same way.** Two ocean research documents took the set from
  20 to 22 documents. Entity F1 fell from 0.9042 to 0.8502
  (precision 0.9219 to 0.8777, recall 0.8872 to 0.8243). Relation
  F1 fell from 0.5976 to 0.5632 (precision 0.5000 to 0.4949,
  recall 0.7424 to 0.6533). The misses concentrate where they
  always have: names the gazetteers do not know, now including
  Alvin, WHOI, and the Carnegie institutions. The full record,
  including a labeling correction made before the run, is in
  `eval/README.md`.
- **Gazetteer growth, October 17, 2026, raised the scores, and
  that is published the same way.** Eight gold LOCATION names
  verified against `eval/eval_set.json` were added: Warsaw,
  Armonk, Ulm, Huntsville, Wapakoneta, and White Sulphur Springs
  and Washington, D.C. to the city gazetteer, and Alabama to the
  states and regions gazetteer. Entity F1 rose from 0.8502 to
  0.8805 (precision 0.8777 to 0.8897, recall 0.8243 to 0.8716;
  129 true positives, 16 false positives, 19 false negatives,
  against 122, 17, and 26 before). Relation F1 rose from 0.5632
  to 0.6034 (precision 0.4949 to 0.5192, recall 0.6533 to 0.7200).
  Seven of the eight names are now extracted; Washington, D.C.
  is in the gazetteer but still not extracted, because the
  gazetteer matcher requires a word boundary after the entry and
  a string ending in a period has none. That boundary case is
  recorded in `eval/README.md`, not hidden behind the gain.
- **Word boundary matcher fix, October 18, 2026, closed that
  boundary case.** For gazetteer entries ending in a period only,
  the matcher now asserts that no word character follows instead
  of requiring a word boundary; every other entry keeps the same
  boundary match, and a regression test covers the case.
  Washington, D.C. is now extracted as a LOCATION. Entity F1 rose
  from 0.8805 to 0.8844 (precision 0.8897 to 0.8904, recall
  0.8716 to 0.8784; 130 true positives, 16 false positives, 18
  false negatives, against 129, 16, and 19 before, so no new
  false positives). Relation F1 did not move (0.6034; precision
  0.5192, recall 0.7200): the one gold relation pointing at
  Washington, D.C. uses a type outside the supported eight and
  its source is still extracted truncated, so it stays missed
  for those named reasons, not this one. The shorter Washington
  fragment is still also emitted alongside the full form; the
  longest match question is separate work, not smuggled in here.
- **Sentence initial person names fix, October 18, 2026, closed
  the next named class.** The capitalized sequence pattern no
  longer skips every sentence initial match outright. A sentence
  initial candidate is let through only when the classifier
  calls it a PERSON, and never when the match is cut short by a
  hyphen (Tim Berners of Tim Berners-Lee is a fragment, not the
  name); every other sentence initial candidate is still
  skipped, and a regression test covers all three cases. All
  five names in the class are now extracted: Neil Armstrong,
  Jennifer Doudna, Katherine Johnson, Andrew Carnegie, and
  Edwin Hubble. Entity F1 rose from 0.8844 to 0.903 (precision
  0.8904 to 0.894, recall 0.8784 to 0.9122; 135 true positives,
  16 false positives, 13 false negatives, against 130, 16, and
  18 before, so the entity false positive count did not move).
  Relation F1 rose from 0.6034 to 0.6316 (precision 0.5192 to
  0.5217, recall 0.72 to 0.8; 60 true positives, 55 false
  positives, 15 false negatives, against 54, 50, and 21
  before): six gold relations were recovered through the five
  newly extracted people, and five new false positives came
  with them, mostly co-occurrence born_in proposals pointing
  at years that are not birth years, the known weakness below.
- **The misses are named, not rounded away.** The system misses
  entities its gazetteers do not know (Watson, iPhone), cannot
  follow pronouns across sentences ("He joined Microsoft" loses
  the works_for relation), and has documented type ambiguities
  the eval labels against it (Windows and iOS are labeled
  TECHNOLOGY; the gazetteer also lists them as organizations).
  Named misses that remain: the Moon; Wikipedia as a single
  word organization; and Alvin and U.S. Navy in the ocean
  research document. Neil Armstrong, Jennifer Doudna, and
  Katherine Johnson are no longer misses: the sentence initial
  fix above extracts them. Washington,
  D.C. is no longer a miss: the October 18, 2026 matcher fix
  above extracts it. Linux and the World Wide Web are
  also emitted with a second, wrong type. Details:
  `eval/README.md` and the eval artifact.
- **Full error analysis:** [`eval/ERROR_ANALYSIS.md`](eval/ERROR_ANALYSIS.md) classifies all 119 error instances (43 entity, 76 relation) of the October 16, 2026 run, before this gazetteer change, into counted classes and ranks what each class implies for the next fix; dated addenda there record the later totals (35 entity errors, 71 relation errors, 106 in all on October 17, 2026; 34 entity errors, 71 relation errors, 105 in all on October 18, 2026; 29 entity errors, 70 relation errors, 99 in all after the sentence initial fix later on October 18, 2026) without reclassifying them.
- **Retrieval over the merged graph, measured:** [`scripts/retrieval_demo.py`](scripts/retrieval_demo.py) builds one graph from all 22 eval documents with the repo's own pipeline (129 nodes, 115 edges) and retrieves answers from it with the QueryEngine, checked against the gold labels. On October 17, 2026, after the gazetteer change above: for one gold relation per document, the gold target appeared among the source's retrieved neighbors in 17 of 22 queries, and a path between the pair was found in 17 of 22, up from 13 of 22 on both checks before the change. The October 18, 2026 matcher fix added the Washington, D.C. node (123 nodes to 124, edges unchanged) and left both checks at 17 of 22. The sentence initial fix later on October 18, 2026 grew the graph to 129 nodes and 115 edges and raised both checks to 20 of 22. The 2 remaining misses are named per document in [`results/retrieval_demo.json`](results/retrieval_demo.json), not averaged away: ocean-research (Alvin and U.S. Navy, both still unextracted, and the gold relation type commissioned_by is outside the supported eight); and carnegie-observatories, where the source organization is extracted truncated and its gold relation type is outside the supported eight, so the now extracted Washington, D.C. target still cannot be reached from it.

### Status and limitations


- Rule based extraction is a teaching-grade instrument: strong on
  gazetteer-known entities, weak on unknown names, pronouns, and
  anything the patterns do not reach. The eval numbers above are
  the current, dated measurement of exactly that.
- The eval set is still small (22 documents, up from 8 on
  October 15, 2026). Growing it further is a standing good first
  issue; see CONTRIBUTING.md.
- The co-occurrence relation pass trades precision for recall by
  design. A confidence threshold or a stated-ness filter is the
  obvious next experiment, and the eval exists to judge it.

## Live demo

Live demo: https://topsoilcommons.github.io/graph/

## Contribute, human or agent


Pick a [good first issue](https://github.com/topsoilcommons/graph/issues) in this repo. Each one is sized in hours and written to be finishable by a newcomer.
Try the Eval Challenge against this repo's published extraction scores. Beat a baseline or document a real failure, with the run attached.
Adopt the extractor or the graph in your own work and report back what happened in real use, good or bad.

The full protocol: [The Open Table](https://github.com/topsoilcommons/topsoilcommons/blob/main/OPEN_TABLE.md). Verified work is credited in the public [Ledger](https://github.com/topsoilcommons/topsoilcommons/blob/main/LEDGER.md).

### Start with a prompt

For an AI agent:

```
You are an AI agent contributing to Graph. Run the Eval Challenge end to end.
Install with: pip install -r requirements.txt
Run the tests with: python -m unittest discover -s tests -v
Run the eval with: python scripts/evaluate_extraction.py --out /tmp/eval_results.json
Compare your run to the published baseline in The proof section above and in results/eval_results.json, measured on the hand labeled set in eval/.
Beat a baseline or document a real failure.
Attach the run to your pull request, keep one improvement per pull request, and name your operator.
```

For a human:

```
File a failure report as an issue and include the input text you ran.
Say what the extractor produced and what should have happened instead.
Attach the eval or test output if you have it.
```

<p>The layer below: <a href="https://topsoilcommons.github.io/cohort/">Cohort, belonging</a></p>
<p>The layer above: <a href="https://topsoilcommons.github.io/machine/">Machine, autonomy</a></p>
<p>The research under this layer: <a href="https://topsoilcommons.github.io/topsoilcommons/foundations.html#truth-and-shared-knowledge">Foundations, Truth and shared knowledge</a></p>
Built on Cohort: belonging.
Unlocks the ability to discern.
<footer class="commons-footer">
  <p>Topsoil Commons addresses the hierarchy of human needs through open source.</p>
  <p>Motto: Stand on the shoulders of giants.</p>
  <p>One rule: raise the floor beneath everyone.</p>
  <p>Its record is filed in <a href="https://topsoilcommons.github.io/index/">the Index</a>.</p>
  <p>Advised by Groundskeeper.</p>
  <p><a href="https://www.linkedin.com/company/topsoil-commons/">Topsoil Commons on LinkedIn</a></p>
</footer>
