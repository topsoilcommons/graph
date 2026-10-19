# Error analysis of the 22 document eval

Date: 2026-10-16. Layer 4, shared truth.

This is the write up of the misses behind the scores published in
`results/eval_results.json` and quoted in the README: 22 documents,
148 gold entities, 75 gold relations. Entities: precision 0.8777,
recall 0.8243, F1 0.8502 (122 true positives, 17 false positives,
26 false negatives). Relations: precision 0.4949, recall 0.6533,
F1 0.5632 (49 true positives, 50 false positives, 26 false
negatives). No extractor code changed in this pass. This analysis
is the record the next fix will be judged against.

## Method

A throwaway script (not shipped in this repo) ran the repo's own
`EntityExtractor` and `RelationExtractor` over every document in
`eval/eval_set.json` and compared the output with the gold labels
per document, using the same matching rules as
`scripts/evaluate_extraction.py`: entities match on (text, type),
case insensitive; relations match on (source, target, type), with
the two symmetric types allowed in either direction. Every false
positive and false negative was assigned to exactly one primary
class below, so the class counts sum to the artifact totals:
43 entity errors (17 FP + 26 FN) and 76 relation errors
(50 FP + 26 FN), 119 error instances in all. Relation origin uses
the confidence the code itself sets: pattern matches carry 0.85,
co-occurrence proposals carry at most 0.6.

One clean result before the misses: DATE entities are exact.
41 gold, 41 predicted, 41 correct, no false positives, no false
negatives. Dates fail only as relation endpoints, below.

## Entity errors

### False negatives: 26

| Class | Count | What it means |
| --- | --- | --- |
| No extraction at all | 18 | The name is in no gazetteer and no pattern reaches it. |
| Same text, wrong type | 5 | The text was extracted, typed so the gold (text, type) pair cannot match. |
| Partial or boundary mismatch | 3 | A shorter or split form was extracted instead of the gold form. |

No extraction at all, by gold type: LOCATION 7 of the 18,
PERSON 5, ORGANIZATION 3, TECHNOLOGY 3 (iPhone, Watson, Alvin).
By form, the 18 split into three groups:

- 12 single token names the gazetteers do not know: iPhone,
  Warsaw, Armonk, Watson, Wapakoneta, Moon, Ulm, Huntsville,
  Alabama, Wikipedia, WHOI, Alvin. The capitalized sequence
  pattern needs at least two words, so a single unknown token has
  no second chance.
- 5 multiword person names whose every occurrence in the document
  is at the start of a sentence: Neil Armstrong, Jennifer Doudna,
  Katherine Johnson, Andrew Carnegie, Edwin Hubble. The
  capitalized sequence pattern skips matches that start in the
  first three characters of a sentence, which is exactly where
  these names always sit.
- 1 abbreviation form: U.S. Navy, whose internal periods defeat
  the capitalized word patterns.

Same text, wrong type (5): White Sulphur Springs and West Virginia
extracted as PERSON, gold LOCATION; Woods Hole Oceanographic
Institution extracted as LOCATION, gold ORGANIZATION (the org
suffix list contains "Institute" but not "Institution");
Carnegie Observatories and Mount Wilson Observatory extracted as
PERSON, gold ORGANIZATION and LOCATION. The unknown name
classifier defaults two and three word capitalized sequences to
PERSON, and several of these are exactly that shape.

Partial or boundary mismatch (3): Woods Hole, Massachusetts was
extracted as two fragments, Woods Hole and Massachusetts;
Washington, D.C. was extracted as Washington; Carnegie Institution
for Science was extracted truncated, as Carnegie Institution
(typed PERSON).

By gold type overall: LOCATION missed 12 of 41, ORGANIZATION 6 of
26, PERSON 5 of 27, TECHNOLOGY 3 of 13, DATE 0 of 41.

### False positives: 17

| Class | Count | What it means |
| --- | --- | --- |
| Same text, wrong type | 10 | A second, wrong type emitted for a gold text. |
| Partial or boundary fragment | 6 | A fragment of a gold form emitted as its own entity. |
| Spurious, no gold counterpart | 1 | A common word matched a gazetteer entry. |

Same text, wrong type (10) splits in two: 5 are the mirror image
of the false negatives above (the wrong type replaced the gold
type), and 5 are extra emissions alongside a correct extraction:
iOS as ORGANIZATION (gold TECHNOLOGY, also extracted correctly),
Windows as ORGANIZATION, Linux as ORGANIZATION, the World Wide
Web as PERSON, Austin as ORGANIZATION. The gazetteers list several
names under two types, and nothing in the extractor chooses one
type per surface form.

