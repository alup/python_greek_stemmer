# -*- coding: utf-8-*-
from __future__ import unicode_literals
from builtins import object
import re
import os
import yaml


class GreekStemmer(object):

    # Regular expression that checks if the word contains only Greek characters
    # ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ
    ALPHABET = u"^[\u0391-\u03a9\u03b1-\u03c9]+$"

    WITH_ACCENT = {
            u'\u03ac': u'\u03b1',
            u'\u03ad': u'\u03b5',
            u'\u03cc': u'\u03bf'
    }

    # ΑΕΗΙΟΥΩ
    VOWELS = u'[\u0391\u0395\u0397\u0399\u039f\u03a5\u03a9]$'

    # ΑΕΗΙΟΩ
    VOWELS_WITHOUT_Y = u'[\u0391\u0395\u0397\u0399\u039f\u03a9]$'

    def __init__(self):
        self.alphabet_regex = re.compile(GreekStemmer.ALPHABET,
                                         flags=re.U | re.I)
        self.vowels_regex = re.compile(GreekStemmer.VOWELS,
                                       flags=re.U | re.I)
        self.vowels_without_y_regex = re.compile(GreekStemmer.VOWELS_WITHOUT_Y,
                                                 flags=re.U | re.I)

        custom_rules = self.load_settings()

        self.step_1_exceptions = custom_rules['step_1_exceptions']
        self.protected_words = custom_rules['protected_words']

        self.step_1_regexp = re.compile(
                u"(.*)({})$".format("|".join(
                    list(self.step_1_exceptions.keys()))))

    def stem(self, word):
        if len(word) < 3:
            return word

        if not self.is_greek(word):
            return word

        if word in self.protected_words:
            return word

        word_length = len(word)
        stem = word

        # step 1
        m = self.step_1_regexp.search(word)
        if m:
            st, suffix = m.groups()
            stem = st + self.step_1_exceptions[suffix]

        # step 2a
        m = re.search(u'^(.+?)(ΑΔΕΣ|ΑΔΩΝ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if not re.search(
                    u'(ΟΚ|ΜΑΜ|ΜΑΝ|ΜΠΑΜΠ|ΠΑΤΕΡ|ΓΙΑΓΙ|ΝΤΑΝΤ|ΚΥΡ|ΘΕΙ|ΠΕΘΕΡ|'
                    'ΜΟΥΣΑΜ|ΚΑΠΛΑΜ|ΠΑΡ|ΨΑΡ|ΤΖΟΥΡ|ΤΑΜΠΟΥΡ)$', st):
                stem += u'ΑΔ'

        # step 2b
        m = re.search(u'^(.+?)(ΕΔΕΣ|ΕΔΩΝ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'(ΟΠ|ΙΠ|ΕΜΠ|ΥΠ|ΓΗΠ|ΔΑΠ|ΚΡΑΣΠ|ΜΙΛ)$', st):
                stem += u'ΕΔ'

        # step 2c
        m = re.search(u'^(.+?)(ΟΥΔΕΣ|ΟΥΔΩΝ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'(ΑΡΚ|ΚΑΛΙΑΚ|ΠΕΤΑΛ|ΛΙΧ|ΠΛΕΞ|ΣΚ|Σ|ΦΛ|ΦΡ|ΒΕΛ|'
                         'ΛΟΥΛ|ΧΝ|ΣΠ|ΤΡΑΓ|ΦΕ)$', st):
                stem += u'ΟΥΔ'

        # step 2d
        m = re.search(u'^(.+?)(ΕΩΣ|ΕΩΝ|ΕΑΣ|ΕΑ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(Θ|Δ|ΕΛ|ΓΑΛ|Ν|Π|ΙΔ|ΠΑΡ|ΣΤΕΡ|ΟΡΦ|ΑΝΔΡ|ΑΝΤΡ)$', st):
                stem += u'Ε'

        # step 3
        m = re.search(u'^(.+?)(ΙΟΥΣ|ΙΑΣ|ΙΕΣ|ΙΟΣ|ΙΟΥ|ΙΟΙ|ΙΩΝ|ΙΟΝ|ΙΑ|ΙΟ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if self.ends_on_vowel(st) or len(st) < 2 or re.search(
                    u'^(ΑΓ|ΑΓΓΕΛ|ΑΓΡ|ΑΕΡ|ΑΘΛ|ΑΚΟΥΣ|ΑΞ|ΑΣ|Β|ΒΙΒΛ|ΒΥΤ|Γ|ΓΙΑΓ|'
                    'ΓΩΝ|Δ|ΔΑΝ|ΔΗΛ|ΔΗΜ|ΔΟΚΙΜ|ΕΛ|ΖΑΧΑΡ|ΗΛ|ΗΠ|ΙΔ|ΙΣΚ|ΙΣΤ|ΙΟΝ|'
                    'ΙΩΝ|ΚΙΜΩΛ|ΚΟΛΟΝ|ΚΟΡ|ΚΤΗΡ|ΚΥΡ|ΛΑΓ|ΛΟΓ|ΜΑΓ|ΜΠΑΝ|ΜΠΡ|ΝΑΥΤ|'
                    'ΝΟΤ|ΟΠΑΛ|ΟΞ|ΟΡ|ΟΣ|ΠΑΝΑΓ|ΠΑΤΡ|ΠΗΛ|ΠΗΝ|ΠΛΑΙΣ|ΠΟΝΤ|ΡΑΔ|ΡΟΔ|'
                    'ΣΚ|ΣΚΟΡΠ|ΣΟΥΝ|ΣΠΑΝ|ΣΤΑΔ|ΣΥΡ|ΤΗΛ|ΤΙΜ|ΤΟΚ|ΤΟΠ|ΤΡΟΧ|ΦΙΛ|'
                    'ΦΩΤ|Χ|ΧΙΛ|ΧΡΩΜ|ΧΩΡ)$', st):
                stem += u'Ι'
            if re.search(u'^(ΠΑΛ)$', st):
                stem += u'ΑΙ'

        # step 4
        m = re.search(u'^(.+?)(ΙΚΟΣ|ΙΚΟΝ|ΙΚΕΙΣ|ΙΚΟΙ|ΙΚΕΣ|ΙΚΟΥΣ|ΙΚΗ|ΙΚΗΣ|'
                      'ΙΚΟ|ΙΚΑ|ΙΚΟΥ|ΙΚΩΝ|ΙΚΩΣ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if self.ends_on_vowel(st) or re.search(
                    u'^(ΑΔ|ΑΛ|ΑΜΑΝ|ΑΜΕΡ|ΑΜΜΟΧΑΛ|ΑΝΗΘ|ΑΝΤΙΔ|ΑΠΛ|ΑΤΤ|ΑΦΡ|'
                    'ΒΑΣ|ΒΡΩΜ|ΓΕΝ|ΓΕΡ|Δ|ΔΥΤ|ΕΙΔ|ΕΝΔ|ΕΞΩΔ|ΗΘ|ΘΕΤ|ΚΑΛΛΙΝ|'
                    'ΚΑΛΠ|ΚΑΤΑΔ|ΚΡ|ΚΩΔ|ΛΟΓ|Μ|ΜΕΡ|ΜΟΝΑΔ|ΜΟΥΛ|ΜΟΥΣ|ΜΠΑΓΙΑΤ|'
                    'ΜΠΑΝ|ΜΠΟΛ|ΜΠΟΣ|ΜΥΣΤ|Ν|ΝΙΤ|ΞΙΚ|ΟΠΤ|ΠΑΝ|ΠΕΤΣ|ΠΙΚΑΝΤ|'
                    'ΠΙΤΣ|ΠΛΑΣΤ|ΠΛΙΑΤΣ|ΠΟΝΤ|ΠΟΣΤΕΛΝ|ΠΡΩΤΟΔ|ΣΕΡΤ|ΣΗΜΑΝΤ|'
                    'ΣΤΑΤ|ΣΥΝΑΔ|ΣΥΝΟΜΗΛ|ΤΕΛ|ΤΕΧΝ|ΤΡΟΠ|ΤΣΑΜ|ΥΠΟΔ|Φ|ΦΙΛΟΝ|'
                    'ΦΥΛΟΔ|ΦΥΣ|ΧΑΣ)$', st) or re.search(u'(ΦΟΙΝ)$', st):
                stem += u'ΙΚ'

        # step 5a
        if word == u'ΑΓΑΜΕ':
            stem = u'ΑΓΑΜ'

        m = re.search(u'^(.+?)(ΑΓΑΜΕ|ΗΣΑΜΕ|ΟΥΣΑΜΕ|ΗΚΑΜΕ|ΗΘΗΚΑΜΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st

        m = re.search(u'^(.+?)(ΑΜΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΑΝΑΠ|ΑΠΟΘ|ΑΠΟΚ|ΑΠΟΣΤ|ΒΟΥΒ|ΞΕΘ|ΟΥΛ|ΠΕΘ|ΠΙΚΡ|'
                         'ΠΟΤ|ΣΙΧ|Χ)$', st):
                stem += u'ΑΜ'

        # step 5b
        m = re.search(u'^(.+?)(ΑΓΑΝΕ|ΗΣΑΝΕ|ΟΥΣΑΝΕ|ΙΟΝΤΑΝΕ|ΙΟΤΑΝΕ|ΙΟΥΝΤΑΝΕ|'
                      'ΟΝΤΑΝΕ|ΟΤΑΝΕ|ΟΥΝΤΑΝΕ|ΗΚΑΝΕ|ΗΘΗΚΑΝΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΤΡ|ΤΣ)$', st):
                stem += u'ΑΓΑΝ'

        m = re.search(u'^(.+?)(ΑΝΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΒΕΤΕΡ|ΒΟΥΛΚ|ΒΡΑΧΜ|Γ|ΔΡΑΔΟΥΜ|Θ|ΚΑΛΠΟΥΖ|ΚΑΣΤΕΛ|'
                         'ΚΟΡΜΟΡ|ΛΑΟΠΛ|ΜΩΑΜΕΘ|Μ|ΜΟΥΣΟΥΛΜ|Ν|ΟΥΛ|Π|ΠΕΛΕΚ|ΠΛ|'
                         'ΠΟΛΙΣ|ΠΟΡΤΟΛ|ΣΑΡΑΚΑΤΣ|ΣΟΥΛΤ|ΤΣΑΡΛΑΤ|ΟΡΦ|ΤΣΙΓΓ|ΤΣΟΠ|'
                         'ΦΩΤΟΣΤΕΦ|Χ|ΨΥΧΟΠΛ|ΑΓ|ΟΡΦ|ΓΑΛ|ΓΕΡ|ΔΕΚ|ΔΙΠΛ|ΑΜΕΡΙΚΑΝ|'
                         'ΟΥΡ|ΠΙΘ|ΠΟΥΡΙΤ|Σ|ΖΩΝΤ|ΙΚ|ΚΑΣΤ|ΚΟΠ|ΛΙΧ|ΛΟΥΘΗΡ|ΜΑΙΝΤ|'
                         'ΜΕΛ|ΣΙΓ|ΣΠ|ΣΤΕΓ|ΤΡΑΓ|ΤΣΑΓ|Φ|ΕΡ|ΑΔΑΠ|ΑΘΙΓΓ|ΑΜΗΧ|'
                         'ΑΝΙΚ|ΑΝΟΡΓ|ΑΠΗΓ|ΑΠΙΘ|ΑΤΣΙΓΓ|ΒΑΣ|ΒΑΣΚ|ΒΑΘΥΓΑΛ|'
                         'ΒΙΟΜΗΧ|ΒΡΑΧΥΚ|ΔΙΑΤ|ΔΙΑΦ|ΕΝΟΡΓ|ΘΥΣ|ΚΑΠΝΟΒΙΟΜΗΧ|'
                         'ΚΑΤΑΓΑΛ|ΚΛΙΒ|ΚΟΙΛΑΡΦ|ΛΙΒ|ΜΕΓΛΟΒΙΟΜΗΧ|ΜΙΚΡΟΒΙΟΜΗΧ|'
                         'ΝΤΑΒ|ΞΗΡΟΚΛΙΒ|ΟΛΙΓΟΔΑΜ|ΟΛΟΓΑΛ|ΠΕΝΤΑΡΦ|ΠΕΡΗΦ|ΠΕΡΙΤΡ|'
                         'ΠΛΑΤ|ΠΟΛΥΔΑΠ|ΠΟΛΥΜΗΧ|ΣΤΕΦ|ΤΑΒ|ΤΕΤ|ΥΠΕΡΗΦ|ΥΠΟΚΟΠ|'
                         'ΧΑΜΗΛΟΔΑΠ|ΨΗΛΟΤΑΒ)$', st) or self.ends_on_vowel2(st):
                stem += u'ΑΝ'

        # step 5c
        m = re.search(u'^(.+?)(ΗΣΕΤΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st

        m = re.search(u'^(.+?)(ΕΤΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if self.ends_on_vowel2(st) or re.search(
                    u'(ΟΔ|ΑΙΡ|ΦΟΡ|ΤΑΘ|ΔΙΑΘ|ΣΧ|ΕΝΔ|ΕΥΡ|ΤΙΘ|ΥΠΕΡΘ|ΡΑΘ|ΕΝΘ|ΡΟΘ|'
                    'ΣΘ|ΠΥΡ|ΑΙΝ|ΣΥΝΔ|ΣΥΝ|ΣΥΝΘ|ΧΩΡ|ΠΟΝ|ΒΡ|ΚΑΘ|ΕΥΘ|ΕΚΘ|ΝΕΤ|ΡΟΝ|'
                    'ΑΡΚ|ΒΑΡ|ΒΟΛ|ΩΦΕΛ)$', st) or re.search(
                            u'^(ΑΒΑΡ|ΒΕΝ|ΕΝΑΡ|ΑΒΡ|ΑΔ|ΑΘ|ΑΝ|ΑΠΛ|ΒΑΡΟΝ|ΝΤΡ|ΣΚ|'
                            'ΚΟΠ|ΜΠΟΡ|ΝΙΦ|ΠΑΓ|ΠΑΡΑΚΑΛ|ΣΕΡΠ|ΣΚΕΛ|ΣΥΡΦ|ΤΟΚ|'
                            'Υ|Δ|ΕΜ|ΘΑΡΡ|Θ)$', st):
                stem += u'ΕΤ'

        # step 5d
        m = re.search(u'^(.+?)(ΟΝΤΑΣ|ΩΝΤΑΣ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^ΑΡΧ$', st):
                stem += u'ΟΝΤ'
            if re.search(u'ΚΡΕ$', st):
                stem += u'ΩΝΤ'

        # step 5e
        m = re.search(u'^(.+?)(ΟΜΑΣΤΕ|ΙΟΜΑΣΤΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^ΟΝ$', st):
                stem += u'ΟΜΑΣΤ'

        # step 5f
        m = re.search(u'^(.+?)(ΙΕΣΤΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(Π|ΑΠ|ΣΥΜΠ|ΑΣΥΜΠ|ΑΚΑΤΑΠ|ΑΜΕΤΑΜΦ)$', st):
                stem += u'ΙΕΣΤ'

        m = re.search(u'^(.+?)(ΕΣΤΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΑΛ|ΑΡ|ΕΚΤΕΛ|Ζ|Μ|Ξ|ΠΑΡΑΚΑΛ|ΑΡ|ΠΡΟ|ΝΙΣ)$', st):
                stem += u'ΕΣΤ'

        # step 5g
        m = re.search(u'^(.+?)(ΗΘΗΚΑ|ΗΘΗΚΕΣ|ΗΘΗΚΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st

        m = re.search(u'^(.+?)(ΗΚΑ|ΗΚΕΣ|ΗΚΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'(ΣΚΩΛ|ΣΚΟΥΛ|ΝΑΡΘ|ΣΦ|ΟΘ|ΠΙΘ)$', st) or re.search(
                    u'^(ΔΙΑΘ|Θ|ΠΑΡΑΚΑΤΑΘ|ΠΡΟΣΘ|ΣΥΝΘ|)$', st):
                stem += u'ΗΚ'

        # step 5h
        m = re.search(u'^(.+?)(ΟΥΣΑ|ΟΥΣΕΣ|ΟΥΣΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΦΑΡΜΑΚ|ΧΑΔ|ΑΓΚ|ΑΝΑΡΡ|ΒΡΟΜ|ΕΚΛΙΠ|ΛΑΜΠΙΔ|ΛΕΧ|'
                         'Μ|ΠΑΤ|Ρ|Λ|ΜΕΔ|ΜΕΣΑΖ|ΥΠΟΤΕΙΝ|ΑΜ|ΑΙΘ|ΑΝΗΚ|ΔΕΣΠΟΖ|'
                         'ΕΝΔΙΑΦΕΡ|ΔΕ|ΔΕΥΤΕΡΕΥ|ΚΑΘΑΡΕΥ|ΠΛΕ|ΤΣΑ)$', st) or \
                re.search(u'(ΠΟΔΑΡ|ΒΛΕΠ|ΠΑΝΤΑΧ|ΦΡΥΔ|ΜΑΝΤΙΛ|ΜΑΛΛ|ΚΥΜΑΤ|ΛΑΧ|'
                          'ΛΗΓ|ΦΑΓ|ΟΜ|ΠΡΩΤ)$', st) or self.ends_on_vowel(st):
                stem += u'ΟΥΣ'

        # step 5i
        m = re.search(u'^(.+?)(ΑΓΑ|ΑΓΕΣ|ΑΓΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if (re.search(
                u'^(ΑΒΑΣΤ|ΠΟΛΥΦ|ΑΔΗΦ|ΠΑΜΦ|Ρ|ΑΣΠ|ΑΦ|ΑΜΑΛ|ΑΜΑΛΛΙ|'
                'ΑΝΥΣΤ|ΑΠΕΡ|ΑΣΠΑΡ|ΑΧΑΡ|ΔΕΡΒΕΝ|ΔΡΟΣΟΠ|ΞΕΦ|ΝΕΟΠ|'
                'ΝΟΜΟΤ|ΟΛΟΠ|ΟΜΟΤ|ΠΡΟΣΤ|ΠΡΟΣΩΠΟΠ|ΣΥΜΠ|ΣΥΝΤ|Τ|ΥΠΟΤ|'
                'ΧΑΡ|ΑΕΙΠ|ΑΙΜΟΣΤ|ΑΝΥΠ|ΑΠΟΤ|ΑΡΤΙΠ|ΔΙΑΤ|ΕΝ|ΕΠΙΤ|'
                'ΚΡΟΚΑΛΟΠ|ΣΙΔΗΡΟΠ|Λ|ΝΑΥ|ΟΥΛΑΜ|ΟΥΡ|Π|ΤΡ|Μ)$', st) or
                re.search(u'(ΟΦ|ΠΕΛ|ΧΟΡΤ|ΛΛ|ΣΦ|ΡΠ|ΦΡ|ΠΡ|ΛΟΧ|ΣΜΗΝ)$', st)) and \
                not (re.search(u'^(ΨΟΦ|ΝΑΥΛΟΧ)$', st) or
                     re.search(u'(ΚΟΛΛ)$', st)):
                stem += u'ΑΓ'

        # step 5j
        m = re.search(u'^(.+?)(ΗΣΕ|ΗΣΟΥ|ΗΣΑ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(Ν|ΧΕΡΣΟΝ|ΔΩΔΕΚΑΝ|ΕΡΗΜΟΝ|ΜΕΓΑΛΟΝ|ΕΠΤΑΝ|Ι)$', st):
                stem += u'ΗΣ'

        # step 5k
        m = re.search(u'^(.+?)(ΗΣΤΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΑΣΒ|ΣΒ|ΑΧΡ|ΧΡ|ΑΠΛ|ΑΕΙΜΝ|ΔΥΣΧΡ|ΕΥΧΡ|'
                         'ΚΟΙΝΟΧΡ|ΠΑΛΙΜΨ)$', st):
                stem += u'ΗΣΤ'

        # step 5l
        m = re.search(u'^(.+?)(ΟΥΝΕ|ΗΣΟΥΝΕ|ΗΘΟΥΝΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(Ν|Ρ|ΣΠΙ|ΣΤΡΑΒΟΜΟΥΤΣ|ΚΑΚΟΜΟΥΤΣ|ΕΞΩΝ)$', st):
                stem += u'ΟΥΝ'

        # step 5m
        m = re.search(u'^(.+?)(ΟΥΜΕ|ΗΣΟΥΜΕ|ΗΘΟΥΜΕ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st
            if re.search(u'^(ΠΑΡΑΣΟΥΣ|Φ|Χ|ΩΡΙΟΠΛ|ΑΖ|ΑΛΛΟΣΟΥΣ|ΑΣΟΥΣ)$', st):
                stem += u'ΟΥΜ'

        # step 6a
        m = re.search(u'^(.+?)(ΜΑΤΟΙ|ΜΑΤΟΥΣ|ΜΑΤΟ|ΜΑΤΑ|ΜΑΤΩΣ|ΜΑΤΩΝ|ΜΑΤΟΣ|'
                      'ΜΑΤΕΣ|ΜΑΤΗ|ΜΑΤΗΣ|ΜΑΤΟΥ)$', stem)
        if m:
            st, suffix = m.groups()
            stem = st + u'Μ'
            if re.search(u'^(ΓΡΑΜ)$', st):
                stem += u'Α'
            elif re.search(u'^(ΓΕ|ΣΤΑ)$', st):
                stem += u'ΑΤ'

        if len(stem) == word_length:
            stem = self.long_stem_list(stem)

        m = re.search(
                u'^(.+?)(ΕΣΤΕΡ|ΕΣΤΑΤ|ΟΤΕΡ|ΟΤΑΤ|ΥΤΕΡ|ΥΤΑΤ|ΩΤΕΡ|ΩΤΑΤ)$', stem)
        if m:
            st, suffix = m.groups()
            if not re.search(u'^(ΕΞ|ΕΣ|ΑΝ|ΚΑΤ|Κ|ΠΡ)$', st):
                stem = st

            if re.search(u'^(ΚΑ|Μ|ΕΛΕ|ΛΕ|ΔΕ)$', st):
                stem = st + u'ΥΤ'

        return stem

    def is_greek(self, word):
        return True if self.alphabet_regex.match(word) else False

    def ends_on_vowel(self, word):
        return True if self.vowels_regex.search(word) else False

    def ends_on_vowel2(self, word):
        return True if self.vowels_without_y_regex.search(word) else False

    def load_settings(self):
        custom_rules = ""
        with open(os.path.join(
                  os.path.dirname(__file__), 'stemmer.yml'), 'r') as f:
            custom_rules = yaml.load(f.read())
        return custom_rules

    def long_stem_list(self, word):
        m = re.search(u'^(.+?)(Α|ΑΓΑΤΕ|ΑΓΑΝ|ΑΕΙ|ΑΜΑΙ|ΑΝ|ΑΣ|ΑΣΑΙ|ΑΤΑΙ|'
                      'ΑΩ|Ε|ΕΙ|ΕΙΣ|ΕΙΤΕ|ΕΣΑΙ|ΕΣ|ΕΤΑΙ|Ι|ΙΕΜΑΙ|ΙΕΜΑΣΤΕ|'
                      'ΙΕΤΑΙ|ΙΕΣΑΙ|ΙΕΣΑΣΤΕ|ΙΟΜΑΣΤΑΝ|ΙΟΜΟΥΝ|ΙΟΜΟΥΝΑ|ΙΟΝΤΑΝ|'
                      'ΙΟΝΤΟΥΣΑΝ|ΙΟΣΑΣΤΑΝ|ΙΟΣΑΣΤΕ|ΙΟΣΟΥΝ|ΙΟΣΟΥΝΑ|ΙΟΤΑΝ|'
                      'ΙΟΥΜΑ|ΙΟΥΜΑΣΤΕ|ΙΟΥΝΤΑΙ|ΙΟΥΝΤΑΝ|Η|ΗΔΕΣ|ΗΔΩΝ|ΗΘΕΙ|'
                      'ΗΘΕΙΣ|ΗΘΕΙΤΕ|ΗΘΗΚΑΤΕ|ΗΘΗΚΑΝ|ΗΘΟΥΝ|ΗΘΩ|ΗΚΑΤΕ|ΗΚΑΝ|'
                      'ΗΣ|ΗΣΑΝ|ΗΣΑΤΕ|ΗΣΕΙ|ΗΣΕΣ|ΗΣΟΥΝ|ΗΣΩ|Ο|ΟΙ|ΟΜΑΙ|ΟΜΑΣΤΑΝ|'
                      'ΟΜΟΥΝ|ΟΜΟΥΝΑ|ΟΝΤΑΙ|ΟΝΤΑΝ|ΟΝΤΟΥΣΑΝ|ΟΣ|ΟΣΑΣΤΑΝ|ΟΣΑΣΤΕ|'
                      'ΟΣΟΥΝ|ΟΣΟΥΝΑ|ΟΤΑΝ|ΟΥ|ΟΥΜΑΙ|ΟΥΜΑΣΤΕ|ΟΥΝ|ΟΥΝΤΑΙ|ΟΥΝΤΑΝ|'
                      'ΟΥΣ|ΟΥΣΑΝ|ΟΥΣΑΤΕ|Υ|ΥΣ|Ω|ΩΝ|ΟΙΣ)$', word)
        if m:
            st, suffix = m.groups()
            return st
        return word
