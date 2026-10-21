"""
Tests for the knowledge graph extractors and the eval harness.

Run: python -m unittest discover -s tests -v
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from knowledge_graph_explorer.entity_extractor import EntityExtractor
from knowledge_graph_explorer.relation_extractor import RelationExtractor
from knowledge_graph_explorer.llm_extractor import LLMExtractor

_spec = importlib.util.spec_from_file_location(
    "evaluate_extraction",
    Path(__file__).resolve().parents[1] / "scripts" / "evaluate_extraction.py")
evaluate_extraction = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(evaluate_extraction)


def pairs(entities):
    return {(e.text, e.entity_type) for e in entities}


class TestEntityExtractor(unittest.TestCase):
    def test_gazetteer_entities(self):
        ents = pairs(EntityExtractor().extract(
            "Ada Lovelace worked in London. Google is a company."))
        self.assertIn(("Ada Lovelace", "PERSON"), ents)
        self.assertIn(("London", "LOCATION"), ents)
        self.assertIn(("Google", "ORGANIZATION"), ents)

    def test_pre_1900_dates(self):
        # Regression: the date patterns once only matched 1900-2099, so
        # the eval set's 1867 and 1898 were invisible.
        ents = pairs(EntityExtractor().extract(
            "Marie Curie was born in 1867 and published the work in 1898."))
        self.assertIn(("1867", "DATE"), ents)
        self.assertIn(("1898", "DATE"), ents)

    def test_gazetteer_entry_ending_in_period(self):
        # Regression: an entry ending in a period (Washington, D.C.) has no word boundary after it, so the matcher never extracted it.
        ents = pairs(EntityExtractor().extract(
            "The institution is headquartered in Washington, D.C."))
        self.assertIn(("Washington, D.C.", "LOCATION"), ents)

    def test_gazetteer_fragment_inside_longer_match_not_emitted(self):
        # Regression: a shorter gazetteer match fully contained in a
        # longer matched span was emitted as its own entity beside
        # the longer form (Washington beside Washington, D.C.).
        # The contained fragment is not emitted, in general and not
        # only for that one name, while a standalone occurrence of
        # the same name elsewhere still extracts.
        contained = pairs(EntityExtractor().extract(
            "The institution is headquartered in Washington, D.C."))
        self.assertIn(("Washington, D.C.", "LOCATION"), contained)
        self.assertNotIn(("Washington", "LOCATION"), contained)

        standalone = pairs(EntityExtractor().extract(
            "Jennifer Doudna was born in Washington in 1964."))
        self.assertIn(("Washington", "LOCATION"), standalone)

        contained_tech = pairs(EntityExtractor().extract(
            "They developed CRISPR-Cas9 in 2012."))
        self.assertIn(("CRISPR-Cas9", "TECHNOLOGY"), contained_tech)
        self.assertNotIn(("CRISPR", "TECHNOLOGY"), contained_tech)

        standalone_tech = pairs(EntityExtractor().extract(
            "They used CRISPR in the laboratory."))
        self.assertIn(("CRISPR", "TECHNOLOGY"), standalone_tech)

    def test_cross_path_fragment_inside_longer_entity_not_emitted(self):
        # Regression: the contained fragment fix for gazetteer matches
        # did not reach fragments whose longer form comes from another
        # extraction path. Virginia (gazetteer) sits inside West
        # Virginia (capitalized sequence), and Woods Hole (capitalized
        # sequence) sits inside Woods Hole, Massachusetts (gazetteer).
        # Neither fragment is emitted, while a standalone occurrence
        # of each name in its own sentence still extracts.
        contained = pairs(EntityExtractor().extract(
            "Katherine Johnson was born in White Sulphur Springs, "
            "West Virginia, in 1918."))
        self.assertIn(("West Virginia", "LOCATION"), contained)
        self.assertNotIn(("Virginia", "LOCATION"), contained)

        standalone = pairs(EntityExtractor().extract(
            "She was born in Virginia in 1918."))
        self.assertIn(("Virginia", "LOCATION"), standalone)

        contained_place = pairs(EntityExtractor().extract(
            "Alvin is operated by the Woods Hole Oceanographic "
            "Institution (WHOI), based in Woods Hole, Massachusetts."))
        self.assertIn(("Woods Hole, Massachusetts", "LOCATION"),
                      contained_place)
        self.assertIn(("Woods Hole Oceanographic Institution",
                       "ORGANIZATION"), contained_place)
        self.assertNotIn(("Woods Hole", "LOCATION"), contained_place)

        standalone_place = pairs(EntityExtractor().extract(
            "The institution is based in Woods Hole."))
        self.assertIn(("Woods Hole", "LOCATION"), standalone_place)

    def test_gazetteer_state_name_carries_gazetteer_type(self):
        # Regression: West Virginia was typed PERSON. It was absent
        # from the states gazetteer (only Virginia was listed), and
        # the capitalized sequence path's gazetteer deferral check
        # omitted the states lookup, so the classifier's default for
        # a two word capitalized sequence (PERSON) won over the
        # gazetteer type. A state name matched by the gazetteer now
        # carries the gazetteer type, LOCATION, and no PERSON form
        # is emitted for it.
        ents = pairs(EntityExtractor().extract(
            "Katherine Johnson was born in White Sulphur Springs, "
            "West Virginia, in 1918."))
        self.assertIn(("West Virginia", "LOCATION"), ents)
        self.assertNotIn(("West Virginia", "PERSON"), ents)
        self.assertNotIn(("Virginia", "LOCATION"), ents)

        other_context = pairs(EntityExtractor().extract(
            "The team traveled to West Virginia for the survey."))
        self.assertIn(("West Virginia", "LOCATION"), other_context)
        self.assertNotIn(("West Virginia", "PERSON"), other_context)

    def test_ocean_research_gazetteer_names(self):
        # Regression: the ocean research gazetteer names added on
        # October 19, 2026 (evening) had no dedicated test: Alvin was
        # covered by no test, and WHOI and U.S. Navy only incidentally
        # through the cross path fragment test. Each name is verified
        # against its gold label in eval/eval_set.json (ocean-research
        # document): Alvin is TECHNOLOGY, not a person name, and the
        # punctuated U.S. Navy is ORGANIZATION.
        ents = pairs(EntityExtractor().extract(
            "The submersible Alvin has carried researchers to the deep "
            "ocean since 1964. Alvin is operated by the Woods Hole "
            "Oceanographic Institution (WHOI), based in Woods Hole, "
            "Massachusetts. The U.S. Navy commissioned Alvin and "
            "remains its owner."))
        self.assertIn(("Alvin", "TECHNOLOGY"), ents)
        self.assertNotIn(("Alvin", "PERSON"), ents)
        self.assertIn(("WHOI", "ORGANIZATION"), ents)
        self.assertIn(("U.S. Navy", "ORGANIZATION"), ents)

    def test_remaining_entity_false_negatives_gazetteer_names(self):
        # Regression: the seven entity false negatives left after the
        # October 21, 2026 re-verification were names the gazetteers
        # did not know, or knew only in a truncated or wrongly typed
        # form. Each name below is verified against its gold label in
        # eval/eval_set.json first: iPhone and Watson are TECHNOLOGY,
        # Moon and Mount Wilson Observatory are LOCATION, and
        # Wikipedia, Carnegie Institution for Science, and Carnegie
        # Observatories are ORGANIZATION. Gold text for the Moon is
        # "Moon" (the document reads "landed on the Moon").
        apple = pairs(EntityExtractor().extract(
            "Apple developed the iPhone, a smartphone that runs iOS."))
        self.assertIn(("iPhone", "TECHNOLOGY"), apple)

        ibm = pairs(EntityExtractor().extract(
            "IBM developed Watson, a question answering system, "
            "in 2011."))
        self.assertIn(("Watson", "TECHNOLOGY"), ibm)

        armstrong = pairs(EntityExtractor().extract(
            "Neil Armstrong worked for NASA and landed on the Moon "
            "in 1969."))
        self.assertIn(("Moon", "LOCATION"), armstrong)

        wikipedia = pairs(EntityExtractor().extract(
            "Jimmy Wales founded Wikipedia in 2001."))
        self.assertIn(("Wikipedia", "ORGANIZATION"), wikipedia)

        carnegie = pairs(EntityExtractor().extract(
            "The Carnegie Institution for Science is headquartered "
            "in Washington, D.C. Andrew Carnegie founded the "
            "Carnegie Institution for Science in 1902 to support "
            "basic research. Its astronomy arm, the Carnegie "
            "Observatories, grew out of the Mount Wilson "
            "Observatory, which George Ellery Hale founded."))
        self.assertIn(("Carnegie Institution for Science",
                       "ORGANIZATION"), carnegie)
        self.assertIn(("Carnegie Observatories", "ORGANIZATION"),
                      carnegie)
        self.assertIn(("Mount Wilson Observatory", "LOCATION"),
                      carnegie)
        self.assertNotIn(("Carnegie Institution", "PERSON"), carnegie)
        self.assertNotIn(("Carnegie Observatories", "PERSON"), carnegie)
        self.assertNotIn(("Mount Wilson Observatory", "PERSON"),
                         carnegie)

    def test_sentence_initial_unknown_person(self):
        # Regression: the capitalized sequence pattern once skipped
        # every match starting a sentence, so an unknown person whose
        # every occurrence is sentence initial (Neil Armstrong in the
        # eval set) was never extracted. The gate is PERSON only: a
        # sentence-initial sequence classified as another type, and a
        # fragment cut short by a hyphen, are still skipped.
        ents = pairs(EntityExtractor().extract(
            "Neil Armstrong was born in Ohio in 1930. "
            "Tim Berners-Lee was born in London in 1955. "
            "The Carnegie Institution for Science is headquartered "
            "in Washington, D.C."))
        self.assertIn(("Neil Armstrong", "PERSON"), ents)
        self.assertNotIn(("Tim Berners", "PERSON"), ents)
        self.assertNotIn(("Carnegie Institution", "LOCATION"), ents)

    def test_two_word_unknown_name(self):
        # Regression: the capitalized sequence pattern once required a
        # connector word between the first two words, so plain two word
        # names were never extracted.
        ents = pairs(EntityExtractor().extract(
            "Working with Pierre Curie in Paris, she discovered radium."))
        self.assertIn(("Pierre Curie", "PERSON"), ents)


class TestRelationExtractor(unittest.TestCase):
    def test_founded_by_pattern(self):
        text = "Steve Jobs founded Apple in 1976."
        entities = EntityExtractor().extract(text)
        rels = RelationExtractor().extract(text, entities)
        triples = {(r.source.text, r.target.text, r.relation_type) for r in rels}
        self.assertIn(("Steve Jobs", "Apple", "founded_by"), triples)


class TestLLMExtractorSkip(unittest.TestCase):
    def test_skips_gracefully_without_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            extractor = LLMExtractor()
            self.assertFalse(extractor.is_available())
            result = extractor.extract("Ada Lovelace was born in London.")
            self.assertEqual(result.status, "skipped")
            self.assertEqual(result.entities, [])
            self.assertEqual(result.relations, [])
            self.assertIn("OPENAI_API_KEY", result.reason)


class TestEvalScoring(unittest.TestCase):
    def test_prf_counts(self):
        gold = {("a",), ("b",), ("c",)}
        pred = {("a",), ("b",), ("d",)}
        scores = evaluate_extraction.prf(gold, pred)
        self.assertEqual((scores["tp"], scores["fp"], scores["fn"]), (2, 1, 1))
        self.assertAlmostEqual(scores["precision"], 2 / 3, places=4)
        self.assertAlmostEqual(scores["recall"], 2 / 3, places=4)

    def test_symmetric_relation_key(self):
        k1 = evaluate_extraction.relation_key("Beta", "Alpha", "partner_of")
        k2 = evaluate_extraction.relation_key("Alpha", "Beta", "partner_of")
        self.assertEqual(k1, k2)
        k3 = evaluate_extraction.relation_key("Beta", "Alpha", "acquired")
        k4 = evaluate_extraction.relation_key("Alpha", "Beta", "acquired")
        self.assertNotEqual(k3, k4)


if __name__ == "__main__":
    unittest.main()
