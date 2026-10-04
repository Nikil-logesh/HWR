"""Regression tests for defects found on REAL websites (first real run, 2026-10-04). Text is synthetic."""
from signalpost.web.extract import description_verdict, deterministic_candidates, email_verdict
from signalpost.web.identity import CompanyIdentity
from signalpost.web.text import parse_page

NAME, ORG = "NORDVIK BYGG AS", "910000012"


def cands(body: str, url="https://nordvik.example/"):
    drops: list[dict] = []
    pt = parse_page(url, f"<html><body>{body}</body></html>")
    return deterministic_candidates([pt], NAME, ORG, drops), drops


def vals(cs, field):
    return [c.value for c in cs if c.field == field]


def test_a_date_is_never_a_phone_number():  # real: "30.04.2026" was published as a phone
    cs, _ = cands("<p>Publisert 30.04.2026 og 01.12.2025 av oss. Sist oppdatert 3/10/2026.</p>")
    assert vals(cs, "contact_phone") == []


def test_real_phones_in_common_norwegian_formats_still_found():
    cs, _ = cands("<p>Tlf: 22 22 22 22</p><p>Mobil +47 906 00 980</p><p>Ring oss på 51 73 11 73.</p><p>Telefon: 41103482</p>")
    assert vals(cs, "contact_phone") == ["22 22 22 22", "+47 906 00 980", "51 73 11 73", "41103482"]


def test_phone_with_country_code_is_not_truncated():  # real: "+47 90 76 50 80" came out as "47 90 76 50"
    cs, _ = cands("<footer>Tlf kontor: +47 90 76 50 80 post@nordvik.example</footer>")
    assert vals(cs, "contact_phone") == ["+47 90 76 50 80"]
    cs2, _ = cands("<footer>Tlf kontor:&nbsp;+47&nbsp;90&nbsp;76&nbsp;50&nbsp;80</footer>")
    assert vals(cs2, "contact_phone") == ["+47 90 76 50 80"]


def test_labelled_organisation_bank_and_fax_numbers_are_not_phones():
    cs, drops = cands("<p>Org.nr 915 23 456</p><p>Bank: 123 45 678</p><p>Fax 22 11 22 33</p><p>KID 123 45 678</p><p>Tlf 22 33 44 55</p>")
    assert vals(cs, "contact_phone") == ["22 33 44 55"]
    assert any("labelled as" in d["reason"] for d in drops)


def test_org_number_and_phone_on_one_footer_line_keep_the_phone():
    cs, _ = cands("<footer>Nordvik Bygg AS, Havnegata 12, 6003 Ålesund. Org.nr. 910 000 012. Telefon 70 12 34 56</footer>")
    assert vals(cs, "contact_phone") == ["70 12 34 56"]


def test_template_placeholder_and_noreply_emails_are_rejected():  # real: fornavn.etternavn@europress.no
    cs, drops = cands("<p>Kontakt: fornavn.etternavn@nordvik.example, noreply@nordvik.example, post@nordvik.example</p>")
    assert vals(cs, "contact_email") == ["post@nordvik.example"]
    assert sum(d["reason"] == "placeholder, no-reply or invoicing mailbox" for d in drops) == 2


def test_email_on_another_business_domain_is_dropped_unless_next_to_the_company_name():
    # real: receive@compello.com (invoice scanner) and a building manager's mailbox on someone else's site
    cs, drops = cands("<p>Kvittering sendes til receive@compello.com</p><p>Styret: styret@bate.no</p>")
    assert vals(cs, "contact_email") == []
    assert all("not next to the company name" in d["reason"] for d in drops) and len(drops) == 2
    near, _ = cands("<p>Nordvik Bygg AS</p><p>Epost: kontakt@annet-domene.example</p>")
    assert vals(near, "contact_email") == ["kontakt@annet-domene.example"]
    org_near, _ = cands("<p>Org.nr 910 000 012 – kontakt@regnskap.example</p>")
    assert vals(org_near, "contact_email") == ["kontakt@regnskap.example"]


