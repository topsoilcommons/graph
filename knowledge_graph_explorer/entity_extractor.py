"""
Named entity recognition using pattern matching, heuristics, and gazetteers.
Extracts PERSON, ORGANIZATION, LOCATION, DATE, and TECHNOLOGY entities.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from .tokenizer import tokenize_sentences, tokenize_words, pos_tag


# ── Gazetteers ──────────────────────────────────────────────────────────────

COUNTRIES = {
    "United States", "United Kingdom", "China", "Japan", "Germany", "France",
    "India", "Brazil", "Canada", "Australia", "Russia", "South Korea",
    "Italy", "Spain", "Mexico", "Indonesia", "Netherlands", "Switzerland",
    "Sweden", "Israel", "Singapore", "Ireland", "Finland", "Norway",
    "Denmark", "Taiwan", "Austria", "Belgium", "Poland", "Turkey",
    "South Africa", "New Zealand", "Argentina", "Thailand", "Egypt",
    "Saudi Arabia", "UAE", "Nigeria", "Kenya", "Colombia",
    "USA", "UK", "US",
}

CITIES = {
    "New York", "San Francisco", "London", "Tokyo", "Beijing", "Shanghai",
    "Paris", "Berlin", "Mumbai", "Bangalore", "Toronto", "Sydney",
    "Seoul", "Singapore", "Hong Kong", "Moscow", "Sao Paulo",
    "Los Angeles", "Chicago", "Seattle", "Boston", "Austin",
    "Silicon Valley", "Mountain View", "Cupertino", "Menlo Park",
    "Redmond", "Palo Alto", "San Jose", "Cambridge", "Oxford",
    "Zurich", "Geneva", "Stockholm", "Helsinki", "Dublin",
    "Tel Aviv", "Shenzhen", "Taipei", "Bangalore", "Hyderabad",
    "Detroit", "Pittsburgh", "Philadelphia", "Atlanta", "Denver",
    "Portland", "Minneapolis", "Washington", "Houston", "Dallas",
    "Miami", "Las Vegas", "Phoenix", "Nashville", "Hawthorne",
    "Heerlen", "Eindhoven", "Warsaw", "Armonk", "Ulm", "Huntsville",
    "Wapakoneta", "White Sulphur Springs", "Washington, D.C.",
    "Woods Hole, Massachusetts",
}

STATES_REGIONS = {
    "California", "Texas", "New York", "Massachusetts", "Washington",
    "Virginia", "West Virginia", "Florida", "Illinois", "Pennsylvania", "Ohio",
    "Georgia", "Colorado", "Oregon", "Bavaria", "Saxony", "Alabama",
    "Europe", "Asia", "Africa", "North America", "South America",
    "Middle East", "Southeast Asia", "East Asia", "Western Europe",
}

KNOWN_ORGANIZATIONS = {
    "Google", "Apple", "Microsoft", "Amazon", "Meta", "Facebook",
    "Tesla", "SpaceX", "Twitter", "Netflix", "Uber", "Airbnb",
    "IBM", "Intel", "AMD", "NVIDIA", "Samsung", "Sony",
    "Oracle", "Salesforce", "Adobe", "VMware", "Cisco", "Dell",
    "HP", "Hewlett-Packard", "Qualcomm", "Broadcom",
    "Alphabet", "YouTube", "Instagram", "WhatsApp", "LinkedIn",
    "OpenAI", "DeepMind", "Anthropic", "Palantir",
    "Stripe", "Square", "PayPal", "Visa", "Mastercard",
    "NASA", "CERN", "MIT", "Stanford", "Harvard", "Caltech",
    "Yale", "Princeton", "Berkeley", "Oxford University",
    "Cambridge University", "ETH Zurich",
    "Goldman Sachs", "JPMorgan", "Morgan Stanley",
    "United Nations", "World Health Organization", "WHO",
    "European Union", "NATO", "OPEC",
    "Toyota", "Volkswagen", "BMW", "Mercedes-Benz",
    "Boeing", "Airbus", "Lockheed Martin",
    "Pfizer", "Moderna", "Johnson & Johnson",
    "Walmart", "Target", "Costco",
    "Disney", "Warner Bros", "Universal",
    "Spotify", "TikTok", "Snapchat", "Pinterest", "Reddit",
    "GitHub", "Stack Overflow", "Mozilla",
    "Red Hat", "Canonical", "Docker", "Kubernetes",
    "Android", "iOS", "Windows", "Linux",
    "the European Union", "the United Nations",
    "Bell Labs", "Xerox PARC", "DARPA",
    "Woods Hole Oceanographic Institution", "WHOI", "U.S. Navy",
    "World Wide Web Consortium", "W3C",
    "Association for Computing Machinery", "ACM",
    "IEEE", "Royal Society",
}

KNOWN_PERSONS = {
    "Elon Musk", "Jeff Bezos", "Bill Gates", "Steve Jobs", "Tim Cook",
    "Mark Zuckerberg", "Sundar Pichai", "Satya Nadella", "Larry Page",
    "Sergey Brin", "Jack Dorsey", "Reed Hastings", "Travis Kalanick",
    "Brian Chesky", "Jensen Huang", "Lisa Su", "Pat Gelsinger",
    "Sam Altman", "Demis Hassabis", "Dario Amodei",
    "Andy Jassy", "Sheryl Sandberg", "Susan Wojcicki",
    "Marissa Mayer", "Meg Whitman", "Ginni Rometty",
    "Bob Iger", "Tim Berners-Lee", "Linus Torvalds",
    "Vint Cerf", "Dennis Ritchie", "Ken Thompson",
    "Alan Turing", "Ada Lovelace", "John von Neumann",
    "Claude Shannon", "Grace Hopper", "Margaret Hamilton",
    "Guido van Rossum", "James Gosling", "Bjarne Stroustrup",
    "Larry Ellison", "Marc Benioff", "Michael Dell",
    "Steve Wozniak", "Paul Allen", "Gordon Moore", "Robert Noyce",
    "Albert Einstein", "Marie Curie", "Isaac Newton",
    "Nikola Tesla", "Thomas Edison", "Alexander Graham Bell",
    "Charles Babbage", "John McCarthy", "Marvin Minsky",
    "Geoffrey Hinton", "Yann LeCun", "Yoshua Bengio",
    "Andrew Ng", "Fei-Fei Li", "Ian Goodfellow",
    "Peter Thiel", "Reid Hoffman", "Max Levchin",
    "Larry Wall", "Brendan Eich", "Rasmus Lerdorf",
    "Jimmy Wales", "Pierre Omidyar", "Jerry Yang",
    "David Filo", "Evan Spiegel", "Kevin Systrom",
    "Jan Koum", "Drew Houston", "Daniel Ek",
    "Jack Ma", "Pony Ma", "Robin Li",
    "Travis Kalanick", "Garrett Camp",
    "Whitney Wolfe Herd", "Reshma Saujani",
    "Stewart Butterfield", "Cal Henderson",
}

TECHNOLOGIES = {
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby",
    "Go", "Rust", "Swift", "Kotlin", "Scala", "PHP", "Perl",
    "HTML", "CSS", "SQL", "NoSQL", "GraphQL", "REST",
    "TensorFlow", "PyTorch", "Keras", "scikit-learn",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Git", "GitHub", "Linux", "Unix", "Windows", "macOS",
    "TCP/IP", "HTTP", "HTTPS", "DNS", "SSL", "TLS",
    "blockchain", "Bitcoin", "Ethereum", "cryptocurrency",
    "machine learning", "deep learning", "neural network",
    "artificial intelligence", "natural language processing",
    "computer vision", "reinforcement learning",
    "cloud computing", "edge computing", "quantum computing",
    "Internet of Things", "IoT", "5G", "WiFi", "Bluetooth",
    "GPS", "LiDAR", "CRISPR", "mRNA",
    "virtual reality", "augmented reality", "mixed reality",
    "self-driving", "autonomous vehicles", "electric vehicles",
    "semiconductor", "microprocessor", "GPU", "CPU", "TPU",
    "transistor", "integrated circuit", "VLSI",
    "ARPANET", "Internet", "World Wide Web", "WWW",
    "PageRank", "MapReduce", "Hadoop", "Spark",
    "Android", "iOS", "Chrome", "Firefox", "Safari",
    "ChatGPT", "GPT-4", "DALL-E", "Midjourney",
    "large language model", "transformer", "attention mechanism",
    "generative AI", "diffusion model",
    "API", "SDK", "IDE", "CI/CD",
    "relational database", "MongoDB", "PostgreSQL", "MySQL",
    "Redis", "Elasticsearch", "Kafka",
    "microservices", "serverless", "containerization",
    "DevOps", "agile", "Scrum",
    "CRISPR-Cas9", "Alvin",
}

# Context words that hint at entity types
PERSON_CONTEXT = {
    "ceo", "founder", "co-founder", "president", "chairman", "director",
    "engineer", "scientist", "researcher", "professor", "inventor",
    "entrepreneur", "executive", "officer", "manager", "leader",
    "pioneer", "visionary", "philanthropist", "billionaire",
    "mr", "mrs", "ms", "dr", "prof",
}

ORG_CONTEXT = {
    "company", "corporation", "inc", "ltd", "llc", "corp", "startup",
    "firm", "enterprise", "institute", "university", "college",
    "foundation", "organization", "agency", "laboratory", "lab",
    "group", "consortium", "association", "society",
}

LOCATION_CONTEXT = {
    "city", "country", "state", "region", "area", "district",
    "valley", "coast", "bay", "island", "continent",
    "headquartered", "based", "located", "offices",
}

ORG_SUFFIXES = {
    "Inc", "Inc.", "Ltd", "Ltd.", "LLC", "Corp", "Corp.",
    "Corporation", "Company", "Co", "Co.", "Group", "Holdings",
    "Technologies", "Labs", "Laboratories", "Systems", "Solutions",
    "Networks", "Dynamics", "Industries", "Ventures", "Partners",
    "Foundation", "Institute", "University", "Association",
}


class Entity:
    """Represents an extracted entity."""

    def __init__(self, text: str, entity_type: str, confidence: float = 1.0,
                 source_sentence: str = "", span=None):
        self.text = text
        self.entity_type = entity_type  # PERSON, ORGANIZATION, LOCATION, DATE, TECHNOLOGY
        self.confidence = confidence
        self.source_sentence = source_sentence
        self.span = span  # (start, end) in source_sentence, when known
        self.mentions = 1

    def __repr__(self):
        return f"Entity({self.text!r}, {self.entity_type}, conf={self.confidence:.2f})"

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.text == other.text and self.entity_type == other.entity_type
        return False

    def __hash__(self):
        return hash((self.text, self.entity_type))


def _gazetteer_pattern(name: str) -> str:
    """Build the word-boundary pattern for one gazetteer entry.

    An entry ending in a period has no word boundary after it (a
    period and the space or end of text that follows are both
    non-word characters, and \\b needs a word/non-word transition),
    so the trailing \\b can never match. For those entries only,
    assert instead that no word character follows.
    """
    if name.endswith("."):
        return r'\b' + re.escape(name) + r'(?!\w)'
    return r'\b' + re.escape(name) + r'\b'


class EntityExtractor:
    """Extract named entities from text using patterns and gazetteers."""

    def __init__(self):
        self.entities: List[Entity] = []
        self._build_lookup_sets()

    def _build_lookup_sets(self):
        """Pre-compute lowercase lookup sets for faster matching."""
        self._countries_lower = {c.lower(): c for c in COUNTRIES}
        self._cities_lower = {c.lower(): c for c in CITIES}
        self._states_lower = {s.lower(): s for s in STATES_REGIONS}
        self._orgs_lower = {o.lower(): o for o in KNOWN_ORGANIZATIONS}
        self._persons_lower = {p.lower(): p for p in KNOWN_PERSONS}
        self._tech_lower = {t.lower(): t for t in TECHNOLOGIES}

    def extract(self, text: str) -> List[Entity]:
        """Extract all entities from text."""
        entities = []
        sentences = tokenize_sentences(text)

        for sentence in sentences:
            sent_entities = []

            # Gazetteer-based extraction (highest priority)
            sent_entities.extend(self._extract_from_gazetteers(sentence))

            # Pattern-based extraction
            sent_entities.extend(self._extract_dates(sentence))
            sent_entities.extend(self._extract_by_context(sentence))
            sent_entities.extend(self._extract_capitalized_sequences(sentence))

            # Cross-path contained fragments: an entity whose span is
            # fully contained inside a longer entity's span in the same
            # sentence is a fragment of that longer entity, not a
            # separate entity, whichever extraction path produced each
            # one (Virginia, from the gazetteer, inside West Virginia,
            # from the capitalized sequence pattern; Woods Hole, from
            # the capitalized sequence pattern, inside the gazetteer
            # match Woods Hole, Massachusetts). A match of the same
            # length at the same span is not a fragment and is kept,
            # and a name that also occurs outside any longer match
            # keeps that occurrence. Entities without a known span
            # are never dropped and never cause a drop.
            sent_entities = [
                ent for i, ent in enumerate(sent_entities)
                if not (ent.span is not None and any(
                    j != i and other.span is not None
                    and other.span[0] <= ent.span[0]
                    and ent.span[1] <= other.span[1]
                    and (other.span[1] - other.span[0])
                    > (ent.span[1] - ent.span[0])
                    for j, other in enumerate(sent_entities)))
            ]

            # Deduplicate within sentence, keeping highest confidence
            seen = {}
            for ent in sent_entities:
                key = (ent.text, ent.entity_type)
                if key not in seen or ent.confidence > seen[key].confidence:
                    ent.source_sentence = sentence
                    seen[key] = ent

            entities.extend(seen.values())

        # Global deduplication
        self.entities = self._deduplicate(entities)
        return self.entities

    def _extract_from_gazetteers(self, sentence: str) -> List[Entity]:
        """Match known entities from gazetteers.

        Matches are collected with their spans first. A match whose
        span is fully contained inside a longer matched span in the
        same sentence is a fragment of that longer match, not a
        separate entity (Washington inside Washington, D.C., CRISPR
        inside CRISPR-Cas9), so it is not emitted. A match of the
        same length at the same span (one name listed under two
        types, or as both a city and a state) is not a fragment and
        is kept, and a name that also occurs outside any longer
        match keeps that occurrence.
        """
        # (lookup, entity type, confidence), persons first as before
        gazetteers = [
            (self._persons_lower, "PERSON", 0.95),
            (self._orgs_lower, "ORGANIZATION", 0.95),
            (self._countries_lower, "LOCATION", 0.95),
            (self._cities_lower, "LOCATION", 0.90),
            (self._states_lower, "LOCATION", 0.85),
            (self._tech_lower, "TECHNOLOGY", 0.90),
        ]
        sent_lower = sentence.lower()
        matches = []  # (start, end, entity)
        for lookup, entity_type, confidence in gazetteers:
            for name_lower, name in lookup.items():
                if name_lower not in sent_lower:
                    continue
                pattern = _gazetteer_pattern(name)
                for match in re.finditer(pattern, sentence, re.IGNORECASE):
                    matches.append((match.start(), match.end(),
                                    Entity(name, entity_type,
                                           confidence=confidence,
                                           span=(match.start(),
                                                 match.end()))))

        entities = []
        for i, (start, end, entity) in enumerate(matches):
            contained = any(
                j != i and o_start <= start and end <= o_end
                and (o_end - o_start) > (end - start)
                for j, (o_start, o_end, _other) in enumerate(matches))
            if not contained:
                entities.append(entity)
        return entities

    def _extract_dates(self, sentence: str) -> List[Entity]:
        """Extract date entities using regex patterns."""
        entities = []

        # Year patterns: 1900-2099
        for match in re.finditer(r'\b((?:18|19|20)\d{2})\b', sentence):
            entities.append(Entity(match.group(1), "DATE", confidence=0.85,
                                   span=match.span(1)))

        # Month Year: "January 2020", "Jan 2020"
        month_pattern = (
            r'\b((?:January|February|March|April|May|June|July|August|'
            r'September|October|November|December|'
            r'Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?'
            r'\s+\d{4})\b'
        )
        for match in re.finditer(month_pattern, sentence):
            entities.append(Entity(match.group(1), "DATE", confidence=0.90,
                                   span=match.span(1)))

        # Decade patterns: "1990s", "2000s"
        for match in re.finditer(r'\b((?:18|19|20)\d{2}s)\b', sentence):
            entities.append(Entity(match.group(1), "DATE", confidence=0.85,
                                   span=match.span(1)))

        # "early/mid/late 2000s" style
        for match in re.finditer(
            r'\b((?:early|mid|late)\s+(?:18|19|20)\d{2}s?)\b', sentence, re.IGNORECASE
        ):
            entities.append(Entity(match.group(1), "DATE", confidence=0.80,
                                   span=match.span(1)))

        return entities

    def _extract_by_context(self, sentence: str) -> List[Entity]:
        """Extract entities based on context words."""
        entities = []
        tokens = tokenize_words(sentence)
        tagged = pos_tag(tokens)

        for i, (token, tag) in enumerate(tagged):
            lower = token.lower()

            # Person context: "CEO X Y", "founder X Y"
            if lower in PERSON_CONTEXT:
                # Look ahead for proper nouns
                name_parts = []
                for j in range(i + 1, min(i + 5, len(tagged))):
                    if tagged[j][1] == "PROPN":
                        name_parts.append(tagged[j][0])
                    elif name_parts:
                        break
                if name_parts:
                    name = " ".join(name_parts)
                    if not self._is_known_non_person(name):
                        start = sentence.find(name)
                        span = (start, start + len(name)) if start >= 0 else None
                        entities.append(Entity(name, "PERSON", confidence=0.75,
                                               span=span))

            # Org context: "company X", "startup X"
            elif lower in ORG_CONTEXT:
                name_parts = []
                for j in range(i + 1, min(i + 5, len(tagged))):
                    if tagged[j][1] == "PROPN":
                        name_parts.append(tagged[j][0])
                    elif name_parts:
                        break
                if name_parts:
                    name = " ".join(name_parts)
                    start = sentence.find(name)
                    span = (start, start + len(name)) if start >= 0 else None
                    entities.append(Entity(name, "ORGANIZATION", confidence=0.70,
                                           span=span))

        return entities

    def _extract_capitalized_sequences(self, sentence: str) -> List[Entity]:
        """Extract sequences of capitalized words as potential entities."""
        entities = []

        # Find sequences of capitalized words (potential proper nouns)
        pattern = r'\b([A-Z][a-z]+(?:\s+(?:of|the|and|for|de|van|von|al|el|la|le)\s+|\s+)[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for match in re.finditer(pattern, sentence):
            candidate = match.group(1).strip()
            span_start, span_end = match.span(1)
            if candidate.startswith("The "):
                candidate = candidate[4:]
                span_start += 4
            span = (span_start, span_start + len(candidate))

            # Skip if already matched by gazetteers. The gazetteer
            # type wins over the classifier below for every
            # gazetteer class, states and regions included: a state
            # name in STATES_REGIONS (West Virginia) was previously
            # re-emitted here with the classifier's PERSON default
            # because this check omitted the states lookup.
            candidate_lower = candidate.lower()
            if (candidate_lower in self._persons_lower or
                candidate_lower in self._orgs_lower or
                candidate_lower in self._countries_lower or
                candidate_lower in self._cities_lower or
                candidate_lower in self._states_lower):
                continue

            # Classify the entity
            entity_type = self._classify_unknown_entity(candidate, sentence)
            if not entity_type:
                continue

            # Sentence-initial matches get a narrower gate, not a
            # blanket skip. Capitalization at the start of a sentence
            # is weak evidence on its own (any two common words are
            # capitalized there), so only a candidate the classifier
            # calls a PERSON is let through, and never when the match
            # is cut short by a hyphen: that is a fragment of a longer
            # hyphenated name (Tim Berners of Tim Berners-Lee), not
            # the name itself.
            if match.start() < 3:
                if entity_type != "PERSON":
                    continue
                if sentence[match.end():match.end() + 1] == "-":
                    continue

            entities.append(Entity(candidate, entity_type, confidence=0.60,
                                   span=span))

        return entities

    def _classify_unknown_entity(self, text: str, context: str) -> Optional[str]:
        """Classify an unknown capitalized sequence based on context clues."""
        context_lower = context.lower()
        text_lower = text.lower()
        words = text.split()

        # Check for org suffixes
        if any(w in ORG_SUFFIXES for w in words):
            return "ORGANIZATION"

        # Check context for clues
        # Look for the entity in context with surrounding words
        idx = context_lower.find(text_lower)
        if idx >= 0:
            # Get surrounding context (50 chars each side)
            start = max(0, idx - 50)
            end = min(len(context_lower), idx + len(text) + 50)
            local_context = context_lower[start:end]

            if any(w in local_context for w in LOCATION_CONTEXT):
                return "LOCATION"
            if any(w in local_context for w in ORG_CONTEXT):
                return "ORGANIZATION"
            if any(w in local_context for w in PERSON_CONTEXT):
                return "PERSON"

        # Heuristic: 2-3 words, all capitalized -> likely a person name
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words):
            # Check if any word is a common location word
            location_words = {"city", "river", "lake", "mountain", "bay", "island", "valley"}
            if any(w.lower() in location_words for w in words):
                return "LOCATION"
            return "PERSON"

        return None

    def _is_known_non_person(self, name: str) -> bool:
        """Check if a name is a known non-person entity."""
        lower = name.lower()
        return (lower in self._orgs_lower or
                lower in self._countries_lower or
                lower in self._cities_lower or
                lower in self._tech_lower)

    def _deduplicate(self, entities: List[Entity]) -> List[Entity]:
        """Merge duplicate entities, keeping highest confidence."""
        merged: Dict[Tuple[str, str], Entity] = {}

        for ent in entities:
            key = (ent.text, ent.entity_type)
            if key in merged:
                merged[key].mentions += 1
                if ent.confidence > merged[key].confidence:
                    merged[key].confidence = ent.confidence
            else:
                merged[key] = ent

        return list(merged.values())

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]

    def get_entity_summary(self) -> Dict[str, int]:
        """Get counts of entities by type."""
        summary = {}
        for ent in self.entities:
            summary[ent.entity_type] = summary.get(ent.entity_type, 0) + 1
        return summary
