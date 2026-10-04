"""Trade-name tier (0.90) and street handling, motivated by real sites: smorhamn.no, lifjellstua.no,
interiorprosjekt.no (name differs from the legal name, address matches exactly). Page text is synthetic."""
from signalpost.web.identity import PUBLISH_THRESHOLD, CompanyIdentity, assess, distinctive_tokens, street_variants
from signalpost.web.text import parse_page


def res(ident, body):
    return assess(ident, [parse_page("https://x.example/", f"<html><body>{body}</body></html>")])


SMORHAMN = CompanyIdentity("910000012", "SMØRHAMN HANDELSTAD AS", street="Smørhamnsvegen 1114", postcode="6729", city="KALVÅG")
LIFJELL = CompanyIdentity("910000020", "LIFJELLSTUA EIENDOM AS", street="Lifjellvegen 934", postcode="3804", city="BØ I TELEMARK")
CO = CompanyIdentity("910000039", "STINA INTERIØR AS", street="c/o Gunnvald Harila, Lisbergvegen 9", postcode="2740", city="ROA")


def test_trade_name_with_exact_street_and_postcode_city_is_publishable_at_exactly_the_threshold():
    r = res(SMORHAMN, "<h1>Smørhamn Handelsstad</h1><p>Smørhamnsvegen 1114, 6729 Kalvåg</p>")  # site spells it differently
    assert r.score == 0.90 == PUBLISH_THRESHOLD and r.publishable
    assert r.signals == ["legal_name_partial", "street_address", "postcode_city"] and "1114" in (r.snippet or "")
    assert res(LIFJELL, "<h1>Lifjellstua</h1><p>Lifjellvegen 934, 3804 Bø i Telemark</p>").publishable


def test_partial_name_without_the_full_address_is_not_enough():
    assert not res(SMORHAMN, "<h1>Smørhamn Handelsstad</h1>").publishable  # no address at all
    assert not res(SMORHAMN, "<h1>Smørhamn</h1><p>Smørhamnsvegen 1114</p>").publishable  # street but no postcode+city
    assert not res(SMORHAMN, "<h1>Smørhamn</h1><p>6729 Kalvåg</p>").publishable  # postcode+city but no street
    assert not res(SMORHAMN, "<p>Smørhamnsvegen, 6729 Kalvåg</p><h1>Smørhamn</h1>").publishable  # street without number


def test_address_alone_or_a_generic_word_never_identifies_a_company():
    assert not res(SMORHAMN, "<h1>Naboen AS</h1><p>Smørhamnsvegen 1114, 6729 Kalvåg</p>").publishable  # co-tenant, other name
    assert not res(LIFJELL, "<h1>Eiendom til salgs</h1><p>Lifjellvegen 934, 3804 Bø i Telemark</p>").publishable  # only 'eiendom'
    assert distinctive_tokens("NORDVIK EIENDOM AS") == ["nordvik"] and distinctive_tokens("AS GROUP HOLDING") == []


def test_c_o_street_is_matched_on_its_house_number_part_only():
    assert street_variants("c/o Gunnvald Harila, Lisbergvegen 9") == ["c o gunnvald harila lisbergvegen 9", "lisbergvegen 9"]
    assert street_variants("Postboks") == [] and street_variants(None) == []
    r = res(CO, "<h1>Stina Interiør AS</h1><p>Lisbergvegen 9, 2740 Roa</p>")
    assert r.publishable and r.signals[:2] == ["legal_name", "street_address"] and r.score == 0.95


def test_a_different_organisation_number_still_vetoes_the_partial_tier():
    r = res(SMORHAMN, "<h1>Smørhamn</h1><p>Smørhamnsvegen 1114, 6729 Kalvåg. Org.nr 910 000 020</p>")
    assert not r.publishable and r.veto and "different organisation number" in r.veto