def test_site_domain_and_freemail_are_accepted():
    cs, _ = cands("<p>post@nordvik.example</p><p>nordvik.bygg@gmail.com</p><p>per@online.no</p>")
    assert set(vals(cs, "contact_email")) == {"post@nordvik.example", "nordvik.bygg@gmail.com", "per@online.no"}


def test_email_verdict_unit():
    assert email_verdict("a@nordvik.example", "https://www.nordvik.example/x", "a@nordvik.example", NAME, ORG) is None
    assert email_verdict("test@nordvik.example", "https://nordvik.example/", "test@nordvik.example", NAME, ORG)


def test_foreign_country_codes_are_never_published_as_norwegian_numbers():  # real: +46 Swedish and +45 Danish numbers
    cs, drops = cands("<p>Tollfokus AB +46 10 27 67 600</p><p>Mobile: +45 29684865</p><p>Mobil +47 91 19 09 46</p>")
    assert vals(cs, "contact_phone") == ["+47 91 19 09 46"]
    assert any("foreign country code" in d["reason"] for d in drops)


def test_plus_space_47_number_is_not_truncated():  # real: "+ 47 90 76 50 80" was published as "47 90 76 50"
    cs, _ = cands("<p>Tlf kontor: + 47 90 76 50 80</p>")
    assert vals(cs, "contact_phone") == ["+ 47 90 76 50 80"]


def test_same_phone_in_two_formats_is_one_fact():  # real: "69891227" and "69 89 12 27" were both published
    cs, _ = cands("<p>Telefon: 69 89 12 27</p><p>Ring 69891227 i dag</p>")
    assert len(vals(cs, "contact_phone")) == 1


def test_invoicing_mailboxes_are_not_contact_emails():  # real: invoicesAS@europress.no, Faktura@mortec.no
    cs, drops = cands("<p>E-post: post@nordvik.example. Faktura: faktura@nordvik.example, invoicesAS@nordvik.example</p>")
    assert vals(cs, "contact_email") == ["post@nordvik.example"]
    assert len(drops) == 2


def test_shared_mailboxes_come_before_personal_ones():  # real: three personal addresses crowded post@ out of the cap
    cs, _ = cands("<p>lasse@nordvik.example magnus@nordvik.example post@nordvik.example</p>")
    assert vals(cs, "contact_email")[0] == "post@nordvik.example"


def test_descriptions_that_are_address_blocks_or_contain_markup_are_dropped():  # real: Ryenberget skole, Energi-Spar
    html = ('<meta name="description" content="Ryenberget skole Enebakkveien 152 0680 Oslo Tlf: 23 21 01 61 E-post: post@x.example">'
            '<meta property="og:description" content="Vi dekker alle fagomr&aring;der innen varmepumper.<br />Har spesialisering.">')
    drops: list[dict] = []
    pt = parse_page("https://nordvik.example/", f"<html><head>{html}</head><body><p>x</p></body></html>")
    assert vals(deterministic_candidates([pt], NAME, ORG, drops), "website_description") == []
    assert {d["reason"] for d in drops} >= {"contact details, not a description"}


def test_social_link_tracking_parameters_are_not_part_of_the_published_value():  # real: ...mortecas/?view_public_for=48762
    cs, _ = cands('<a href="https://www.facebook.com/nordvikbygg/?view_public_for=487622811770293">Facebook</a>')
    [c] = [c for c in cs if c.field == "social_facebook"]
    assert c.value == "https://www.facebook.com/nordvikbygg/" and c.value in c.snippet


def test_description_verdict_markup_and_plain_text():
    assert description_verdict("Alt innen varme.<br />Har spesialisering.") == "markup inside the description"
    assert description_verdict("Vi bygger hus og renoverer bad i Stavanger.") is None


SISTERS = ("<h2>Nordvik Bygg AS</h2><p>Havnegata 1 5217 Hagavik</p><p>Tel: 93861541</p><p>Mail: ola@nordvikbygg.no</p>"
           "<h2>Fjellvik Bygg</h2><p>Fjellveien 55 5314 Kjerrgarden</p><p>Tel: 56155590</p><p>Mail: kari@fjellvik.example</p>"
           "<h2>Sjøvik Bygg</h2><p>Kaia 6 0176 Oslo</p><p>Tel: 40000078</p>" + "<p>.</p>" * 40 + "<p>Administrasjon: helene@nordvik.example</p>")