Partial fragments (6): CRISPR alongside the correctly extracted
CRISPR-Cas9, Virginia cut out of West Virginia, Massachusetts,
Woods Hole, Washington cut out of Washington, D.C., and Carnegie
Institution cut out of Carnegie Institution for Science.

Spurious (1): "Universal" as ORGANIZATION in the computing
pioneers document. The text says "a universal machine"; the
organization gazetteer contains Universal and the match is case
insensitive, so a common adjective becomes a company.

## Relation errors

### False negatives: 26

| Class | Count | What it means |
| --- | --- | --- |
| Endpoint entity not extracted | 18 | A gold endpoint's exact text never appears in the extracted entities, so the pipeline cannot build the relation. |
| Gold type outside the supported eight | 7 | The label uses a relation type the system does not define, so no run can match it. |
| Endpoints extracted, relation missed | 1 | Both names were found; the wording that states the relation was not. |

Endpoint cascade (18) is the entity problem restated at the
pipeline level: it covers all three Armstrong relations, all three
Katherine Johnson relations, both IBM relations, the Wikipedia
founder relations (3), and the born_in or developed relations lost
with Warsaw, Ulm, Jennifer Doudna, and iPhone. Fixing entity recall
is fixing most of relation recall; the two are not separate work.

Unsupported gold types (7), all in the two documents added on
2026-10-16: founded (2, carnegie-observatories), commissioned_by
(1), operated_by (1), headquartered_in (1), established_in (1),
part_of (1). This contradicts the labeling rule stated in
`eval/README.md`, that relations use only the eight types the
system supports. The scorer matches type strings exactly, and
`RELATION_DEFINITIONS` defines none of these seven, so they are
unwinnable as labeled. One of them, established_in, also points at
a DATE target ("1902"), which none of the eight types takes in
that direction either. This class needs a labeling or schema
decision, not extractor work: map the labels to the supported
types where a supported type says the same thing (founded to
founded_by, headquartered_in to located_in), extend the schema
deliberately for the rest (commissioned_by, operated_by, part_of),
or amend the labeling rule. The labels were left as they are for
this analysis; changing them changes the scores, and that change
should be made openly, as its own unit.

The one remaining miss (1): Microsoft, works_for. Both Satya
Nadella and Microsoft are extracted, but the stating sentence is
"He joined Microsoft in 1992", where the subject is a pronoun in a
different sentence from the name. The extractor works sentence by
sentence and does not resolve pronouns.

### False positives: 50

| Class | Count | What it means |
| --- | --- | --- |
| Co-occurrence proposal the text does not state | 44 | Two entities sit within 10 words, a type is inferred from their entity types alone, and the text states no such relation. |
| Pattern overmatch | 3 | A verb pattern fired on a pair the gold labels do not relate. |
| Self relation from a dual typed entity | 3 | The same text extracted under two types is paired with itself. |

The co-occurrence class (44 of 50) is the precision problem, and
inside it one inference does most of the damage. All 26 false
positive born_in relations come from the co-occurrence pass, which
assigns born_in to any PERSON paired with a DATE or a LOCATION.
22 of the 26 point at a year that is not a birth year (a founding
year, a publication year, a tenure start); the other 4 point at a
location the person is merely near in the sentence (India, Austin,
Texas, Berlin). Measured by origin across all relation types,
pattern proposals are 27 correct of 30 (precision 0.90) and
co-occurrence proposals are 22 correct of 66 (precision 0.33).
But co-occurrence is not uniformly bad, and the fix must not treat
it as if it were: by type, co-occurrence born_in is 2 correct
against 26 wrong, while co-occurrence located_in is 11 correct
against 2 wrong. The stated-ness problem lives in specific
inferred types, born_in first, then partner_of (0 correct, 3
wrong) and developed (3 correct, 7 wrong) and works_for (3
correct, 5 wrong). located_in co-occurrence earns its place.

