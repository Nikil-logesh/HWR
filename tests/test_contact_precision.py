"""Regression tests for defects found on REAL websites (first real run, 2026-10-04). Text is synthetic."""
from signalpost.web.extract import deterministic_candidates, email_verdict
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
    assert sum(d["reason"] == "placeholder or no-reply mailbox" for d in drops) == 2


def test_email_on_another_business_domain_is_dropped_unless_next_to_the_company_name():
    # real: receive@compello.com (invoice scanner) and faktura@bate.no (building manager) on someone else's site
    cs, drops = cands("<p>Faktura sendes til receive@compello.com</p><p>Styret: faktura@bate.no</p>")
    assert vals(cs, "contact_email") == []
    assert all("not next to the company name" in d["reason"] for d in drops) and len(drops) == 2
    near, _ = cands("<p>Nordvik Bygg AS</p><p>Epost: kontakt@annet-domene.example</p>")
    assert vals(near, "contact_email") == ["kontakt@annet-domene.example"]
    org_near, _ = cands("<p>Org.nr 910 000 012 – faktura@regnskap.example</p>")
    assert vals(org_near, "contact_email") == ["faktura@regnskap.example"]


def test_site_domain_and_freemail_are_accepted():
    cs, _ = cands("<p>post@nordvik.example</p><p>nordvik.bygg@gmail.com</p><p>per@online.no</p>")
    assert set(vals(cs, "contact_email")) == {"post@nordvik.example", "nordvik.bygg@gmail.com", "per@online.no"}


def test_email_verdict_unit():
    assert email_verdict("a@nordvik.example", "https://www.nordvik.example/x", "a@nordvik.example", NAME, ORG) is None
    assert email_verdict("test@nordvik.example", "https://nordvik.example/", "test@nordvik.example", NAME, ORG)