OWN = CompanyIdentity(ORG, NAME, street="Havnegata 1", postcode="5217", city="HAGAVIK")


def test_on_a_sister_unit_listing_only_contacts_next_to_this_company_are_published():  # real: piba.no, 4 sister kindergartens
    drops: list[dict] = []
    pt = parse_page("https://nordvik.example/", f"<html><body>{SISTERS}</body></html>")
    cs = deterministic_candidates([pt], NAME, ORG, drops, OWN)
    assert vals(cs, "contact_phone") == ["93861541"]  # not 56155590 (Fjellvik) or 40000078 (Sjøvik)
    assert vals(cs, "contact_email") == ["ola@nordvikbygg.no"]  # the domain carries the company name, so the other domain is fine
    assert any("block for the company" in d["reason"] for d in drops)  # the administration mailbox sits with another unit


def test_single_location_page_keeps_every_contact():
    cs, _ = cands("<p>Nordvik Bygg AS</p><p>Tel: 93861541 / 56155590</p><p>post@nordvik.example</p>")
    assert vals(cs, "contact_phone") == ["93861541", "56155590"]


def test_other_domain_mailbox_in_running_text_is_not_attributed_by_a_passing_mention():  # real: a member firm's address on Eurojuris' ISO page
    text = "<p>Kvalitetsansvarlig for Nordvik Bygg AS er Lars.</p><p>Kontakt</p><p>x</p><p>y</p><p>lars@advokatfirma.example</p>"
    cs, drops = cands(text)
    assert vals(cs, "contact_email") == [] and drops[0]["reason"].startswith("email domain differs")
    assert vals(cands("<p>Nordvik Bygg AS</p><p>post@nordvikbygg.no</p>")[0], "contact_email") == ["post@nordvikbygg.no"]


def test_group_page_core_name_does_not_claim_sister_units():  # real: "Washington Mills AS" vs "Washington Mills North Grafton, Inc."
    ident = CompanyIdentity(ORG, "WASHINGTON MILLS AS", street="Kaia 1", postcode="7300", city="ORKANGER")
    body = ("<p>Washington Mills North Grafton, Inc.</p><p>20 Main St 01536 Grafton</p><p>info@washingtonmills.example</p>"
            "<p>Washington Mills Electro Minerals</p><p>Mosley Road 1801 Buffalo</p><p>sales@washingtonmills.example</p>"
            "<p>Washington Mills Iberia</p><p>Calle Sol 5 2800 Madrid</p><p>iberia@washingtonmills.example</p>"
            "<p>Washington Mills AS</p><p>NO-7300 Orkanger</p><p>wmas@washingtonmills.example</p>")
    drops: list[dict] = []
    pt = parse_page("https://washingtonmills.example/", f"<html><body>{body}</body></html>")
    cs = deterministic_candidates([pt], "WASHINGTON MILLS AS", ORG, drops, ident)
    assert vals(cs, "contact_email") == ["wmas@washingtonmills.example"]


def test_listing_without_any_block_for_this_company_publishes_nothing():  # real: a chain page where the company has no own block
    body = ("<h2>Fjellvik Bygg</h2><p>Fjellveien 55 5314 Kjerrgarden</p><p>Tel: 56155590</p>"
            "<h2>Sjøvik Bygg</h2><p>Kaia 6 0176 Oslo</p><p>Tel: 40000078</p><h2>Bergvik Bygg</h2><p>Torget 2 5003 Bergen</p><p>Tel: 55000000</p>")
    drops: list[dict] = []
    pt = parse_page("https://nordvik.example/", f"<html><body>{body}</body></html>")
    assert deterministic_candidates([pt], NAME, ORG, drops, OWN) == []
    assert {d["reason"] for d in drops} == {"page lists several other locations and this contact is not next to this company's name or address"}
