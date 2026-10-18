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
