# Audit review sheet

For each company check: (1) the REGISTER rows against the linked Brønnøysund record, (2) every WEB row: does the source URL really belong to this company, and does the snippet contain the value? Mark a verdict per row (CSV has a verdict column). A single 'wrong company' verdict blocks publication of that profile.

## PROFLAME AS — 821535352

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/821535352>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=29579.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/821535352 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=29579.0 |
| REGISTER | financials.total_assets | amount=301543.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/821535352 | eiendeler.sumEiendeler=301543.0 |
| REGISTER | founded | 2018-09-11 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | stiftelsesdato="2018-09-11" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | PROFLAME AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | navn="PROFLAME AS" |
| REGISTER | nace | code=46.490, description=Engroshandel med andre husholdningsvarer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | naeringskode1.kode="46.490" |
| WEB | official_website | not published: identity score 0.50 below 0.9 (signals: legal_name); candidate domain built from the legal name, not listed in the register | 0.0 | https://proflame.no/ | not published: identity score 0.50 below 0.9 (signals: legal_name); candidate domain built from the legal name, not listed in the register |
| REGISTER | registered_address | city=TANANGER, country=Norge, municipality=SOLA, municipality_number=1124, postcode=4056, street=Rodamyrkroken 11 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | forretningsadresse={"adresse": ["Rodamyrkroken 11"], "poststed": "TANANGER", "postnummer": "4056", "kommune": "SOLA", "kommunenummer": "1124", "land": "Norge",  |
| REGISTER | roles | last_changed=2018-10-11, name=Bernt Andre Bratlie, role=Daglig leder, role_code=DAGL; last_changed=2018-10-11, name=Bernt Andre Bratlie, role=Styrets leder, rol | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352/roller | Daglig leder: Bernt Andre Bratlie; Styrets leder: Bernt Andre Bratlie; Varamedlem: Elisabeth Bratlie |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/821535352 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=TANANGER, country=Norge, municipality=SOLA, municipality_number=1124, postcode=4056, street=Rodamyrkroken 11, nace=46.490, name=PROFLAME AS, organi | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=821535352&size=100 | 921643845 PROFLAME AS |

## JAVI HOLDING AS — 880166352

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/880166352>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=0.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/880166352 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=0.0 |
| REGISTER | financials.total_assets | amount=275340.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/880166352 | eiendeler.sumEiendeler=275340.0 |
| REGISTER | founded | 1998-09-04 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | stiftelsesdato="1998-09-04" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | JAVI HOLDING AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | navn="JAVI HOLDING AS" |
| REGISTER | nace | code=68.110, description=Kjøp og salg av egen fast eiendom | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | naeringskode1.kode="68.110" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (javiholding.no does not exist or is unreachable; j | 1.0 |  |  |
| REGISTER | registered_address | city=HAUGESUND, country=Norge, municipality=HAUGESUND, municipality_number=1106, postcode=5527, street=Haraldsgata 146 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | forretningsadresse={"adresse": ["Haraldsgata 146"], "poststed": "HAUGESUND", "postnummer": "5527", "kommune": "HAUGESUND", "kommunenummer": "1106", "land": "Nor |
| REGISTER | roles | last_changed=1998-10-02, name=Ivar Jacobsen, role=Daglig leder, role_code=DAGL; last_changed=1998-10-02, name=Ivar Jacobsen, role=Styrets leder, role_code=LEDE; | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352/roller | Daglig leder: Ivar Jacobsen; Styrets leder: Ivar Jacobsen; Varamedlem: John Kongshavn |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/880166352 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=HAUGESUND, country=Norge, municipality=HAUGESUND, municipality_number=1106, postcode=5527, street=Haraldsgata 146, nace=68.110, name=JAVI HOLDING A | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=880166352&size=100 | 890291082 JAVI HOLDING AS |

## BERGEN HUDLEGEKLINIKK TORE MORKEN AS — 889252022

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/889252022>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=5648334.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/889252022 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=5648334.0 |
| REGISTER | financials.total_assets | amount=3479581.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/889252022 | eiendeler.sumEiendeler=3479581.0 |
| REGISTER | founded | 2005-12-27 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | stiftelsesdato="2005-12-27" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | BERGEN HUDLEGEKLINIKK TORE MORKEN AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | navn="BERGEN HUDLEGEKLINIKK TORE MORKEN AS" |
| REGISTER | nace | code=86.221, description=Spesialiserte legetjenester, unntatt psykiatriske legetjenester | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | naeringskode1.kode="86.221" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (bergenhudlegeklinikktoremorken.no does not exist o | 1.0 |  |  |
| REGISTER | registered_address | city=BERGEN, country=Norge, municipality=BERGEN, municipality_number=4601, postcode=5012, street=Valkendorfsgaten 9 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | forretningsadresse={"adresse": ["Valkendorfsgaten 9"], "poststed": "BERGEN", "postnummer": "5012", "kommune": "BERGEN", "kommunenummer": "4601", "land": "Norge" |
| REGISTER | roles | last_changed=2006-01-04, name=Tore Morken, role=Daglig leder, role_code=DAGL; last_changed=2006-01-04, name=Tore Morken, role=Styrets leder, role_code=LEDE; las | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022/roller | Daglig leder: Tore Morken; Styrets leder: Tore Morken; Varamedlem: Mette Helvik Morken |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/889252022 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=BERGEN, country=Norge, municipality=BERGEN, municipality_number=4601, postcode=5012, street=Valkendorfsgaten 9, nace=86.221, name=BERGEN HUDLEGEKLI | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=889252022&size=100 | 980544109 BERGEN HUDLEGEKLINIKK TORE MORKEN AS |

## LTS FLYFISHING AS — 897757672

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/897757672>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | service@lts-flyfishing.com | 0.85 | https://lts-flyfishing.com/ | service@lts-flyfishing.com |
| WEB | contact_phone_1 | 95827078 | 0.85 | https://lts-flyfishing.com/kontakt-oss/ | Telefon :Jon Erik: 95827078 |
| REGISTER | financials.revenue | amount=2745703.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/897757672 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=2745703.0 |
| REGISTER | financials.total_assets | amount=5693674.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/897757672 | eiendeler.sumEiendeler=5693674.0 |
| REGISTER | founded | 2011-12-15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672 | stiftelsesdato="2011-12-15" |
| WEB | latest_activity_date | 2024-03-14 | 0.9 | https://lts-flyfishing.com/feed/ | <height>32</height> </image>  	<item> 		<title>Tidligfiske</title> 		<link>https://lts-flyfishing.com/tidligfiske/</link> 					<comments>https://lts-flyfishing. |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | LTS FLYFISHING AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672 | navn="LTS FLYFISHING AS" |
| REGISTER | nace | code=46.490, description=Engroshandel med andre husholdningsvarer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672 | naeringskode1.kode="46.490" |
| WEB | official_website | https://lts-flyfishing.com/ | 1.0 | https://lts-flyfishing.com/ | 332 Løkken Verk • Norge service@lts-flyfishing.com org. nr: 897757672 Frakt, angrerett og retur Personvernerklæring Vilkår og bet |
| WEB | public_activity | date=2024-03-14, date_text=Thu, 14 Mar 2024 13:24:17 +0000, title=Tidligfiske, url=https://lts-flyfishing.com/tidligfiske/; date=2020-11-23, date_text=Mon, 23 N | 0.9 | https://lts-flyfishing.com/feed/ | <height>32</height> </image>  	<item> 		<title>Tidligfiske</title> 		<link>https://lts-flyfishing.com/tidligfiske/</link> 					<comments>https://lts-flyfishing. |
| REGISTER | registered_address | city=LØKKEN VERK, country=Norge, municipality=ORKLAND, municipality_number=5059, postcode=7332, street=Løkkenveien 276 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672 | forretningsadresse={"adresse": ["Løkkenveien 276"], "poststed": "LØKKEN VERK", "postnummer": "7332", "kommune": "ORKLAND", "kommunenummer": "5059", "land": "Nor |
| REGISTER | roles | last_changed=2012-01-04, name=Leiv Birger Rædergård, role=Daglig leder, role_code=DAGL; last_changed=2025-10-11, name=Leiv Birger Rædergård, role=Styremedlem, r | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672/roller | Daglig leder: Leiv Birger Rædergård; Styremedlem: Leiv Birger Rædergård; Styremedlem: Trond Syrstad; Styrets leder: John Olav Rædergård |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/897757672 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=LØKKEN VERK, country=Norge, municipality=ORKLAND, municipality_number=5059, postcode=7332, street=Løkkenveien 276, nace=46.490, name=LTS FLYFISHING | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=897757672&size=100 | 997798333 LTS FLYFISHING AS |

## AMICITIA AS — 914749158

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/914749158>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.total_assets | amount=4658902.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/914749158 | eiendeler.sumEiendeler=4658902.0 |
| REGISTER | founded | 2014-12-16 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | stiftelsesdato="2014-12-16" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | AMICITIA AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | navn="AMICITIA AS" |
| REGISTER | nace | code=00.000, description=Uoppgitt | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | naeringskode1.kode="00.000" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (amicitia.no does not exist or is unreachable; amic | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0278, street=Karenslyst Allé 8B | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | forretningsadresse={"adresse": ["Karenslyst Allé 8B"], "poststed": "OSLO", "postnummer": "0278", "kommune": "OSLO", "kommunenummer": "0301", "land": "Norge", "l |
| REGISTER | roles | last_changed=2015-01-06, name=Eli Sævareid, role=Daglig leder, role_code=DAGL; last_changed=2015-01-06, name=Eli Sævareid, role=Styrets leder, role_code=LEDE | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158/roller | Daglig leder: Eli Sævareid; Styrets leder: Eli Sævareid |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914749158 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | checked: no registered subunits | 1.0 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=914749158&size=100 | checked: no registered subunits |

## KNUTEPUNKTET NAMO AS — 914859298

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/914859298>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | financials.revenue | amount=7076393.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/914859298 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=7076393.0 |
| REGISTER | financials.total_assets | amount=1630107.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/914859298 | eiendeler.sumEiendeler=1630107.0 |
| REGISTER | founded | 2015-01-05 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298 | stiftelsesdato="2015-01-05" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | KNUTEPUNKTET NAMO AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298 | navn="KNUTEPUNKTET NAMO AS" |
| REGISTER | nace | code=47.110, description=Detaljhandel med bredt vareutvalg med hovedvekt på nærings- og nytelsesmidler | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298 | naeringskode1.kode="47.110" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (knutepunktetnamo.no does not exist or is unreachab | 1.0 |  |  |
| REGISTER | registered_address | city=KRISTIANSUND N, country=Norge, municipality=KRISTIANSUND, municipality_number=1505, postcode=6514, street=Kordellen 18 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298 | forretningsadresse={"adresse": ["Kordellen 18"], "poststed": "KRISTIANSUND N", "postnummer": "6514", "kommune": "KRISTIANSUND", "kommunenummer": "1505", "land": |
| REGISTER | roles | last_changed=2023-06-01, name=Mohammed Ibrahim Fattah, role=Daglig leder, role_code=DAGL; last_changed=2023-06-01, name=Mohammed Ibrahim Fattah, role=Styrets le | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298/roller | Daglig leder: Mohammed Ibrahim Fattah; Styrets leder: Mohammed Ibrahim Fattah |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/914859298 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=KRISTIANSUND N, country=Norge, municipality=KRISTIANSUND, municipality_number=1505, postcode=6511, street=Wilhelm Dalls vei 50, nace=47.110, name=K | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=914859298&size=100 | 980904431 KNUTEPUNKTET NAMO AS |

## JABO HOLDING AS — 916980884

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/916980884>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.total_assets | amount=10007828.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/916980884 | eiendeler.sumEiendeler=10007828.0 |
| REGISTER | founded | 2016-03-15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | stiftelsesdato="2016-03-15" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | JABO HOLDING AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | navn="JABO HOLDING AS" |
| REGISTER | nace | code=64.323, description=Andre egeninvesteringsselskaper | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | naeringskode1.kode="64.323" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (jaboholding.no does not exist or is unreachable; j | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0265, street=Elisenbergveien 15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | forretningsadresse={"adresse": ["Elisenbergveien 15"], "poststed": "OSLO", "postnummer": "0265", "kommune": "OSLO", "kommunenummer": "0301", "land": "Norge", "l |
| REGISTER | roles | last_changed=2016-04-07, name=Jan Leif Bodd, role=Daglig leder, role_code=DAGL; last_changed=2016-04-07, name=Tone Mette Kittelsen Bodd, role=Styremedlem, role_ | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884/roller | Daglig leder: Jan Leif Bodd; Styremedlem: Tone Mette Kittelsen Bodd; Styrets leder: Jan Leif Bodd |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/916980884 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | checked: no registered subunits | 1.0 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=916980884&size=100 | checked: no registered subunits |

## ATLANT ENTREPRENØR AS — 918270116

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/918270116>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | post@atlant-entreprenor.no | 0.85 | https://atlant-entreprenor.no/kontakt-oss/ | post@atlant-entreprenor.no |
| WEB | contact_email_2 | haavard@atlant-entreprenor.no | 0.85 | https://atlant-entreprenor.no/kontakt-oss/ | haavard@atlant-entreprenor.no |
| WEB | contact_email_3 | michal@atlant-entreprenor.no | 0.85 | https://atlant-entreprenor.no/kontakt-oss/ | michal@atlant-entreprenor.no |
| WEB | contact_phone_1 | +47 33 33 29 63 | 0.85 | https://atlant-entreprenor.no/kontakt-oss/ | +47 33 33 29 63 |
| WEB | contact_phone_2 | 905 36 975 | 0.85 | https://atlant-entreprenor.no/kontakt-oss/ | Mobil: 905 36 975 |
| REGISTER | employees | 15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | antallAnsatte=15 |
| REGISTER | financials.revenue | amount=65460663.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/918270116 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=65460663.0 |
| REGISTER | financials.total_assets | amount=25682894.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/918270116 | eiendeler.sumEiendeler=25682894.0 |
| REGISTER | founded | 2016-12-02 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | stiftelsesdato="2016-12-02" |
| WEB | latest_activity_date | 2024-08-27 | 0.9 | https://atlant-entreprenor.no/feed/ | <height>32</height> </image>  	<item> 		<title>Vettre Skole –  Ombygging og tilbygg</title> 		<link>https://atlant-entreprenor.no/vettre-skole-ombygging-og-tilb |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | ATLANT ENTREPRENØR AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | navn="ATLANT ENTREPRENØR AS" |
| REGISTER | nace | code=41.000, description=Oppføring av bygninger | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | naeringskode1.kode="41.000" |
| WEB | official_website | https://atlant-entreprenor.no/ | 0.95 | https://atlant-entreprenor.no/kontakt-oss/ | 63 E-post post@atlant-entreprenor.no Besøks- / Postadresse Velleveien 70, 3118 Tønsberg Haavard Høie Daglig leder Mobil: 905 36 975 |
| WEB | public_activity | date=2024-08-27, date_text=Tue, 27 Aug 2024 12:51:34 +0000, title=Vettre Skole –  Ombygging og tilbygg, url=https://atlant-entreprenor.no/vettre-skole-ombygging | 0.9 | https://atlant-entreprenor.no/feed/ | <height>32</height> </image>  	<item> 		<title>Vettre Skole –  Ombygging og tilbygg</title> 		<link>https://atlant-entreprenor.no/vettre-skole-ombygging-og-tilb |
| REGISTER | registered_address | city=TØNSBERG, country=Norge, municipality=TØNSBERG, municipality_number=3905, postcode=3118, street=Velleveien 70 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | forretningsadresse={"adresse": ["Velleveien 70"], "poststed": "TØNSBERG", "postnummer": "3118", "kommune": "TØNSBERG", "kommunenummer": "3905", "land": "Norge", |
| REGISTER | roles | last_changed=2017-02-07, name=Haavard Høie, role=Daglig leder, role_code=DAGL; last_changed=2022-10-10, name=Ola Blom, role=Styremedlem, role_code=MEDL; last_ch | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116/roller | Daglig leder: Haavard Høie; Styremedlem: Ola Blom; Styremedlem: Vidar Kristoffersen; Styrets leder: Haavard Høie |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/918270116 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | Atlant Entreprenør utfører alle typer byggeoppdrag for private og offentlige oppdragsgivere i Vestfold. Vi kan vise til bred portefølje. | 0.85 | https://atlant-entreprenor.no/ | Atlant Entreprenør utfører alle typer byggeoppdrag for private og offentlige oppdragsgivere i Vestfold. Vi kan vise til bred portefølje. |
| REGISTER | workplaces | address=city=TØNSBERG, country=Norge, municipality=TØNSBERG, municipality_number=3905, postcode=3118, street=Velleveien 70, employees=15, nace=41.000, name=ATLA | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=918270116&size=100 | 919299509 ATLANT ENTREPENØR AS |

## VINTERDALEN AS — 921486332

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/921486332>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | bes@vinterdalen.no | 0.85 | https://vinterdalen.no/om-oss | E: bes@vinterdalen.no |
| WEB | contact_phone_1 | 92 99 46 59 | 0.85 | https://vinterdalen.no/om-oss | T: 92 99 46 59 |
| WEB | contact_phone_2 | 92994650 | 0.85 | https://vinterdalen.no/kontakt | 92994650 |
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=50000.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/921486332 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=50000.0 |
| REGISTER | financials.total_assets | amount=213644.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/921486332 | eiendeler.sumEiendeler=213644.0 |
| REGISTER | founded | 2018-09-18 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | stiftelsesdato="2018-09-18" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | VINTERDALEN AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | navn="VINTERDALEN AS" |
| REGISTER | nace | code=47.810, description=Detaljhandel med motorvogner | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | naeringskode1.kode="47.810" |
| WEB | official_website | https://vinterdalen.no/ | 0.95 | https://vinterdalen.no/kontakt | efon 92994650 E-post bes@vinterdalen.no Adresse Vinterdalen Soleng 5 9146 Olderdalen ÅPNINGSTID Copyright 2023 © VINTERDALEN AS |
| REGISTER | registered_address | city=OLDERDALEN, country=Norge, municipality=KÅFJORD, municipality_number=5540, postcode=9146, street=Soleng 5 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | forretningsadresse={"adresse": ["Soleng 5"], "poststed": "OLDERDALEN", "postnummer": "9146", "kommune": "KÅFJORD", "kommunenummer": "5540", "land": "Norge", "la |
| REGISTER | roles | last_changed=2018-10-02, name=Bjørn-Even Salamonsen, role=Styrets leder, role_code=LEDE | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332/roller | Styrets leder: Bjørn-Even Salamonsen |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921486332 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=OLDERDALEN, country=Norge, municipality=KÅFJORD, municipality_number=5540, postcode=9146, street=Soleng 5, nace=47.810, name=VINTERDALEN AS, organi | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=921486332&size=100 | 933045196 VINTERDALEN AS |

## SSE HOLDING AS — 921724845

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/921724845>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=0.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/921724845 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=0.0 |
| REGISTER | financials.total_assets | amount=53439.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/921724845 | eiendeler.sumEiendeler=53439.0 |
| REGISTER | founded | 2018-10-03 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | stiftelsesdato="2018-10-03" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | SSE HOLDING AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | navn="SSE HOLDING AS" |
| REGISTER | nace | code=64.323, description=Andre egeninvesteringsselskaper | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | naeringskode1.kode="64.323" |
| REGISTER | registered_address | city=LARVIK, country=Norge, municipality=LARVIK, municipality_number=3909, postcode=3271, street=Faret 22 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | forretningsadresse={"adresse": ["Faret 22"], "poststed": "LARVIK", "postnummer": "3271", "kommune": "LARVIK", "kommunenummer": "3909", "land": "Norge", "landkod |
| REGISTER | roles | last_changed=2026-02-02, name=Jarle Svendsen, role=Daglig leder, role_code=DAGL; last_changed=2026-02-02, name=Bjørn Svanberg, role=Styrets leder, role_code=LED | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845/roller | Daglig leder: Jarle Svendsen; Styrets leder: Bjørn Svanberg |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/921724845 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | checked: no registered subunits | 1.0 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=921724845&size=100 | checked: no registered subunits |

## SPEKEMAT AS — 922149348

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/922149348>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | financials.revenue | amount=4869122.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/922149348 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=4869122.0 |
| REGISTER | financials.total_assets | amount=1636720.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/922149348 | eiendeler.sumEiendeler=1636720.0 |
| REGISTER | founded | 2019-01-21 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348 | stiftelsesdato="2019-01-21" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | SPEKEMAT AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348 | navn="SPEKEMAT AS" |
| REGISTER | nace | code=10.130, description=Produksjon av kjøtt- og fjørfevarer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348 | naeringskode1.kode="10.130" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (spekemat.no does not exist or is unreachable; spek | 1.0 |  |  |
| REGISTER | registered_address | city=REKDAL, country=Norge, municipality=VESTNES, municipality_number=1535, postcode=6395, street=Rekdalsvegen 140 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348 | forretningsadresse={"adresse": ["Rekdalsvegen 140"], "poststed": "REKDAL", "postnummer": "6395", "kommune": "VESTNES", "kommunenummer": "1535", "land": "Norge", |
| REGISTER | roles | last_changed=2019-02-01, name=Raimo Heinonen, role=Daglig leder, role_code=DAGL; last_changed=2019-02-01, name=Raimo Heinonen, role=Styrets leder, role_code=LED | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348/roller | Daglig leder: Raimo Heinonen; Styrets leder: Raimo Heinonen |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/922149348 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=REKDAL, country=Norge, municipality=VESTNES, municipality_number=1535, postcode=6395, street=Rekdalsvegen 140, nace=10.130, name=SPEKEMAT AS, organ | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=922149348&size=100 | 822180582 SPEKEMAT AS |

## JR OLSEN CONSULT AS — 925702455

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/925702455>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | financials.revenue | amount=3025839.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/925702455 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=3025839.0 |
| REGISTER | financials.total_assets | amount=1994333.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/925702455 | eiendeler.sumEiendeler=1994333.0 |
| REGISTER | founded | 2020-09-08 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455 | stiftelsesdato="2020-09-08" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | JR OLSEN CONSULT AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455 | navn="JR OLSEN CONSULT AS" |
| REGISTER | nace | code=62.200, description=Konsulentvirksomhet tilknyttet informasjonsteknologi og forvaltning og drift av it-systemer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455 | naeringskode1.kode="62.200" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (jrolsenconsult.no does not exist or is unreachable | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0198, street=Strandhaugen 4 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455 | forretningsadresse={"adresse": ["Strandhaugen 4"], "poststed": "OSLO", "postnummer": "0198", "kommune": "OSLO", "kommunenummer": "0301", "land": "Norge", "landk |
| REGISTER | roles | last_changed=2020-09-25, name=Jan Rainer Olsen, role=Styrets leder, role_code=LEDE | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455/roller | Styrets leder: Jan Rainer Olsen |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/925702455 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0198, street=Strandhaugen 4, nace=62.200, name=JR OLSEN CONSULT AS, orga | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=925702455&size=100 | 925717789 JR OLSEN CONSULT AS |

## NESHEIMSTUNET AS — 927263017

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/927263017>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | post@nesheimstunet.no | 0.85 | https://nesheimstunet.no/ | post@nesheimstunet.no |
| WEB | contact_phone_1 | +47 924 61 223 | 0.85 | https://nesheimstunet.no/ | +47 924 61 223 |
| REGISTER | employees | 20 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | antallAnsatte=20 |
| REGISTER | financials.revenue | amount=2527666.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/927263017 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=2527666.0 |
| REGISTER | financials.total_assets | amount=985402.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/927263017 | eiendeler.sumEiendeler=985402.0 |
| REGISTER | founded | 2021-04-30 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | stiftelsesdato="2021-04-30" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | NESHEIMSTUNET AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | navn="NESHEIMSTUNET AS" |
| REGISTER | nace | code=55.100, description=Drift av hoteller | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | naeringskode1.kode="55.100" |
| WEB | official_website | https://nesheimstunet.no/ | 0.95 | https://nesheimstunet.no/ | til å se deg! Bestill nå Her finner du oss!  Nesheimstunet Saudavegen 7194 5578 Nedre Vats, Norge  +47 924 61 223  post@nesheimstune |
| REGISTER | registered_address | city=NEDRE VATS, country=Norge, municipality=VINDAFJORD, municipality_number=1160, postcode=5578, street=Saudavegen 7194 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | forretningsadresse={"adresse": ["Saudavegen 7194"], "poststed": "NEDRE VATS", "postnummer": "5578", "kommune": "VINDAFJORD", "kommunenummer": "1160", "land": "N |
| REGISTER | roles | last_changed=2021-06-15, name=Bjørn Steinar Nesheim, role=Styrets leder, role_code=LEDE | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017/roller | Styrets leder: Bjørn Steinar Nesheim |
| WEB | social_facebook | https://www.facebook.com/p/Nesheimstunet-100057054986782/ | 0.85 | https://nesheimstunet.no/ | https://www.facebook.com/p/Nesheimstunet-100057054986782/ |
| WEB | social_instagram | https://www.instagram.com/Nesheimstunet/ | 0.85 | https://nesheimstunet.no/ | https://www.instagram.com/Nesheimstunet/ |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/927263017 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | Vi leier ut til bryllup, selskaper, møter, etc. og har konserter flere ganger i året. Vi har 18 senger fordelt på 8 rom og serverer kortreist, hjemmelaget mat | 0.85 | https://nesheimstunet.no/ | Vi leier ut til bryllup, selskaper, møter, etc. og har konserter flere ganger i året. Vi har 18 senger fordelt på 8 rom og serverer kortreist, hjemmelaget mat |
| REGISTER | workplaces | address=city=NEDRE VATS, country=Norge, municipality=VINDAFJORD, municipality_number=1160, postcode=5578, street=Saudavegen 7194, employees=20, nace=55.100, nam | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=927263017&size=100 | 919752483 NESHEIMTUNET AS |

## BARCODE 104 AS — 928124835

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/928124835>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=13375225.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/928124835 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=13375225.0 |
| REGISTER | financials.total_assets | amount=223893469.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/928124835 | eiendeler.sumEiendeler=223893469.0 |
| REGISTER | founded | 2021-09-20 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | stiftelsesdato="2021-09-20" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | BARCODE 104 AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | navn="BARCODE 104 AS" |
| REGISTER | nace | code=68.200, description=Utleie av egen eller leid fast eiendom | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | naeringskode1.kode="68.200" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (barcode104.no does not exist or is unreachable; ba | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0250, street=c/o Malling & Co Forvaltning AS, Dronning Mauds gate 15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | forretningsadresse={"adresse": ["c/o Malling & Co Forvaltning AS", "Dronning Mauds gate 15"], "poststed": "OSLO", "postnummer": "0250", "kommune": "OSLO", "komm |
| REGISTER | roles | last_changed=2026-06-22, name=Jonas Rosenlund, role=Styremedlem, role_code=MEDL; last_changed=2026-06-22, name=Kimberly Adamek Cholewa, role=Styremedlem, role_c | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835/roller | Styremedlem: Jonas Rosenlund; Styremedlem: Kimberly Adamek Cholewa; Styremedlem: Ola M Abdelrahman; Styrets leder: Marius Ekbråten Johansen |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/928124835 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0250, street=c/o Malling & Co Forvaltning AS, Dronning Mauds gate 15, na | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=928124835&size=100 | 928321932 BARCODE 104 AS |

## BRØDRENE SOLEM AS — 930274585

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/930274585>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | elin@brodrenesolem.no | 0.85 | https://brodrenesolem.no/ | Mail: elin@brodrenesolem.no |
| WEB | contact_phone_1 | 32 87 75 00 | 0.85 | https://brodrenesolem.no/ | TELEFON 32 87 75 00 |
| WEB | contact_phone_2 | 934 84 577 | 0.85 | https://brodrenesolem.no/ | Tlf: 934 84 577 |
| REGISTER | employees | 5 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | antallAnsatte=5 |
| REGISTER | financials.revenue | amount=10143045.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/930274585 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=10143045.0 |
| REGISTER | financials.total_assets | amount=10241184.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/930274585 | eiendeler.sumEiendeler=10241184.0 |
| REGISTER | founded | 1979-01-01 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | stiftelsesdato="1979-01-01" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | BRØDRENE SOLEM AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | navn="BRØDRENE SOLEM AS" |
| REGISTER | nace | code=43.120, description=Grunnarbeid | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | naeringskode1.kode="43.120" |
| WEB | official_website | https://brodrenesolem.no/ | 1.0 | https://brodrenesolem.no/ | ne Solem AS 3055 Krokstadelva Telefon 32 87 75 00 Org. nr.: 930 274 585 MVA Kontoransvarlig Elin Solem Tlf: 934 84 577 Mail: elin@b |
| REGISTER | registered_address | city=KROKSTADELVA, country=Norge, municipality=DRAMMEN, municipality_number=3301, postcode=3055, street=Krokstad Industriområde | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | forretningsadresse={"adresse": ["Krokstad Industriområde"], "poststed": "KROKSTADELVA", "postnummer": "3055", "kommune": "DRAMMEN", "kommunenummer": "3301", "la |
| REGISTER | roles | last_changed=2009-04-06, name=Tormod Solem, role=Daglig leder, role_code=DAGL; last_changed=2018-04-04, name=Tormod Solem, role=Styremedlem, role_code=MEDL; las | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585/roller | Daglig leder: Tormod Solem; Styremedlem: Tormod Solem; Styrets leder: Elin Marie Solem |
| WEB | social_facebook | https://www.facebook.com/Br%C3%B8drene-Solem-As-526299460812034/ | 0.85 | https://brodrenesolem.no/ | https://www.facebook.com/Br%C3%B8drene-Solem-As-526299460812034/?fref=ts |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/930274585 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=KROKSTADELVA, country=Norge, municipality=DRAMMEN, municipality_number=3301, postcode=3055, street=Krokstad Industriområde, employees=5, nace=43.12 | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=930274585&size=100 | 971828706 SOLEM BRØDRENE AS |

## EVENTYR SJOKOLADE AS — 931741586

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/931741586>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | careers_page | kind=company_page, url=https://www.eventyr.no/ledige-stillinger | 0.9 | https://www.eventyr.no/ | https://www.eventyr.no/ledige-stillinger |
| WEB | contact_email_1 | POST@EVENTYR.NO | 0.85 | https://www.eventyr.no/ | EVENTYR SJOKOLADE AS • OLAV TRYGGVASONS GATE 28, 7011 TRONDHEIM • POST@EVENTYR.NO • TLF 930 91 264 |
| WEB | contact_phone_1 | 930 91 264 | 0.85 | https://www.eventyr.no/ | EVENTYR SJOKOLADE AS • OLAV TRYGGVASONS GATE 28, 7011 TRONDHEIM • POST@EVENTYR.NO • TLF 930 91 264 |
| REGISTER | financials.revenue | amount=1510076.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/931741586 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=1510076.0 |
| REGISTER | financials.total_assets | amount=479968.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/931741586 | eiendeler.sumEiendeler=479968.0 |
| REGISTER | founded | 2023-05-14 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586 | stiftelsesdato="2023-05-14" |
| WEB | hiring_status | no_open_positions | 0.85 | https://www.eventyr.no/ledige-stillinger | Per nå har vi dessverre ingen ledige stillinger tilgjengelige. Vi oppfordrer deg til å sjekke tilbake jevnlig, da vi vil annonsere eventuelle nye stillinger her |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | EVENTYR SJOKOLADE AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586 | navn="EVENTYR SJOKOLADE AS" |
| REGISTER | nace | code=10.820, description=Produksjon av kakao, sjokolade og sukkervarer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586 | naeringskode1.kode="10.820" |
| WEB | official_website | https://www.eventyr.no/ | 0.95 | https://www.eventyr.no/ | FAQ \| HER KAN DU KJØPE VÅR SJOKOLADE EVENTYR SJOKOLADE AS • OLAV TRYGGVASONS GATE 28, 7011 TRONDHEIM • POST@EVENTYR.NO • TLF 930 91 264 EVENTYR |
| WEB | open_positions | the careers page states there are no open positions | 1.0 | https://www.eventyr.no/ledige-stillinger | the careers page states there are no open positions |
| REGISTER | registered_address | city=TRONDHEIM, country=Norge, municipality=TRONDHEIM, municipality_number=5001, postcode=7011, street=Olav Tryggvasons gate 28 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586 | forretningsadresse={"adresse": ["Olav Tryggvasons gate 28"], "poststed": "TRONDHEIM", "postnummer": "7011", "kommune": "TRONDHEIM", "kommunenummer": "5001", "la |
| REGISTER | roles | last_changed=2026-06-18, name=Aleksander Aurstad Olsen, role=Daglig leder, role_code=DAGL; last_changed=2023-07-19, name=Aleksander Aurstad Olsen, role=Styremed | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586/roller | Daglig leder: Aleksander Aurstad Olsen; Styremedlem: Aleksander Aurstad Olsen; Styremedlem: Håvard Lehn; Styremedlem: Odin Johansen; Styrets leder: Ole-Kjetil L |
| WEB | social_instagram | https://www.instagram.com/eventyrsjokolade/ | 0.85 | https://www.eventyr.no/ | https://www.instagram.com/eventyrsjokolade/ |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931741586 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=TRONDHEIM, country=Norge, municipality=TRONDHEIM, municipality_number=5001, postcode=7011, street=Olav Tryggvasons gate 28, nace=10.820, name=EVENT | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=931741586&size=100 | 931886231 EVENTYR SJOKOLADE AS |

## CROSSFUNCTIONAL AS — 931846280

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/931846280>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=0.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/931846280 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=0.0 |
| REGISTER | financials.total_assets | amount=23245.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/931846280 | eiendeler.sumEiendeler=23245.0 |
| REGISTER | founded | 2023-07-14 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | stiftelsesdato="2023-07-14" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | CROSSFUNCTIONAL AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | navn="CROSSFUNCTIONAL AS" |
| REGISTER | nace | code=62.200, description=Konsulentvirksomhet tilknyttet informasjonsteknologi og forvaltning og drift av it-systemer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | naeringskode1.kode="62.200" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (crossfunctional.no does not exist or is unreachabl | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0276, street=Bruksenhetsnummer H0302, Skøyen terrasse 24 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | forretningsadresse={"adresse": ["Bruksenhetsnummer H0302", "Skøyen terrasse 24"], "poststed": "OSLO", "postnummer": "0276", "kommune": "OSLO", "kommunenummer":  |
| REGISTER | roles | last_changed=2023-08-07, name=Espen Abrahamsen, role=Daglig leder, role_code=DAGL; last_changed=2023-08-07, name=Espen Abrahamsen, role=Styrets leder, role_code | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280/roller | Daglig leder: Espen Abrahamsen; Styrets leder: Espen Abrahamsen |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/931846280 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | checked: no registered subunits | 1.0 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=931846280&size=100 | checked: no registered subunits |

## HITRA TØMRERTEAM AS — 933037991

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/933037991>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | financials.revenue | amount=4913199.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/933037991 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=4913199.0 |
| REGISTER | financials.total_assets | amount=1534984.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/933037991 | eiendeler.sumEiendeler=1534984.0 |
| REGISTER | founded | 2024-01-26 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991 | stiftelsesdato="2024-01-26" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | HITRA TØMRERTEAM AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991 | navn="HITRA TØMRERTEAM AS" |
| REGISTER | nace | code=41.000, description=Oppføring av bygninger | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991 | naeringskode1.kode="41.000" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (hitratomrerteam.no does not exist or is unreachabl | 1.0 |  |  |
| REGISTER | registered_address | city=MELANDSJØ, country=Norge, municipality=HITRA, municipality_number=5056, postcode=7250, street=Svenesveien 1 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991 | forretningsadresse={"adresse": ["Svenesveien 1"], "poststed": "MELANDSJØ", "postnummer": "7250", "kommune": "HITRA", "kommunenummer": "5056", "land": "Norge", " |
| REGISTER | roles | last_changed=2024-02-20, name=Nils Jacob Berg Kjølsø, role=Daglig leder, role_code=DAGL; last_changed=2024-02-20, name=Nils Jacob Berg Kjølsø, role=Styremedlem, | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991/roller | Daglig leder: Nils Jacob Berg Kjølsø; Styremedlem: Nils Jacob Berg Kjølsø; Styrets leder: Rune Lossius |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933037991 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=MELANDSJØ, country=Norge, municipality=HITRA, municipality_number=5056, postcode=7250, street=Svenesveien 1, nace=41.000, name=HITRA TØMRERTEAM AS, | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=933037991&size=100 | 933075427 HITRA TØMRERTEAM AS |

## NY-HEIM BYGG AS — 933293440

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/933293440>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | financials.revenue | amount=1072757.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/933293440 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=1072757.0 |
| REGISTER | financials.total_assets | amount=129714.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/933293440 | eiendeler.sumEiendeler=129714.0 |
| REGISTER | founded | 2024-03-18 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440 | stiftelsesdato="2024-03-18" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | NY-HEIM BYGG AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440 | navn="NY-HEIM BYGG AS" |
| REGISTER | nace | code=43.320, description=Snekkerarbeid | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440 | naeringskode1.kode="43.320" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (nyheimbygg.no does not mention the company; ny-hei | 1.0 |  |  |
| REGISTER | registered_address | city=BODØ, country=Norge, municipality=BODØ, municipality_number=1804, postcode=8005, street=Prinsens gate 102 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440 | forretningsadresse={"adresse": ["Prinsens gate 102"], "poststed": "BODØ", "postnummer": "8005", "kommune": "BODØ", "kommunenummer": "1804", "land": "Norge", "la |
| REGISTER | roles | last_changed=2024-04-13, name=Andrei Cosmin Nyheim, role=Daglig leder, role_code=DAGL; last_changed=2024-04-13, name=Andrei Cosmin Nyheim, role=Styrets leder, r | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440/roller | Daglig leder: Andrei Cosmin Nyheim; Styrets leder: Andrei Cosmin Nyheim |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/933293440 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=BODØ, country=Norge, municipality=BODØ, municipality_number=1804, postcode=8005, street=Prinsens gate 102, nace=43.320, name=NY-HEIM BYGG AS, organ | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=933293440&size=100 | 933316238 NY-HEIM BYGG AS |

## BLEND SALONG AS — 934347684

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/934347684>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | blendsalong@hotmail.com | 0.85 | https://blendsalong.no/ | blendsalong@hotmail.com |
| WEB | contact_phone_1 | 78430666 | 0.85 | https://blendsalong.no/ | 78430666 |
| REGISTER | financials.revenue | amount=1545163.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/934347684 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=1545163.0 |
| REGISTER | financials.total_assets | amount=1001195.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/934347684 | eiendeler.sumEiendeler=1001195.0 |
| REGISTER | founded | 2024-11-22 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684 | stiftelsesdato="2024-11-22" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | BLEND SALONG AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684 | navn="BLEND SALONG AS" |
| REGISTER | nace | code=96.210, description=Frisering og barbering | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684 | naeringskode1.kode="96.210" |
| WEB | official_website | https://blendsalong.no/ | 1.0 | https://blendsalong.no/ | ien 51 B 9510 Alta 78430666 blendsalong@hotmail.com Org.nr: 934347684 Personvernerklæring · Informasjonskapsler Åpningstider Man |
| REGISTER | registered_address | city=ALTA, country=Norge, municipality=ALTA, municipality_number=5601, postcode=9510, street=Løkkeveien 51B | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684 | forretningsadresse={"adresse": ["Løkkeveien 51B"], "poststed": "ALTA", "postnummer": "9510", "kommune": "ALTA", "kommunenummer": "5601", "land": "Norge", "landk |
| REGISTER | roles | last_changed=2024-11-27, name=Lilly-Marlén Antonsen, role=Styrets leder, role_code=LEDE | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684/roller | Styrets leder: Lilly-Marlén Antonsen |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/934347684 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | Velkommen til Blend Salong AS. Bestill time enkelt online og la oss ta vare på deg. | 0.85 | https://blendsalong.no/ | Velkommen til Blend Salong AS. Bestill time enkelt online og la oss ta vare på deg. |
| REGISTER | workplaces | address=city=ALTA, country=Norge, municipality=ALTA, municipality_number=5601, postcode=9510, street=Løkkeveien 51B, nace=96.210, name=BLEND SALONG AS, organisa | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=934347684&size=100 | 934579291 BLEND SALONG AS |

## UNFORGETTABLE AS — 935547113

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/935547113>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | julijana@unforgettable.no | 0.85 | https://unforgettable.no/about | julijana@unforgettable.no |
| WEB | contact_phone_1 | +47 91 37 60 10 | 0.85 | https://unforgettable.no/about | +47 91 37 60 10 |
| REGISTER | financials.revenue | amount=110920.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/935547113 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=110920.0 |
| REGISTER | financials.total_assets | amount=1824539.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/935547113 | eiendeler.sumEiendeler=1824539.0 |
| REGISTER | founded | 2025-05-15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113 | stiftelsesdato="2025-05-15" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | UNFORGETTABLE AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113 | navn="UNFORGETTABLE AS" |
| REGISTER | nace | code=79.902, description=Guide- og reiseledervirksomhet | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113 | naeringskode1.kode="79.902" |
| WEB | official_website | https://unforgettable.no/ | 0.95 | https://unforgettable.no/ | type":"WebSite"} {"legalName":"Unforgettable AS","address":"Kavringen brygge 1\n0252 Oslo\nNorway","email":"julijana@unforgettable.no","te |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0252, street=Kavringen brygge 1 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113 | forretningsadresse={"adresse": ["Kavringen brygge 1"], "poststed": "OSLO", "postnummer": "0252", "kommune": "OSLO", "kommunenummer": "0301", "land": "Norge", "l |
| REGISTER | roles | last_changed=2025-05-22, name=Julijana Damcevska, role=Daglig leder, role_code=DAGL; last_changed=2025-12-11, name=Alexander Risøy, role=Styremedlem, role_code= | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113/roller | Daglig leder: Julijana Damcevska; Styremedlem: Alexander Risøy; Styrets leder: Julijana Damcevska |
| WEB | social_instagram | http://instagram.com/unforgettable.no | 0.85 | https://unforgettable.no/ | http://instagram.com/unforgettable.no |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/935547113 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | Discover North Macedonia's rich culture and vibrant wine scene with guided tours in September 2025. Join us for an unforgettable cultural and wine journey. | 0.85 | https://unforgettable.no/ | Discover North Macedonia's rich culture and vibrant wine scene with guided tours in September 2025. Join us for an unforgettable cultural and wine journey. |
| REGISTER | workplaces | address=city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0252, street=Kavringen brygge 1, nace=79.902, name=UNFORGETTABLE AS, org | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=935547113&size=100 | 935574455 UNFORGETTABLE AS |

## GAVETIL AS — 936155650

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/936155650>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | hello@gavetil.no | 0.85 | https://www.gavetil.no/policies/contact-information | Epost: hello@gavetil.no |
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=0.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/936155650 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=0.0 |
| REGISTER | financials.total_assets | amount=8720.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/936155650 | eiendeler.sumEiendeler=8720.0 |
| REGISTER | founded | 2025-08-30 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | stiftelsesdato="2025-08-30" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | GAVETIL AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | navn="GAVETIL AS" |
| REGISTER | nace | code=47.780, description=Annen detaljhandel med andre nye varer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | naeringskode1.kode="47.780" |
| WEB | official_website | https://www.gavetil.no/ | 1.0 | https://www.gavetil.no/policies/contact-information | em KONTAKTINFORMASJON Kontaktinformasjon Gavetil AS Org.nr: 936155650 Epost: hello@gavetil.no Adresse: Øsbyfaret 31, Oslo Om Gave |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0687, street=Østbyfaret 31B | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | forretningsadresse={"adresse": ["Østbyfaret 31B"], "poststed": "OSLO", "postnummer": "0687", "kommune": "OSLO", "kommunenummer": "0301", "land": "Norge", "landk |
| REGISTER | roles | last_changed=2025-09-12, name=Andressa Pinheiro Gomes, role=Daglig leder, role_code=DAGL; last_changed=2025-09-12, name=Andressa Pinheiro Gomes, role=Styremedle | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650/roller | Daglig leder: Andressa Pinheiro Gomes; Styremedlem: Andressa Pinheiro Gomes; Styrets leder: Jørgen Kielland Gran |
| WEB | social_instagram | https://www.instagram.com/gavetil.no | 0.85 | https://www.gavetil.no/ | https://www.instagram.com/gavetil.no |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936155650 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | Send en gjennomtenkt gave direkte til mottaker. Gaveesker pakket for hånd, med personlig hilsen og levering i hele Norge. | 0.85 | https://www.gavetil.no/ | Send en gjennomtenkt gave direkte til mottaker. Gaveesker pakket for hånd, med personlig hilsen og levering i hele Norge. |
| REGISTER | workplaces | address=city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0687, street=Østbyfaret 31B, nace=47.780, name=GAVETIL AS, organisation_ | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=936155650&size=100 | 936175295 GAVETIL AS |

## MEDICVISION OPTIKK AS — 936245749

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/936245749>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | Rolf@medicvision.no | 0.85 | https://medicvision.no/ | Rolf@medicvision.no |
| WEB | contact_phone_1 | +47 909 38 038 | 0.85 | https://medicvision.no/ | +47 909 38 038 |
| WEB | contact_phone_2 | +47 370 33 100 | 0.85 | https://medicvision.no/ | +47 370 33 100 |
| REGISTER | financials.revenue | amount=1134911.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/936245749 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=1134911.0 |
| REGISTER | financials.total_assets | amount=2689769.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/936245749 | eiendeler.sumEiendeler=2689769.0 |
| REGISTER | founded | 2025-09-16 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749 | stiftelsesdato="2025-09-16" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | MEDICVISION OPTIKK AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749 | navn="MEDICVISION OPTIKK AS" |
| REGISTER | nace | code=47.920, description=Formidlingstjenester tilknyttet detaljhandel med spesialisert vareutvalg | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749 | naeringskode1.kode="47.920" |
| WEB | official_website | https://medicvision.no/ | 1.0 | https://medicvision.no/ | lue",           "propertyID": "Org.nr",           "value": "936245749"         }       ],       "address": {         "@type": "Po |
| REGISTER | registered_address | city=ARENDAL, country=Norge, municipality=ARENDAL, municipality_number=4203, postcode=4838, street=Parkveien 4 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749 | forretningsadresse={"adresse": ["Parkveien 4"], "poststed": "ARENDAL", "postnummer": "4838", "kommune": "ARENDAL", "kommunenummer": "4203", "land": "Norge", "la |
| REGISTER | roles | last_changed=2025-10-06, name=Kenneth Vik Lund, role=Daglig leder, role_code=DAGL; last_changed=2025-10-30, name=Kenneth Vik Lund, role=Styrets leder, role_code | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749/roller | Daglig leder: Kenneth Vik Lund; Styrets leder: Kenneth Vik Lund |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936245749 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | MedicVision Optikk leverer lupebriller, diagnostiske instrumenter, medisinsk belysning og mikroskoper til øye, allmennmedisin, dental, ØNH og laboratorier. | 0.85 | https://medicvision.no/ | MedicVision Optikk leverer lupebriller, diagnostiske instrumenter, medisinsk belysning og mikroskoper til øye, allmennmedisin, dental, ØNH og laboratorier. |
| REGISTER | workplaces | address=city=ARENDAL, country=Norge, municipality=ARENDAL, municipality_number=4203, postcode=4838, street=Parkveien 4, nace=47.920, name=MEDVICISION OPTIKK AS, | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=936245749&size=100 | 936505562 MEDVICISION OPTIKK AS |

## GRAANUL NORWAY AS — 936761704

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/936761704>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | financials.revenue | amount=0.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/936761704 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=0.0 |
| REGISTER | financials.total_assets | amount=30000.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/936761704 | eiendeler.sumEiendeler=30000.0 |
| REGISTER | founded | 2025-12-05 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704 | stiftelsesdato="2025-12-05" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | GRAANUL NORWAY AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704 | navn="GRAANUL NORWAY AS" |
| REGISTER | nace | code=70.200, description=Bedriftsrådgivning og annen administrativ rådgivning | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704 | naeringskode1.kode="70.200" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (graanulnorway.no does not exist or is unreachable; | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0161, street=Klingenberggata 7 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704 | forretningsadresse={"adresse": ["Klingenberggata 7"], "poststed": "OSLO", "postnummer": "0161", "kommune": "OSLO", "kommunenummer": "0301", "land": "Norge", "la |
| REGISTER | roles | last_changed=2026-03-10, name=Lars Christian Bacher, role=Daglig leder, role_code=DAGL; last_changed=2026-03-10, name=Rain Silivask, role=Styrets leder, role_co | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704/roller | Daglig leder: Lars Christian Bacher; Styrets leder: Rain Silivask |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/936761704 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0161, street=Klingenberggata 7, nace=70.200, name=GRAANUL NORWAY AS, org | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=936761704&size=100 | 937335172 GRAANUL NORWAY AS |

## AUTOPLAN AS — 981038223

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/981038223>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | careers_page | kind=company_page, url=https://www.autoplan.no/ledige-stillinger | 0.9 | https://www.autoplan.no/ | https://www.autoplan.no/ledige-stillinger |
| WEB | contact_email_1 | kundeservice@autoplan.no | 0.85 | https://www.autoplan.no/ | kundeservice@autoplan.no |
| REGISTER | employees | 77 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | antallAnsatte=77 |
| REGISTER | financials.revenue | amount=2542415973.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/981038223 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=2542415973.0 |
| REGISTER | financials.total_assets | amount=1075366888.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/981038223 | eiendeler.sumEiendeler=1075366888.0 |
| REGISTER | founded | 1999-08-30 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | stiftelsesdato="1999-08-30" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | AUTOPLAN AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | navn="AUTOPLAN AS" |
| REGISTER | nace | code=77.110, description=Utleie og leasing av biler og andre lette motorvogner | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | naeringskode1.kode="77.110" |
| WEB | official_website | https://www.autoplan.no/ | 1.0 | https://www.autoplan.no/om-oss | . 2,6 milliarder NOK. 02886 kundeservice@autoplan.no Orgnr: 981 038 223 Hovedkontor Besøksadresse Elgvegen 2, 2340 Løten Postadress |
| REGISTER | registered_address | city=LØTEN, country=Norge, municipality=LØTEN, municipality_number=3412, postcode=2340, street=Elgvegen 2 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | forretningsadresse={"adresse": ["Elgvegen 2"], "poststed": "LØTEN", "postnummer": "2340", "kommune": "LØTEN", "kommunenummer": "3412", "land": "Norge", "landkod |
| REGISTER | roles | last_changed=2023-12-19, name=Kenneth Skjønhaug, role=Daglig leder, role_code=DAGL; last_changed=2024-09-06, name=Christian Nordeng, role=Styremedlem, role_code | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223/roller | Daglig leder: Kenneth Skjønhaug; Styremedlem: Christian Nordeng; Styremedlem: Johanne Oppegaard Sulland; Styremedlem: Kristin Killi Skinlo; Styremedlem: Odd Arv |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/981038223 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| WEB | website_description | Proff-lease fra Autoplan er en komplett løsning som forenkler bilholdet for norske bedrifter og offentlige virksomheter. Leasing har aldri vært enklere. | 0.85 | https://www.autoplan.no/ | Proff-lease fra Autoplan er en komplett løsning som forenkler bilholdet for norske bedrifter og offentlige virksomheter. Leasing har aldri vært enklere. |
| REGISTER | workplaces | address=city=LØTEN, country=Norge, municipality=LØTEN, municipality_number=3412, postcode=2340, street=Elgvegen 2, employees=77, nace=77.110, name=AUTOPLAN AS,  | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=981038223&size=100 | 981046080 AUTOPLAN AS |

## NAVAL INVEST AS — 989008994

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/989008994>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.total_assets | amount=8569576.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/989008994 | eiendeler.sumEiendeler=8569576.0 |
| REGISTER | founded | 2005-12-01 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | stiftelsesdato="2005-12-01" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | NAVAL INVEST AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | navn="NAVAL INVEST AS" |
| REGISTER | nace | code=64.323, description=Andre egeninvesteringsselskaper | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | naeringskode1.kode="64.323" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (navalinvest.no does not exist or is unreachable; n | 1.0 |  |  |
| REGISTER | registered_address | city=RAUDEBERG, country=Norge, municipality=KINN, municipality_number=4602, postcode=6710 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | forretningsadresse={"poststed": "RAUDEBERG", "postnummer": "6710", "kommune": "KINN", "kommunenummer": "4602", "land": "Norge", "landkode": "NO"} |
| REGISTER | roles | last_changed=2026-04-25, name=Stian Kongsvik, role=Daglig leder, role_code=DAGL; last_changed=2026-08-21, name=Stian Kongsvik, role=Styremedlem, role_code=MEDL; | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994/roller | Daglig leder: Stian Kongsvik; Styremedlem: Stian Kongsvik; Styrets leder: Geir Kongsvik |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989008994 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=RAUDEBERG, country=Norge, municipality=KINN, municipality_number=4602, postcode=6710, nace=64.323, name=NAVAL INVEST AS, organisation_number=932282 | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=989008994&size=100 | 932282844 NAVAL INVEST AS |

## SKATTEBO INVEST AS — 989212761

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/989212761>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=0.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/989212761 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=0.0 |
| REGISTER | financials.total_assets | amount=3742936.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/989212761 | eiendeler.sumEiendeler=3742936.0 |
| REGISTER | founded | 2005-12-15 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | stiftelsesdato="2005-12-15" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | SKATTEBO INVEST AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | navn="SKATTEBO INVEST AS" |
| REGISTER | nace | code=42.210, description=Bygging av vann- og kloakkanlegg | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | naeringskode1.kode="42.210" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (skatteboinvest.no does not exist or is unreachable | 1.0 |  |  |
| REGISTER | registered_address | city=LEIRA I VALDRES, country=Norge, municipality=NORD-AURDAL, municipality_number=3451, postcode=2920, street=Kalplassvegen 14 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | forretningsadresse={"adresse": ["Kalplassvegen 14"], "poststed": "LEIRA I VALDRES", "postnummer": "2920", "kommune": "NORD-AURDAL", "kommunenummer": "3451", "la |
| REGISTER | roles | last_changed=2006-02-06, name=Jon Harald Skattebo, role=Daglig leder, role_code=DAGL; last_changed=2023-01-05, name=Henrik Wickstrøm Skattebo, role=Styremedlem, | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761/roller | Daglig leder: Jon Harald Skattebo; Styremedlem: Henrik Wickstrøm Skattebo; Styrets leder: Jon Harald Skattebo |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/989212761 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | checked: no registered subunits | 1.0 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=989212761&size=100 | checked: no registered subunits |

## NORWEGIAN FILM AS — 991698140

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/991698140>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | harRegistrertAntallAnsatte=false | 1.0 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | harRegistrertAntallAnsatte=false |
| REGISTER | financials.revenue | amount=452350.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/991698140 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=452350.0 |
| REGISTER | financials.total_assets | amount=2397156.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/991698140 | eiendeler.sumEiendeler=2397156.0 |
| REGISTER | founded | 2007-09-04 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | stiftelsesdato="2007-09-04" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | NORWEGIAN FILM AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | navn="NORWEGIAN FILM AS" |
| REGISTER | nace | code=82.400, description=Formidlingstjenester tilknyttet forretningsmessig tjenesteyting ikke nevnt annet sted | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | naeringskode1.kode="82.400" |
| WEB | official_website | not published: identity score 0.50 below 0.9 (signals: legal_name); candidate domain built from the legal name, not listed in the register | 0.0 | https://www.norwegianfilm.com/ | not published: identity score 0.50 below 0.9 (signals: legal_name); candidate domain built from the legal name, not listed in the register |
| REGISTER | registered_address | city=SEM, country=Norge, municipality=TØNSBERG, municipality_number=3905, postcode=3170, street=c/o Azets Insight AS, Åshaugveien 68 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | forretningsadresse={"adresse": ["c/o Azets Insight AS", "Åshaugveien 68"], "poststed": "SEM", "postnummer": "3170", "kommune": "TØNSBERG", "kommunenummer": "390 |
| REGISTER | roles | last_changed=2026-04-09, name=John Patrik Borggren, role=Styrets leder, role_code=LEDE | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140/roller | Styrets leder: John Patrik Borggren |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991698140 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=SEM, country=Norge, municipality=TØNSBERG, municipality_number=3905, postcode=3170, street=c/o Azets Insight AS, Åshaugveien 68, nace=82.400, name= | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=991698140&size=100 | 991703837 NORWEGIAN FILM AS |

## GAIA GRUPPEN AS — 991851410

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/991851410>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| REGISTER | employees | 14 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | antallAnsatte=14 |
| REGISTER | financials.revenue | amount=21705995.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/991851410 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=21705995.0 |
| REGISTER | financials.total_assets | amount=82935219.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/991851410 | eiendeler.sumEiendeler=82935219.0 |
| REGISTER | founded | 2007-10-03 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | stiftelsesdato="2007-10-03" |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | GAIA GRUPPEN AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | navn="GAIA GRUPPEN AS" |
| REGISTER | nace | code=46.340, description=Engroshandel med drikkevarer | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | naeringskode1.kode="46.340" |
| WEB | official_website | no website listed in the official register; domain names built from the legal name were tried without result (gaiagruppen.no disallows fetching (robots.txt); ga | 1.0 |  |  |
| REGISTER | registered_address | city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0560, street=Bygning B, Trondheimsveien 2 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | forretningsadresse={"adresse": ["Bygning B", "Trondheimsveien 2"], "poststed": "OSLO", "postnummer": "0560", "kommune": "OSLO", "kommunenummer": "0301", "land": |
| REGISTER | roles | last_changed=2026-06-17, name=Veronica Langjord, role=Daglig leder, role_code=DAGL; last_changed=2025-09-23, name=Christine Rein-Helliesen, role=Styremedlem, ro | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410/roller | Daglig leder: Veronica Langjord; Styremedlem: Christine Rein-Helliesen; Styremedlem: Erik Richard Thrane; Styremedlem: Lars Geir Rein-Helliesen; Styrets leder:  |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/991851410 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=OSLO, country=Norge, municipality=OSLO, municipality_number=0301, postcode=0560, street=Bygning B, Trondheimsveien 2, employees=14, nace=46.340, na | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=991851410&size=100 | 926392913 GAIA GRUPPEN AS |

## SOGN ENTREPRENØR AS — 992106905

Register record: <https://data.brreg.no/enhetsregisteret/api/enheter/992106905>

| layer | field | value | confidence | source | snippet |
|---|---|---|---|---|---|
| WEB | contact_email_1 | post@sognentreprenor.no | 0.85 | https://www.sognentreprenor.no/ | post@sognentreprenor.no |
| WEB | contact_email_2 | post@www.sognentreprenor.no | 0.85 | https://www.sognentreprenor.no/ | post@www.sognentreprenor.no |
| WEB | contact_phone_1 | 970 57 470 | 0.85 | https://www.sognentreprenor.no/ | 970 57 470 |
| REGISTER | employees | 13 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | antallAnsatte=13 |
| REGISTER | financials.revenue | amount=19021623.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/992106905 | resultatregnskapResultat.driftsresultat.driftsinntekter.sumDriftsinntekter=19021623.0 |
| REGISTER | financials.total_assets | amount=8850092.0, currency=NOK | 0.99 | https://data.brreg.no/regnskapsregisteret/regnskap/992106905 | eiendeler.sumEiendeler=8850092.0 |
| REGISTER | founded | 2007-11-11 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | stiftelsesdato="2007-11-11" |
| WEB | latest_activity_date | 2016-02-05 | 0.9 | https://www.sognentreprenor.no/feed/ | <generator>https://wordpress.org/?v=7.1.2</generator> 	<item> 		<title>Treng de nye lokaler?</title> 		<link>https://www.sognentreprenor.no/2016/02/05/treng-de- |
| REGISTER | legal_form | code=AS, description=Aksjeselskap | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | organisasjonsform.kode="AS" |
| REGISTER | legal_name | SOGN ENTREPRENØR AS | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | navn="SOGN ENTREPRENØR AS" |
| REGISTER | nace | code=41.000, description=Oppføring av bygninger | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | naeringskode1.kode="41.000" |
| WEB | official_website | https://www.sognentreprenor.no/ | 0.95 | https://www.sognentreprenor.no/ | esse: Gaupnegrandane, 6868 Gaupne ( sjå kart ) Postadresse: Gaupnegrandane 63, 6868 gaupne Utvalde referansar Me har jobba med mange utfo |
| WEB | public_activity | date=2016-02-05, date_text=Fri, 05 Feb 2016 13:09:48 +0000, title=Treng de nye lokaler?, url=https://www.sognentreprenor.no/2016/02/05/treng-de-nye-lokaler/ | 0.9 | https://www.sognentreprenor.no/feed/ | <generator>https://wordpress.org/?v=7.1.2</generator> 	<item> 		<title>Treng de nye lokaler?</title> 		<link>https://www.sognentreprenor.no/2016/02/05/treng-de- |
| REGISTER | registered_address | city=GAUPNE, country=Norge, municipality=LUSTER, municipality_number=4644, postcode=6868, street=Gaupnegrandane 63 | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | forretningsadresse={"adresse": ["Gaupnegrandane 63"], "poststed": "GAUPNE", "postnummer": "6868", "kommune": "LUSTER", "kommunenummer": "4644", "land": "Norge", |
| REGISTER | roles | last_changed=2015-07-15, name=Rolf Ole Kleiven, role=Daglig leder, role_code=DAGL; last_changed=2020-06-18, name=Rolf Ole Kleiven, role=Styrets leder, role_code | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905/roller | Daglig leder: Rolf Ole Kleiven; Styrets leder: Rolf Ole Kleiven; Varamedlem: Sindre Kleiven |
| REGISTER | status | active | 0.99 | https://data.brreg.no/enhetsregisteret/api/enheter/992106905 | no insolvency/dissolution flags set: {"konkurs": false, "underAvvikling": false, "underTvangsavviklingEllerTvangsopplosning": false} |
| REGISTER | workplaces | address=city=GAUPNE, country=Norge, municipality=LUSTER, municipality_number=4644, postcode=6868, street=Gaupnegrandane 63, employees=13, nace=41.000, name=SOGN | 0.99 | https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=992106905&size=100 | 979501080 SOGN ENTREPRENØR AS |

