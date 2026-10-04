"""Group / portfolio pages are not exact matches (RULES.md). Motivated by a real run: a property group's page listed eight
single-purpose companies with their organisation numbers and one of them was published as "verified". Text is synthetic."""
from signalpost.universe import valid_orgnr
from signalpost.web.identity import CompanyIdentity, assess
from signalpost.web.text import parse_page


def mk(n: int) -> str:
    k = 910000000 + n * 7
    while not valid_orgnr(str(k)):
        k += 1
    return str(k)


def spaced(o: str) -> str:
    return f"{o[:3]} {o[3:6]} {o[6:]}"


def res(ident, body):
    return assess(ident, [parse_page("https://x.example/", f"<html><body>{body}</body></html>")])


OURS, B, C, D = mk(1), mk(2), mk(3), mk(4)
ID = CompanyIdentity(OURS, "NORDVIK F3 NÆRING AS", street="Havnegata 1", postcode="0252", city="OSLO")


def test_own_number_in_a_list_of_other_companies_is_a_portfolio_page_not_a_match():
    body = "".join(f"<li>{n} AS {spaced(o)}</li>" for n, o in [("Nordvik F2 Næring", B), ("Nordvik F3 Næring", OURS),
                                                              ("Nordvik F7 Næring", C), ("Nordvik F8 Næring", D)])
    r = res(ID, body)
    assert not r.publishable and "group or portfolio" in (r.veto or "")


def test_own_number_with_one_parent_mentioned_is_still_a_match():
    r = res(ID, f"<p>Nordvik F3 Næring AS Org.nr {spaced(OURS)}. Eid av Nordvik Gruppen AS, org.nr {spaced(B)}</p>")
    assert r.publishable and r.score == 1.0


def test_stray_numbers_that_merely_pass_modulus_11_do_not_trigger_the_group_veto():
    r = res(ID, f"<p>Nordvik F3 Næring AS Org.nr {spaced(OURS)}</p><p>Varenr {spaced(B)} og {spaced(C)} og {spaced(D)}</p>")
    assert r.publishable
