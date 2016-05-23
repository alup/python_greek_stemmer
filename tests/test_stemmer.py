# -*- coding: utf-8 -*
import pytest

import yaml
from greek_stemmer import GreekStemmer

def test_stem_examples():
    gs = GreekStemmer()
    words = []
    with open('tests/fixtures/examples.yml', 'r') as f:
        words = yaml.load(f.read())

    for word, st in words.iteritems():
        assert gs.stem(word) == st

def test_stem_with_non_greek_letters():
    gs = GreekStemmer()
    assert gs.stem(u"englishΟΣ") == u"englishΟΣ"