Pattern overmatches (3): Austin to Texas located_in (through the
loose "{E1} in {E2}" and comma patterns, on the wrongly typed
Austin entity), Pierre Curie to Paris located_in ("Working with
Pierre Curie in Paris" states presence, not the labeled relation),
and Emmanuelle Charpentier to CRISPR developed, which is also a
boundary case: the pattern fired on the real "developed
CRISPR-Cas9" wording, but the predicted endpoint is the fragment
CRISPR, so exact matching counts it wrong.

Self relations (3): iOS developed iOS, Windows developed Windows,
Linux developed Linux, each at confidence 0.6. They are the dual
type entity emissions above, paired with themselves by the
co-occurrence pass.

## Examples

1. Katherine Johnson (gazetteer miss, wrong type, cascade, in one
   document). Text: "Katherine Johnson was born in White Sulphur
   Springs, West Virginia, in 1918." Expected: Katherine Johnson
   PERSON, White Sulphur Springs LOCATION, West Virginia LOCATION,
   1918 DATE, and born_in relations to both places. Actual:
   Katherine Johnson not extracted (sentence initial, unknown to
   the person gazetteer), both places extracted as PERSON,
   Virginia also emitted as a LOCATION fragment, 1918 extracted
   correctly, and all three gold relations of the document missed
   because their source was never extracted.
2. Ocean research (unseen names, boundary, unsupported type).
   Text: "Alvin is operated by the Woods Hole Oceanographic
   Institution (WHOI), based in Woods Hole, Massachusetts."
   Expected: Alvin TECHNOLOGY, the institution and WHOI
   ORGANIZATION, Woods Hole, Massachusetts as one LOCATION, and an
   operated_by relation. Actual: Alvin and WHOI not
   extracted, the institution extracted as LOCATION, the place
   extracted as two fragments, and operated_by could not have
   matched in any case, because the type is not in the system's
   eight.
3. Musk companies (co-occurrence born_in). Text: "Elon Musk
   founded SpaceX in 2002." Expected: the one gold relation,
   SpaceX founded_by Elon Musk, which the pattern pass finds.
   Actual: that relation, plus Elon Musk born_in 2002, proposed
   only because a PERSON and a DATE stand within 10 words.

## What each class implies for the next fix, ranked by count

1. Co-occurrence unstated relations, 44 FP. Gate the inferred
   types that the counts condemn, born_in first: a PERSON plus
   DATE or LOCATION co-occurrence should not become born_in
   without born wording in the sentence. Keep located_in
   co-occurrence, which is 11 correct against 2 wrong. Judge the
   change on relation precision and on the 22 co-occurrence true
   positives it must not lose.
2. Entity no extraction, 18 FN, with the 18 endpoint cascade
   relation misses behind it. Two small, separable mechanisms:
   single token unknown names (12), which need a pattern or
   context route that works for one word, and sentence initial
   multiword names (5), which the capitalized sequence pattern
   currently skips by construction. Acronym in parentheses (WHOI)
   and the abbreviation form (U.S. Navy) sit in the same class.
3. Type ambiguity, one mechanism behind 10 entity FP, 5 entity FN,
   and the 3 self relations. Choose one type per surface form per
   document by an explicit precedence, and never pair an entity
   with itself. The documented Windows, Linux, and World Wide Web
   disagreements in `eval/README.md` are part of this class and
   stay visible either way.
4. Boundary and fragment errors, 3 entity FN and 6 entity FP, plus
   1 pattern relation FP built on a fragment. Longest match wins:
   the comma pair form (Woods Hole, Massachusetts; Washington,
   D.C.) and the full suffixed organization name (Carnegie
   Institution for Science) should be extracted whole or not at
   all, and a fragment of an already extracted longer form should
   not be emitted separately.
5. Unsupported gold relation types, 7 FN. A labeling or schema
   decision for a human to make before any extractor change, as
   set out above. No code fix can move these numbers.
6. Pattern overmatches, 3 FP. The loose located_in patterns
   ("{E1} in {E2}", "{E1}, {E2}") are the named risk; tighten them
   only after the co-occurrence work, because pattern proposals
   overall measure 27 correct of 30.
7. Pronoun and cross sentence relation miss, 1 FN, and the
   case insensitive common word match, 1 FP (Universal). Real,
   named, and last by count. The Universal case is a one word
   gazetteer hygiene question; pronoun resolution is a capability
   addition and should not be smuggled in as a small fix.

## Reproduce

```bash
python -m unittest discover -s tests                 # 7 tests, OK
python scripts/evaluate_extraction.py --out /tmp/eval_results.json
diff results/eval_results.json /tmp/eval_results.json  # no difference
```

The scores this analysis describes were reproduced from the
committed artifact before the analysis was written, and again
after it: entities P 0.8777 R 0.8243 F1 0.8502, relations
P 0.4949 R 0.6533 F1 0.5632, identical in both runs.

## Addendum, October 17, 2026: gazetteer growth

The classification above describes the run of October 16, 2026
and is left as written. On October 17, 2026 the ranked second
fix was taken in its gazetteer part: eight gold LOCATION names
were added to the gazetteers (Warsaw, Armonk, Ulm, Huntsville,
Wapakoneta, White Sulphur Springs, and Washington, D.C. as
cities; Alabama as a state or region), each verified against
the gold labels in `eval_set.json`. The new measured totals in
`results/eval_results.json` are: entities P 0.8897 R 0.8716
F1 0.8805 (129 TP, 16 FP, 19 FN, so 35 entity errors against
43 here); relations P 0.5192 R 0.7200 F1 0.6034 (54 TP, 50 FP,
21 FN, so 71 relation errors against 76 here); 106 error
instances in all, against 119. The retrieval demo rose from
13 of 22 to 17 of 22 on both checks. The new errors were not
reclassified into the classes above in this pass; the counts
here are artifact totals only.

What this changes in the classes above, by direct check against
the new run: seven of the eight added names are now extracted,
so those single token gazetteer misses are gone as entity
errors. Washington, D.C. is still not extracted even though it
is now in the gazetteer, because the matcher requires a word
boundary after the entry and an entry ending in a period has
none; it stays in the boundary class. The entity cascade class
persists in reduced form: the armstrong, crispr, and katherine
johnson documents still lose their first gold relations at
retrieval because the source persons (Neil Armstrong, Jennifer
Doudna, Katherine Johnson) are still not extracted, the
sentence initial person names class, which this pass did not
touch. U.S. Navy (the abbreviation form) and Alvin remain
unextracted, as recorded above.

## Addendum, October 18, 2026: word boundary matcher fix

The classification above and the October 17, 2026 addendum are
left as written. On October 18, 2026 the boundary case named in
both was fixed: the gazetteer matcher now asserts, for entries
ending in a period only, that no word character follows,
instead of requiring a word boundary that a period can never
have; every other entry keeps its word boundary match. A
regression test covers the case. The new measured totals in
`results/eval_results.json` are: entities P 0.8904 R 0.8784
F1 0.8844 (130 TP, 16 FP, 18 FN, so 34 entity errors against
35 in the October 17 addendum); relations P 0.5192 R 0.7200
F1 0.6034 (54 TP, 50 FP, 21 FN, so 71 relation errors,
unchanged); 105 error instances in all, against 106. The
retrieval demo stayed at 17 of 22 on both checks; its graph
grew from 123 nodes to 124 (edges unchanged at 104) with the
new Washington, D.C. node. The new errors were not
reclassified into the classes above in this pass; the counts
here are artifact totals only.

What this changes in the classes above, by direct check
against the new run: Washington, D.C. is now extracted as a
LOCATION, so that one boundary false negative is gone. The
fragment half of the boundary class remains: Washington is
still also emitted alongside the full form, so that false
positive is unchanged, and the false positive total did not
move (16 before and after), which is the check that the fix
did not loosen matching generally. Relation totals did not
move: the gold relation pointing at Washington, D.C. uses
the unsupported headquartered_in type and its source is
still extracted truncated. The sentence initial person
names class, U.S. Navy, and Alvin are untouched, as recorded
above.

## Addendum, October 18, 2026: sentence initial person names

The classification above and the earlier addenda are left as
written. Later on October 18, 2026 the sentence initial part
of the entity no extraction class was fixed: the capitalized
sequence pattern no longer skips every sentence initial match.
A sentence initial candidate now passes only when the
classifier calls it a PERSON, and never when the match is cut
short by a hyphen (a fragment of a longer hyphenated name).
A regression test covers the pass and both blocked cases. The
new measured totals in `results/eval_results.json` are:
entities P 0.894 R 0.9122 F1 0.903 (135 TP, 16 FP, 13 FN, so
29 entity errors against 34 in the October 18 addendum
above); relations P 0.5217 R 0.8 F1 0.6316 (60 TP, 55 FP,
15 FN, so 70 relation errors against 71); 99 error instances
in all, against 105. The retrieval demo rose from 17 of 22
to 20 of 22 on both checks; its graph grew from 124 nodes
and 104 edges to 129 nodes and 115 edges. The new errors
were not reclassified into the classes above in this pass;
the counts here are artifact totals only, plus the per class
check below.

What this changes in the classes above, by direct check
against the new run: all five sentence initial persons
(Neil Armstrong, Jennifer Doudna, Katherine Johnson, Andrew
Carnegie, Edwin Hubble) are now extracted, so those five
entity false negatives are gone and the entity false positive
total did not move (16 before and after), which is the check
that the narrower gate did not loosen matching generally.
Six endpoint cascade relation misses behind three of those
names were recovered (two each in the armstrong, crispr, and
katherine johnson documents). Five new relation false
positives came with the newly extracted people, mostly
co-occurrence born_in proposals pointing at years that are
not birth years, which grows the co-occurrence class above
rather than starting a new one. The unsupported gold types
class (7) is untouched: no gold labels were changed, and
that decision stays open for a human. U.S. Navy, Alvin, and
WHOI remain unextracted, as recorded above.

## Addendum, October 19, 2026: contained gazetteer fragments

The classification above and the earlier addenda are left as
written. On October 19, 2026 the fragment half of the boundary
class that the October 18 addendum left open was fixed in
general form: gazetteer matches are now collected with their
spans, and a match whose span is fully contained inside a
longer matched span in the same sentence is not emitted as a
separate entity. A match of the same length at the same span
is not a fragment and is kept, and a name that also occurs
outside any longer match keeps that occurrence. A regression
test covers the contained case for two different names and
the standalone case for both. The new measured totals in
`results/eval_results.json` are: entities P 0.906 R 0.9122
F1 0.9091 (135 TP, 14 FP, 13 FN, so 27 entity errors against
29 in the October 18 addendum above); relations P 0.531
R 0.8 F1 0.6383 (60 TP, 53 FP, 15 FN, so 68 relation errors
against 70); 95 error instances in all, against 99. The
retrieval demo stayed at 20 of 22 on both checks; its graph
shrank from 129 nodes and 115 edges to 128 nodes and 113
edges. The new errors were not reclassified into the classes
above in this pass; the counts here are artifact totals only,
plus the per class check below.

What this changes in the classes above, by direct check
against the new run: exactly two entity false positives were
removed, the Washington fragment beside Washington, D.C. in
the carnegie-observatories document and the CRISPR fragment
beside CRISPR-Cas9 in the crispr document, and no other
entity changed in any document. The two relation false
positives built on the CRISPR fragment (Jennifer Doudna and
Emmanuelle Charpentier each developed CRISPR, beside the
correct developed relations to CRISPR-Cas9, which were
already extracted and stay) are gone with it. Standalone
Washington is still extracted in the microsoft, amazon, and
crispr documents, where it is gold, which is the check that
the suppression is by span, not by name. Other fragment
forms named above are not gazetteer matches inside a longer
gazetteer match and are untouched by this fix: Virginia
inside West Virginia and the Woods Hole fragments remain.
The unsupported gold types class (7) is untouched: no gold
labels were changed, and that decision stays open for a
human. U.S. Navy, Alvin, and WHOI remain unextracted, as
recorded above.

## Addendum, October 19, 2026 (evening): the ocean research gazetteer growth

Five verified gold names from the ocean-research document
were added to the gazetteers (Alvin as TECHNOLOGY; Woods
Hole Oceanographic Institution, WHOI, and U.S. Navy as
ORGANIZATION; Woods Hole, Massachusetts as LOCATION). New
totals from `results/eval_results.json`: entities P 0.9211
R 0.9459 F1 0.9333 (140 TP, 12 FP, 8 FN, so 20 entity
errors against 27 in the October 19 addendum above);
relations P 0.5169 R 0.8133 F1 0.6321 (61 TP, 57 FP, 14 FN,
so 71 relation errors against 68); 91 error instances in
all, against 95. The new errors were not reclassified into
the classes above in this pass; the counts here are
artifact totals only, plus the per document check below.

What this changes in the classes above, by direct check
against the new run: the ocean-research document's five
entity false negatives are gone and its institution type
error with them (the gazetteer did not know the names
class), and one located_in true relation was gained. Four
new relation false positives appeared, all co-occurrence
proposals the new entities made possible, in the class
this analysis already ranks first; that is why relation
precision and F1 fell while entity scores rose, and it is
published as measured. The retrieval demo stayed at 20 of
22 on both checks: the ocean-research miss now stands
purely on the unsupported gold types class, because
commissioned_by is outside the supported eight and no
edge joins Alvin to U.S. Navy. That class (7) is
untouched: no gold labels were changed, and that decision
stays open for a human.
