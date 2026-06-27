from llm_eval.scoring import answer_correct, regex_matches, response_correct, tool_selection_correct


def test_answer_correct_exact_and_numeric():
    assert answer_correct("391", "391")
    assert answer_correct("1,000", "1000.0")
    assert answer_correct("Θερμοπύλες", "Στη μάχη των Θερμοπυλών", r"Θερμοπ.*")
    assert not answer_correct("cobalt", "blue")
    assert not answer_correct("Θερμοπύλες", "Μαραθώνας", r"Θερμοπ.*")
    assert not answer_correct("anything", "value", "[")
    assert not regex_matches(r"Θερμοπ.*", None)


def test_tool_selection_subset():
    assert tool_selection_correct(["calculator_multiply"], ["calculator_multiply", "calculator_add"])
    assert not tool_selection_correct(["calculator_power"], ["calculator_multiply"])
    assert tool_selection_correct([], [])


def test_language_regexes_accept_short_direct_answers():
    cases = [
        ("Στις 27 Μαΐου 1942", "27 Μαΐου 1942", r"(?:Στις\s*)?27\s+Μαΐου\s+1942"),
        ("Stis 27 Maioy 1942", "27 Maioy 1942", r"(?:Stis\s*|Στις\s*)?27\s+(?:Maioy|Μαΐου)\s+1942"),
        ("το 2003", "2003", r"(?:το\s*)?2003"),
        ("3.166 άτομα", "3.166", r"3\.166(?:\s*άτομ\w*)?"),
        (
            "Η Εθνική Βραζιλίας ηττήθηκε από την Εθνική Παραγουάης με σκορ 0:2 στα πέναλτι",
            "ηττήθηκε με σκορ 0:2 στα πέναλτι",
            r"ηττήθηκ\w*[\s\S]*(?:Παραγουά\w*[\s\S]*)?0\s*:?\s*2[\s\S]*πέναλτι\w*",
        ),
        (
            "για να ειναι στατιστικα significant θες τουλαχιστον τοσους οταν το πλυθος για το οποιο μιλας ειναι 10 εκατομμύρια",
            "για να ειναι στατιστικα significant θες τουλάχιστον τοσους οταν το πλυθος για το οποιο μιλας ειναι 10 εκατομμύρια",
            r"στατιστ\w*[\s\S]*signifi\w*[\s\S]*τουλ[αά]χι\w*",
        ),
        ("νήσους Μάρσαλ και Τζίλμπερτ", "Μάρσαλ και Τζίλμπερτ", r"(?:νήσους\w*[\s\S]*)?Μάρσαλ\w*[\s\S]*Τζίλμπε\w*"),
        ("14 μήνες ειρήνης", "14", r"14(?:\s+μήνες(?:\s+ειρήνης)?)?"),
        ("28 οικογένειες", "28", r"28(?:\s+οικογέν\w*)?"),
        ("μην βάλεις την εμπειρία από την σεζόν", "σεζόν", r"(?:βάλεις\w*[\s\S]*εμπειρί\w*[\s\S]*)?σεζόν\w*"),
        ("τον Ιούνιο του 2007", "2007", r"(?:Ιούνιο\w*[\s\S]*του\s*)?2007"),
        ("μόλις 17 εκατ. λιρών", "17 εκατ. λίρες", r"17\s+εκατ\.?\s+λ[ιί]ρ\w*"),
        ("έξι βραβεία", "6", r"(?:6|έξι)(?:\s+βραβεία\w*)?"),
        ("πέντε φορές", "Πέντε", r"πέντε(?:\s+φορές)?"),
    ]

    for expected, extracted, pattern in cases:
        assert answer_correct(expected, extracted, pattern)


def test_response_correct_matches_raw_response_when_extraction_is_too_short():
    assert response_correct(
        "στο pestview γαμιέται ο δίας ακόμη και χωρίς AI",
        "AI",
        "Ανέφερε ότι το pestview γαμιέται ο δίας ακόμη και χωρίς AI.",
        r"pestview[\s\S]*γαμι[εέ]ται[\s\S]*δ[ιί]ας[\s\S]*AI",
    )
    assert response_correct(
        "Στις 27 Μαΐου 1942",
        "1942",
        "Στις 27 Μαΐου 1942.",
    )
    assert not response_correct("cobalt", "blue", "The answer is green.")


def test_response_correct_accepts_mixed_script_and_paraphrase_matches():
    assert response_correct(
        "telos panton, prepi na paroume to account tou stripe apo ton xagara, theloume na mas kani add opos eixe gini sto heroku kai sto azure kai oxi na mas dosi ta stixia.",
        "prepi na παρουme το account tou stripe apo ton xagara, thelουμε na mas kani add οποs eixe gini sto heroku kai sto azure kai oxi na mas δοση ta stixia",
        "FINAL_ANSWER: prepi na παρουme το account tou stripe apo ton xagara, thelουμε na mas kani add οποs eixe gini sto heroku kai sto azure kai oxi na mas δοση ta stixia.",
    )
    assert response_correct(
        "προς το παρόν κοιτάς το board Client Documentation",
        "Documentation",
        "Αντικείμενο: board Client Documentation",
    )
    assert response_correct(
        "ναι, ηθελα να δεις εαν χρειαζοταν κατι αλλο αλλαγη πριν τα παω εκει",
        "εκεί",
        "Το Taylor ανέφερε ότι χρειαζόταν να δει αν χρειάζεται κάτι άλλο πριν τα παω εκεί.",
    )
    assert response_correct(
        "και μετα ολοι θα πρεπει να φερετε το local σας στη κατασταση που θα ειναι το remote",
        "remote",
        "Ο Casey ανέφερε ότι οι άλλοι θα πρέπει να φέρουν το local τους στη κατάσταση που θα είναι το remote.",
    )
    assert response_correct(
        "ειχα ενα task, να βαλω να φαινονται τα consumables on visit appointment στα reports",
        "reports",
        "Το Casey ανέφερε ότι είχε ένα task να βάλει τα consumables να εμφανιστούν στα reports.",
    )


def test_response_correct_rejects_unrelated_short_responses():
    assert not response_correct(
        "na klaftei pou ton eipa oti den ginetai na kanoume amesws ylopoiisi kai na kanoume k swsto estimate mazi?",
        "υπάρχει",
        "Αυτό το κείμενο δεν υπάρχει.",
    )
    assert not response_correct(
        "ekana upload to logo metatopia sto openproject epitelos kai alaksa to theme",
        "OpenProject",
        "Αναφέρεται στην επιλογή του λογότυπου του MetaProject για το OpenProject.",
    )
