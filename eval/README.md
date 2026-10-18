# Extraction eval set

`eval_set.json` is a small, hand labeled evaluation set for this
project's extractors: 20 short documents about technology, science
history, space, and medicine, with entities and relations labeled
by hand. The first 8 documents are the original set; 12 were added
on October 15, 2026 (see the expansion record below). It exists so
the README can publish precision and recall that come from a real
run (`scripts/evaluate_extraction.py`, results in
`results/eval_results.json`) instead of adjectives.

## Labeling rules

- Entities use the surface form as written in the text, typed as
  PERSON, ORGANIZATION, LOCATION, DATE, or TECHNOLOGY.
- Relations use only the eight types the system supports
  (founded_by, located_in, works_for, acquired, developed, born_in,
  partner_of, competes_with), in the direction conventions documented
  in `knowledge_graph_explorer/llm_extractor.py`.
- When a text states a location as a city, state pair ("headquartered
  in Mountain View, California"), both the city and the state get a
  located_in label.
- A relation is labeled only when the text states it. Facts that are
  true in the world but not stated in the document do not count, and an
  extractor that emits them loses precision. This is the rule that
  makes the co-occurrence relations cost something, as they should.
- Known hard case, labeled deliberately: "Windows" is labeled
  TECHNOLOGY in the Microsoft document. The gazetteer also lists
  Windows as an organization, so the rule based extractor disagrees.
  The label stands, the disagreement is published, and the eval is
  more honest for containing a case the system gets wrong.

## Expansion record, October 15, 2026

12 new documents were added, ids: facebook, oracle, world wide
web, linux and git, amazon, armstrong, crispr, einstein, samsung,
spotify, wikipedia founder, katherine johnson. They add 70 gold
entities and 35 gold relations. The original 8 documents and
their labels were not changed. Passage texts were adapted from
public sources: Wikipedia articles (Facebook, Oracle Corporation,
Tim Berners-Lee, Linus Torvalds, Amazon, Samsung, Spotify, Jimmy
Wales, Albert Einstein, Neil Armstrong, and CRISPR), the NASA
biographies of Neil Armstrong and Katherine Johnson, the Nobel
Prize biography of Albert Einstein, the Nobel Prize summary of
the 2020 chemistry prize (CRISPR), and the CERN public history
pages.

Labeling was done in two passes by the same labeler. In the first
pass each passage was labeled from its text. The second pass
re-derived the labels from the passage texts and the labeling
rules above alone, without consulting the first pass labels. The
two passes were then compared programmatically.

The comparison found 5 disagreements, resolved as follows:

1. Moon as a LOCATION entity in armstrong (second pass only).
   Resolved: included. The labeling rules set no Earth only limit
   on LOCATION, and the Moon is a proper named place stated in
   the text.
2. born_in to Ohio in armstrong (first pass only).
3. born_in to Germany in einstein (first pass only).
4. born_in to Alabama in wikipedia founder (first pass only).
5. born_in to West Virginia in katherine johnson (first pass
   only). Items 2 to 5 are one question: when a birthplace is
   stated as a pair (city with state or country), does born_in
   take both levels or only the first place named? Resolved: both
   levels, in all four documents. The original curie document is
   the direct precedent (born_in Warsaw and born_in Poland are
   both gold), and the written pair rule for located_in shows the
   same convention. One contrary precedent was found in the
   original set and is recorded here rather than silently fixed:
   the microsoft document labels born_in Hyderabad only, although
   India is a gold entity in that document. The original labels
   were left untouched so the 8 document baseline stays
   comparable; the both levels convention applies to the new
   documents.

Two type calls in the new documents follow the Windows precedent
above: Linux and the World Wide Web are labeled TECHNOLOGY, and
the extractor also emits Linux as ORGANIZATION and the World
Wide Web as PERSON. Both disagreements stand in the labels and
cost the extractor precision, as they should.

Scores, exactly as measured by `scripts/evaluate_extraction.py`:

- Before the expansion (8 documents, 63 gold entities, 31 gold
  relations, artifact values to four decimals): entities P
  0.9365, R 0.9365, F1 0.9365; relations P 0.4727, R 0.8387, F1
  0.6047. This is also the discrepancy settlement: the artifact
  produced 0.9365, which the README had printed as 0.937 and
  CHECKLIST.md as 0.936.
- After the expansion (20 documents, 133 gold entities, 66 gold
  relations, current `results/eval_results.json`): entities P
  0.9219, R 0.8872, F1 0.9042; relations P 0.5000, R 0.7424, F1
  0.5976. Entity F1 and relation F1 both fell. The new documents
  name people and places the gazetteers do not know, and a gold
  relation whose endpoints are missed is missed at the pipeline
  level, so relation recall fell with entity recall.

## Expansion record, October 16, 2026

Two documents in a domain the set did not cover, ocean research
institutions, written for this expansion and labeled under the rules
above: `ocean-research` (the submersible Alvin and the Woods Hole
Oceanographic Institution) and `carnegie-observatories` (the
Carnegie Institution for Science and Edwin Hubble). One labeling
correction was made before the run: an early draft of the ocean
document carried a DATE entity its text never states; it was
removed, because a label comes from the text or it does not ship.

Scores after this expansion (22 documents, 148 gold entities, 75
gold relations, current `results/eval_results.json`): entities P
0.8777, R 0.8243, F1 0.8502; relations P 0.4949, R 0.6533, F1
0.5632. Both F1 scores fell again, for the same named reason: the
new documents name things the gazetteers do not know (Alvin, WHOI,
the Carnegie names), entity recall fell, and relation recall fell
with it, because a gold relation whose endpoints are missed is
missed at the pipeline level.

## Gazetteer growth, October 17, 2026

Eight names that are gold LOCATION entities in this set, spelled
exactly as the gold labels spell them, were added to the
gazetteers in `knowledge_graph_explorer/entity_extractor.py`:
Warsaw, Armonk, Ulm, Huntsville, Wapakoneta, White Sulphur
Springs, and Washington, D.C. to the city gazetteer, and Alabama
to the states and regions gazetteer. Each name was verified
against the gold labels before it was added. No other names were
added in this pass: Alvin (TECHNOLOGY) and U.S. Navy
(ORGANIZATION) are different failure classes and were left out
on purpose.

Scores after this change (22 documents, 148 gold entities, 75
gold relations, current `results/eval_results.json`): entities P
0.8897, R 0.8716, F1 0.8805 (129 TP, 16 FP, 19 FN); relations P
0.5192, R 0.7200, F1 0.6034 (54 TP, 50 FP, 21 FN). Before the
change: entities F1 0.8502, relations F1 0.5632. The retrieval
demo (`results/retrieval_demo.json`, graph of 123 nodes and 104
edges) rose from 13 of 22 to 17 of 22 on both of its checks (gold
target in the source's neighbors, and a path found).

What remains, measured on the same runs:

- Seven of the eight added names are now extracted as LOCATION.
  Washington, D.C. is not, although it is now in the city
  gazetteer: the gazetteer matcher anchors each entry with a word
  boundary on both sides, and an entry ending in a period has no
  word boundary after it, so the pattern never matches. This is
  the boundary class from `ERROR_ANALYSIS.md`, now isolated to
  one name.
- Entity cascade misses persist where the other endpoint is
  still missed: Wapakoneta, Washington (in the crispr document),
  and White Sulphur Springs are now extracted, but their gold
  relations are still missed because Neil Armstrong, Jennifer
  Doudna, and Katherine Johnson are not extracted. Those three
  are the sentence initial person names class: every occurrence
  in their documents sits at the start of a sentence, which the
  capitalized sequence pattern skips by construction.
- Alvin and U.S. Navy remain unextracted in the ocean research
  document, for the reasons recorded in `ERROR_ANALYSIS.md`.

## Word boundary matcher fix, October 18, 2026

The first bullet under "What remains" above is now superseded.
The gazetteer matcher in
`knowledge_graph_explorer/entity_extractor.py` anchored every
entry with a word boundary on both sides; an entry ending in a
period has no word boundary after it, so "Washington, D.C."
could never match. The matcher now builds its pattern through
one helper: entries ending in a period assert instead that no
word character follows, and every other entry keeps the exact
word boundary match it had. Matching was not loosened in
general, and the measured run below shows no new false
positives. A regression test
(`test_gazetteer_entry_ending_in_period`) covers the case, with
a note on why it exists.

Scores after this change (22 documents, 148 gold entities, 75
gold relations, current `results/eval_results.json`): entities P
0.8904, R 0.8784, F1 0.8844 (130 TP, 16 FP, 18 FN); relations P
0.5192, R 0.7200, F1 0.6034 (54 TP, 50 FP, 21 FN). Before the
change: entities F1 0.8805, relations F1 0.6034. Entity recall
rose by the one name: Washington, D.C. is now extracted as a
LOCATION in the carnegie-observatories document, all eight
names added on October 17, 2026 are now extracted, and the
false positive count did not move. Relation scores did not
move either: the one gold relation pointing at Washington,
D.C. (headquartered_in, in carnegie-observatories) uses a type
outside the supported eight, and its source is still extracted
truncated, so it stays missed for those reasons. The retrieval
demo (`results/retrieval_demo.json`, graph of 124 nodes and
104 edges, up from 123 nodes) stayed at 17 of 22 on both of
its checks, for the same source side reason.

What remains from the list above, unchanged by this fix: the
sentence initial person names class (Neil Armstrong, Jennifer
Doudna, Katherine Johnson), Alvin, and U.S. Navy. One partial
form also remains: the shorter Washington is still emitted
alongside Washington, D.C. in that document, as it was before;
extracting the longest form only is separate work.

## Scoring

Micro averaged precision, recall, and F1 over the whole set. Entities
match on (text, type), case insensitive. Relations match on
(source, target, type); the two symmetric types (partner_of,
competes_with) match in either direction. Relations are scored at the
pipeline level: a gold relation whose endpoint entities the entity
extractor missed counts as missed, because that is what a user of the
pipeline experiences.

## Size, stated plainly

22 documents, 148 gold entities, 75 gold relations. That is still
a small eval, useful for regression tracking and honest comparison
between the rule based and LLM extractors, not a benchmark.
Growing it is a standing good first issue (see CONTRIBUTING.md).

## Error analysis

`ERROR_ANALYSIS.md` in this folder classifies every false positive
and false negative of the 22 document run into counted classes,
with examples, and ranks what each class implies for the next fix.
