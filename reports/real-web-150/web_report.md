# Real-website run report

companies: 150 | listing a website in the register: 150

## official_website outcome (of 150 listing a site)
- ambiguous: 68
- available: 48
- failed: 28
- blocked: 4
- not_available: 2

## why not verified (top reasons)
- 68 x ambiguous: not published
- 14 x failed: website fetch failed: ConnectError
- 6 x failed: website fetch failed: ProxyError
- 4 x blocked: robots.txt disallows fetching the registered website
- 4 x failed: website fetch failed: ConnectTimeout
- 1 x failed: website fetch failed: ReadTimeout
- 1 x not_available: no website listed in the official register; no search-based discovery performed
- 1 x not_available: registered website returned HTTP 404
- 1 x failed: website fetch failed: too_many_redirects
- 1 x failed: website fetch failed: HTTP 503
- 1 x failed: website fetch failed: HTTP 500

## identity signals of the 48 verified sites
- organisation_number: 22
- legal_name+street_address: 15
- legal_name+postcode_city: 4
- legal_name+registered_phone: 3
- organisation_number+legal_name_not_on_page: 2
- legal_name_partial+street_address+postcode_city: 2

## coverage among the 48 verified sites
- website_description: 27
- contact_email_1: 40
- contact_phone_1: 45
- social_linkedin: 8
- social_facebook: 11
- social_instagram: 7
- products_services: 0
- careers_page: 8
- open_positions: 0
- hiring_status: 1
- public_activity: 8
- latest_activity_date: 8
- open_positions states: {'not_available': 47, 'ambiguous': 1}
- public_activity states: {'not_available': 39, 'available': 8, 'ambiguous': 1}
- careers_page states: {'absent': 40, 'available': 8}
- hiring_status values: {'no_open_positions': 1}

## facts dropped by the verifier / guards
- 94 x contact_phone: this page has a block for the company and the contact is not in it
- 90 x contact_email: this page has a block for the company and the contact is not in it
- 14 x contact_email: email domain differs from the site and is not next to the company name
- 5 x contact_email: placeholder, no-reply or invoicing mailbox
- 4 x website_description: contact details, not a description
- 2 x website_description: markup inside the description
- 1 x contact_phone: labelled as an organisation/bank/fax/reference number
- 1 x contact_phone: foreign country code +45

## requests
- website-listing companies: mean 7.6, max 15; verified: mean 8.7

## samples to inspect by hand (verified sites)

### NYERA CONSULTING AS (835989372) -> https://www.nyera.as/
- identity: identity_gate:organisation_number | snippet: 'ost: marie@nyera.as nyera nyera Nyera Consulting AS Org.nr: 835 989 372 nyera nyera'
- contact_email_1: "marie@nyera.as"

### SKEISBOTNEN BARNEHAGE AS (895637912) -> https://www.piba.no/
- identity: identity_gate:legal_name+street_address | snippet: 'rd Dr. Brandts Skeisbotnen Furehaugen Skeisbotnen barnehage Skeisbotnen 58 5217 Hagavik Ruth Nyheim Tel: 93861541 Mail: Ruth@skeisbotn'
- contact_email_1: "Ruth@skeisbotnen.no"
- contact_phone_1: "93861541"
- careers_page: {"kind": "company_page", "url": "https://www.piba.no/jobbe-hos-oss"}

### MØBELSNEKKERSKOLEN AS (898571122) -> https://mobelsnekker.no/
- identity: identity_gate:legal_name+street_address | snippet: 'lefon: 69891227 E-post: post@mobelsnekker.no Besøksadresse: Husflidveien 7, 1850 Mysen Kontakt Fyll ut feltene under, så kontakter vi'
- website_description: "Møbelsnekkerskolen ligger sentralt og vakkert til utenfor Mysen. Du er hjertelig velkommen innom for en prat."
- contact_email_1: "post@mobelsnekker.no"
- contact_phone_1: "69891227"

### KIROPRAKTOR LINDA GÖRANSDOTTER OHREN AS (911598116) -> https://kiropraktor.info/
- identity: identity_gate:legal_name+street_address | snippet: '17:00 Onsdag: 8:00-14:00 ADRESSE Tønsberg Medisinske Senter Kilengaten 18, 3117 Tønsberg Avd. STOKKE. Nygaards alle 4, 3160 Stokke Bo'
- website_description: "Kiropraktor Tønsberg og Stokke. Del av stort tverrfaglig miljø på Tønsberg Medisinske Senter. Oppdaterte erfarne kiropraktorer, medlemmer av Norsk Kiropraktorf
- contact_phone_1: "33376333"
- latest_activity_date: "2025-12-04"
- public_activity: 'Forskningsprosjekt gjennom OUS' 2025-12-04 <https://kiropraktor.info/feed/> snippet: '<height>32</height>\n</image> \n\t<item>\n\t\t<title>Forskningsprosjekt gjennom OUS</title>\n\t\t<link>https://kiropraktor.info/forskningsprosjekt-gj'
- public_activity: 'Styrke-uka 2025' 2025-10-26 <https://kiropraktor.info/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Styrke-uka 2025</title>\n\t\t<link>https://kiropraktor.info/styrkeuka/</link>\n\t\t\n\t\t'
- public_activity: 'Tips for å forebygge knesmerter' 2025-01-29 <https://kiropraktor.info/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Tips for å forebygge knesmerter</title>\n\t\t<link>https://kiropraktor.info/tips-fo'
- public_activity: 'Nakkehodepine – en glemt eller ignorert hodepine?' 2022-05-21 <https://kiropraktor.info/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Nakkehodepine – en glemt eller ignorert hodepine?</title>\n\t\t<link>https://kiropr'

### BYGGA AS (911599236) -> https://bygga.no/
- identity: identity_gate:legal_name+registered_phone | snippet: 'Byggmester i Stavanger - Bygga AS Til Bygga Plissé for Solskjerming og plissé → Hjem Tjeneste'
- website_description: "Den hyggelige byggmesteren i Stavanger. Fagkunnskap i generasjoner. Vi kan bad, bygging, påbygg av hus og renovering av hus."
- contact_email_1: "post@bygga.no"
- contact_phone_1: "51 73 11 73"
- latest_activity_date: "2026-01-29"
- public_activity: 'Plisségardiner på mål i toppleilighet på Lervig Brygge' 2026-01-29 <https://bygga.no/feed/> snippet: '<height>32</height>\n</image> \n\t<item>\n\t\t<title>Plisségardiner på mål i toppleilighet på Lervig Brygge</title>\n\t\t<link>https://bygga.no/pliss'
- public_activity: 'Slik bygger vi våtrom' 2024-10-24 <https://bygga.no/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Slik bygger vi våtrom</title>\n\t\t<link>https://bygga.no/slik-bygger-vi-vatrom/</l'
- public_activity: 'Svart belte i kundetilfredshet' 2024-02-15 <https://bygga.no/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Svart belte i kundetilfredshet</title>\n\t\t<link>https://bygga.no/svart-belte-i-ku'
- public_activity: 'Med spisskompetanse på eldre hus og eiendommer' 2024-02-14 <https://bygga.no/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Med spisskompetanse på eldre hus og eiendommer</title>\n\t\t<link>https://bygga.no/'

### LOFOTEN WOOL & ART AS (914113768) -> https://lofoten-wool.no/
- identity: identity_gate:organisation_number | snippet: 'k Pinterest Instagram YouTube Lofoten Wool & Art AS Org.nr: 914 113 768 Tlf kontor: +47 90 76 50 80 post@lofoten-wool.no LOFOTEN WO'
- website_description: "Ullgarn fra lykkelige sauer. 100% norsk ull fra Norsk kvit sau, Gammelnorsk sau og Spælsau i Lofoten og Nord-Norge. Sauefarget og plantefarget garn. Strikkepak
- contact_email_1: "post@lofoten-wool.no"
- contact_phone_1: "+ 47 90 76 50 80"

### RAKKESTAD SLANGESERVICE AS (915980430) -> https://rakkestad-slangeservice.no/
- identity: identity_gate:legal_name+street_address | snippet: 'r. defaultdefaultdefaultdefaultdefaultdefaultdefaultdefault Bedriftsveien 5 1890 Rakkestad 47 64 52 88 kae@rakkestad-slangeservice.no G'
- website_description: "Kontakt oss i dag for en hyggelig prat - Rakkestad slangeservice"
- contact_email_1: "kae@rakkestad-slangeservice.no"
- contact_phone_1: "47 64 52 88"

### FULLSTAKK MARKETING AS (917220786) -> https://www.fullstakk.no
- identity: identity_gate:organisation_number | snippet: 'Oslo Følg oss I fall du trenger organisasjonsnummeret vårt 917 220 786 Våre tjenester Om oss Artikler Karriere Artikler Kontakt os'
- website_description: "Vi bistår med taktisk rådgiving og operasjonelle spesialister som gjør din digitale markedsføring til en vekstmaskin."
- contact_email_1: "hello@fullstakk.com"
- contact_phone_1: "+47 995 63 145"
- careers_page: {"kind": "company_page", "url": "https://www.fullstakk.no/karriere"}

### SCALA BØ AS (917603510) -> https://www.bosenteret.no/
- identity: identity_gate:organisation_number | snippet: 'redriksborg Eiendom AS Storgata 5 1607 Fredrikstad Org.nr : 917 603 510 Faktura sendes på EHF. Kan du ikke sende faktura på EHF, ta'
- website_description: "Velkommen til Bøsenteret, det pulserende kjøpesenteret som gir deg alt du trenger under ett tak. Midt i hjertet Bø, er Bøsenteret en viktig destinasjon for lok
- contact_email_1: "tove.bringa@bosenteret.no"
- contact_phone_1: "40 40 87 88"
- careers_page: {"kind": "company_page", "url": "https://www.bosenteret.no/jobs"}
- hiring_status: "no_open_positions"

### NORTHERN HIGHLIGHTS AS (920915418) -> https://www.northernhighlights.no/
- identity: identity_gate:organisation_number | snippet: 'otification Contact us 2026 Northern Highlights AS, org.nr: 920 915 418 Data protection regulations Terms and conditions A website'
- contact_email_1: "post@northernhighlights.no"
- contact_phone_1: "+47 22 22 22 22"

### MORTEC AS (922238561) -> https://www.mortec.no/
- identity: identity_gate:organisation_number | snippet: 'frastruktur Mortec AS Slettestien 4, 1359 Eiksmarka O rg nr 922 238 561 Bank 1506 206 1313 www.mortec.no Epost Post@mortec.no Faktu'
- contact_email_1: "post@mortec.no"
- contact_phone_1: "+47 920 18 382"

### MOER INSTALLASJON AS (923156631) -> https://www.moer.no/
- identity: identity_gate:organisation_number | snippet: 'installasjon AS 33 30 33 20 Østveien 529, 3145 Tjøme Org.no 923 156 631 Moer Installasjon AS - Moer Gruppen\xa0- din elektriker i Vest'
- contact_email_1: "post@moer.no"
- contact_phone_1: "33 35 90 90"

### STABIL DATA OG FOTO AS (923833021) -> https://stabildataogfotoas.no/
- identity: identity_gate:legal_name+postcode_city | snippet: 'ering osv. Nå har vi flyttet til Kjærre - Koretveien 50 B - 1626 Manstad Veibeskrivelse trykk her. Du kan ringe for timeavtale etter'
- contact_phone_1: "90764526"
- latest_activity_date: "2020-07-21"
- public_activity: 'Nyheter' 2020-07-21 <https://stabildataogfotoas.no/feed/> snippet: '</slash:comments>\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Nyheter</title>\n\t\t<link>https://stabildataogfotoas.no/2020/07/21/hello-world/</link>\n\t\t'

### TOLLFOKUS AS (924788380) -> https://www.tullfokus.com/en
- identity: identity_gate:organisation_number | snippet: 'KUS AB Corporate ID: 556944-0505 TOLLFOKUS AS Corporate ID: 924 788 380 Prästängsvägen 29 45233 Strömstad Sweden Services Import De'
- website_description: "We handle both Swedish and Norwegian exports & imports. With personal service, experienced dedicated customs experts and the latest technology."
- contact_email_1: "kontakt@tullfokus.com"

### NORWEGIAN HOUSING AS (925216151) -> https://www.norwegianhousing.no/
- identity: identity_gate:organisation_number | snippet: 'st Melding Send melding © 2026 Norwegian Housing AS Org.nr. 925 216 151 Norwegian Housing AS Norwegian Housing AS – vi kjøper eiend'
- website_description: "Norwegian Housing AS – vi kjøper eiendommer og tomter i Norge, direkte eller i samarbeid med deg."
- contact_email_1: "post@norwegianhousing.no"
- contact_phone_1: "450 08 200"

### ANGSTKLINIKKEN AS (926627430) -> https://angstklinikken.no/
- identity: identity_gate:legal_name+street_address | snippet: 'Les mer Kontakt +47 980 86 017 post@angstklinikken.no Besøk Universitetsgata 14, 0164 Oslo Se veibeskrivelse Informasjon Ofte stilte spørsm'
- website_description: "Angstklinikken er Norges største klinikk for angstbehandling, med psykologer som har spisskompetanse på angst, OCD, stress og relaterte plager."
- contact_email_1: "post@angstklinikken.no"
- contact_phone_1: "+47 980 86 017"

### KRETSA AS (928047806) -> https://www.kretsa.no/
- identity: identity_gate:legal_name+registered_phone | snippet: 'Kretsa 0 Skip to Content VÅRE PRODUKTER OM OSS KONTAKT OSS Open Me'
- contact_email_1: "elisabeth@kretsa.no"
- contact_phone_1: "917 69 632"

### BLOKKSBERG AS (933246558) -> https://blokksberg.com/
- identity: identity_gate:organisation_number | snippet: 'te løsninger i produksjon. hei@blokksberg.com Blokksberg AS 933 246 558 MVA Sannergata 5A, 0557 Oslo hei@blokksberg.com +47 488 61'
- website_description: "Vårt mål er å fjerne friksjonen mellom mennesker og teknologi."
- contact_email_1: "hei@blokksberg.com"
- contact_phone_1: "+47 488 61 588"

### MYRVÅG AS (933460517) -> https://sandalikt.no/
- identity: identity_gate:organisation_number | snippet: 'tt © 2026 SANDAL IKT · Ei merkevare frå Myrvåg AS · Org.nr. 933 460 517 MVA Informasjonskapslar og statistikk Vi brukar nødvendige'
- website_description: "Vi hjelper privatpersonar og små verksemder med IT-support, Microsoft 365, nettverk og moderne nettsider."
- contact_email_1: "post@sandalikt.no"
- contact_phone_1: "70 04 02 00"

### EMBALLASJELAGERET AS (933537463) -> https://www.emballasjelageret.no/
- identity: identity_gate:legal_name+street_address | snippet: 'i kan hjelpe deg med din emballasjebehov. Emballasjelageret Rindsemvegen 1 Verdal, 7657 Email post@emballasjelageret.no Phone +47 4110'
- website_description: "Trenger du krukker eller flasker til din produksjon?"
- contact_email_1: "post@emballasjelageret.no"
- contact_phone_1: "+47 41103482"

### ARLEAL AS (934556534) -> https://arleal.no/
- identity: identity_gate:organisation_number | snippet: 'o +47 991 98 274 Personvern Arleal AS · Organisasjonsnummer 934 556 534 · Registrert i Foretaksregisteret · Nådlandsberget 31, 4034'
- website_description: "Arleal AS er et norsk aksjeselskap i Stavanger, stiftet i 2024. Selskapet utvikler og driver egne apper og tjenester. Første produkt er Tregom."
- contact_email_1: "baag@arleal.no"
- contact_phone_1: "+47 991 98 274"

### ULEFOS BRUG AS (938317828) -> https://www.ulefos.no/
- identity: identity_gate:legal_name+street_address | snippet: 'rskler Beslag Dokumenter Kontakt Ulefos Brug Ulefos Brug AS Fabrikkgata 8 3830 Ulefoss 35 94 94 50 ulefos.brug@ulefos.no Ansatte: Sal'
- contact_email_1: "agj@ulefos.no"
- contact_phone_1: "35 94 94 50"

### STIFTELSEN KONGSBERG JAZZFESTIVAL (970491708) -> https://kongsbergjazz.no/
- identity: identity_gate:organisation_number | snippet: 'G JAZZFESTIVAL Stiftelsen Kongsberg Jazzfestival // Org. nr 970 491 708 Fakturaadresse: Hyttegata 1, 3616 KONGSBERG // kongsbergjaz'
- website_description: "Dette er forsiden til Kongsberg Jazzfestival. Her finner du knapper til programside, informasjon, siste nyheter og Barnivalen."
- contact_email_1: "kontoret@kongsbergjazz.no"
- contact_phone_1: "48 95 02 63"

### RYENBERGET SKOLE (971526459) -> https://www.delk.no/ryenberget-skole/
- identity: identity_gate:organisation_number | snippet: 'lo 23 21 01 61 [javascript protected email address] Org.nr. 971 526 459 Ryenberget skole eies og drives av DELK . Vi er en del av n'
- contact_email_1: "post@ryenbergetskole.no"
- contact_phone_1: "23 21 01 61"
- careers_page: {"kind": "company_page", "url": "https://www.delk.no/ryenberget-skole/jobbe-hos-oss/"}

### EGIL PEDERSEN AS (976910702) -> https://egilpedersen.no/
- identity: identity_gate:organisation_number | snippet: 'andag - fredag: 07:00 - 16:00 post@egilpedersen.no Org.nr.: 976 910 702 Facebook-f Instagram Våre malertjenester Innvendig maling U'
- website_description: "Over 120 år som din lokale maler og tapetserer i Sarpsborg! Som byens malermester tilbyr vi innvendig og utvendig maling samt sprøytemaling. Som gulvlegger leg
- contact_email_1: "post@egilpedersen.no"
- contact_phone_1: "994 10 121"
- latest_activity_date: "2024-12-02"
- public_activity: 'I utvider vårt nedslagsfelt!' 2024-12-02 <https://egilpedersen.no/feed/> snippet: '<height>32</height>\n</image> \n\t<item>\n\t\t<title>I utvider vårt nedslagsfelt!</title>\n\t\t<link>https://egilpedersen.no/i-utvider-vart-nedslagsf'

### HÆGEBOSTAD OG ÅSERAL RENOVASJONSSELSKAP-HÅR IKS (979361475) -> https://www.har-renovasjon.no/
- identity: identity_gate:organisation_number+legal_name_not_on_page | snippet: 'ttebu MinRenovasjon app. © Copyright 2026 HÅR IKS - Org.nr: 979 361 475 | Personvernerklæring | Tilgjengelighetserklæring Design: N'
- contact_email_1: "post@har-renovasjon.no"
- contact_phone_1: "913 24 720"

### PROTOTYPER AS (979369344) -> https://prototyper.as/
- identity: identity_gate:organisation_number | snippet: 'steget med oss! Kontakt Info Addresse Prototyper AS (org.nr 979 369 344) Ole Deviks vei 16, 0666 Oslo Ring oss: Truls: 934 04 331 E'
- contact_email_1: "post@prototyper.as"
- contact_phone_1: "906 59 973"

### SMØRHAMN HANDELSTAD AS (979439938) -> https://www.smorhamn.no/
- identity: identity_gate:legal_name_partial+street_address+postcode_city | snippet: 'OSS Tlf: +47 958 68 768 E-post: smorhamn@gmail.com ADRESSE Smørhamnsvegen 1114 6729 Kalvåg BESTILLING E-post: smorhamn@gmail.com el. Airbn'
- contact_email_1: "smorhamn@gmail.com"
- contact_phone_1: "+47 958 68 768"

### HAVBRUKSSTASJONEN I TROMSØ AS (980900754) -> https://havbruksstasjonen.no/
- identity: identity_gate:legal_name+street_address | snippet: 'Arkiv English Eid av: Adresse Havbruksstasjonen i Tromsø AS Skarsfjordvegen 860, 9131 Kårvik Telefon: +47 77 66 74 00 E-post: e-post@havbru'
- website_description: "Havbruksstasjonen er et forskningsanlegg for studier av marin fisk, ferskvannsfisk, skalldyr, skjell og andre akvatiske organismer."
- contact_email_1: "e-post@havbruksstasjonen.no"
- contact_phone_1: "+47 77 66 74 00"

### NORDNET BANK NUF (982503868) -> https://www.nordnet.no/
- identity: identity_gate:legal_name+street_address | snippet: 'ghet Sikkerhet og svindel © 2026 Nordnet Bank AB. Nordnet | Karl Johans gate 16c | 0154 Oslo Litt morsommere sparing & investering. Det skal'
- website_description: "Det skal være enkelt og inspirerende for alle å investere. Kom i gang nå!"
- contact_email_1: "kundeservice@nordnet.no"
- contact_phone_1: "23 33 30 23"

### TENDENZER AS (982820871) -> https://tendenzer.no/
- identity: identity_gate:legal_name+street_address | snippet: 'risikofritt og enkelt å jobbe sammen med oss. Tendenzer AS O.H. Bangs vei 51 1363 Høvik +47 67 81 81 30 This email address is being prot'
- website_description: "Branding & sales of world leading brands"
- contact_phone_1: "+47 67 81 81 30"

### ERIKSFIORD AS (983394361) -> https://www.eriksfiord.com/
- identity: identity_gate:legal_name+postcode_city | snippet: 'on tradition. Eriksfiord AS iPark Prof. Olav Hanssensvei 7A 4021 Stavanger, Norway Mobile: +47 91190946 Email: ms AT eriksfiord.com Er'
- contact_phone_1: "+47 91190946"
- latest_activity_date: "2026-09-21"
- public_activity: 'Eriksfiord personnel presenting at Geological Society of London Oct 06-07, 2026' 2026-09-21 <https://www.eriksfiord.com/feed/> snippet: '<height>32</height>\n</image> \n\t<item>\n\t\t<title>Eriksfiord personnel presenting at Geological Society of London Oct 06-07, 2026</title>\n\t\t<li'
- public_activity: 'Continued Beach Volleyball Success for the “Eriksfiord Boys”' 2026-08-06 <https://www.eriksfiord.com/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Continued Beach Volleyball Success for the “Eriksfiord Boys”</title>\n\t\t<link>htt'
- public_activity: 'Eriksfiord runs workshop with Halliburton and Baker Hughes @ ARMA 2026' 2026-06-27 <https://www.eriksfiord.com/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Eriksfiord runs workshop with Halliburton and Baker Hughes @ ARMA 2026</title>\n\t'
- public_activity: 'Visit Eriksfiord’s booth 37 at the 67th Annual SPWLA Symposium at Lake Conroe, May 16-20, 2026' 2026-05-06 <https://www.eriksfiord.com/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Visit Eriksfiord’s booth 37 at the 67th Annual SPWLA Symposium at Lake Conroe, M'

### EUROPRESS AS (983739849) -> https://europressgroup.com/no/
- identity: identity_gate:organisation_number | snippet: 'e-faktura: Europress AS E-invoice address: Europress AS, NO983739849 Operator: Basware Operator address: BAWCFI22 Om dere ikke h'
- website_description: "Europress tilbyr innovative komprimatorer och presser for avfallshåndtering og hjelper sine kunder med å nå mål om en sirkulær økonomi."
- contact_email_1: "post@europress.no"
- contact_phone_1: "815 00 221"
- careers_page: {"kind": "company_page", "url": "https://europressgroup.com/no/rekruttering/"}
- latest_activity_date: "2026-08-24"
- public_activity: 'Eljas Tuovinen appointed Chief Commercial Officer at Europress' 2026-08-24 <https://europressgroup.com/no/feed/> snippet: '<height>32</height>\n</image> \n\t<item>\n\t\t<title>Eljas Tuovinen appointed Chief Commercial Officer at Europress</title>\n\t\t<link>https://europr'
- public_activity: 'Suur-Savo samvirkelag og Encore Miljøtjenester – intelligent avfallshåndtering med SMART-teknologi' 2024-07-26 <https://europressgroup.com/no/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>Suur-Savo samvirkelag og Encore Miljøtjenester – intelligent avfallshåndtering m'
- public_activity: 'RESIRKULERING MED KOMPRIMATORER OG BALLEPRESSER – PLAST' 2024-07-26 <https://europressgroup.com/no/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>RESIRKULERING MED KOMPRIMATORER OG BALLEPRESSER – PLAST</title>\n\t\t<link>https://'
- public_activity: 'RESIRKULERING MED KOMPRIMATORER OG BALLEPRESSER – PAPP' 2024-07-26 <https://europressgroup.com/no/feed/> snippet: '</content:encoded>\n\t\t\t\t\t\n\t\t\n\t\t\n\t\t\t</item>\n\t\t<item>\n\t\t<title>RESIRKULERING MED KOMPRIMATORER OG BALLEPRESSER – PAPP</title>\n\t\t<link>https://e'

### NORDENG AS (985406693) -> https://www.nordengas.no/
- identity: identity_gate:legal_name+registered_phone | snippet: 'Nordeng AS Tromsø | Forretningsfører fiskenæringen | Kystbåtrederier T'
- website_description: "Nordeng AS kan med sin erfaring og ekspertise bidra til etablering og best mulig drift av fiskenæringen, spesielt fangstsektoren. Ta kontakt."
- contact_email_1: "bjarni.sigurdsson@nordengas.no"
- contact_phone_1: "+47 959 03 787"

### COMPUTAS AS (986352325) -> https://computas.com/
- identity: identity_gate:legal_name+street_address | snippet: 'er Kontakt oss (+47) 21 99 33 20 kontakt@computas.com Oslo: Akersgata 35 0158 Oslo Personvernerklæring Besøk oss Oslo: Akersgata 35,'
- website_description: "Computas er et nordisk IT- og rådgivningsselskap med over 40 års erfaring i å bruke teknologi til å skape varig verdi. Vi hjelper store og små virksomheter, i 
- contact_email_1: "kontakt@computas.com"
- contact_phone_1: "21 99 33 20"
- latest_activity_date: "2026-10-02"
- public_activity: 'Computas bidrar til TV-aksjonen' 2026-10-02 <https://computas.com/feed/> snippet: '<site xmlns="com-wordpress:feed-additions:1">237093896</site>\t<item>\n\t\t<title>Computas bidrar til TV-aksjonen</title>\n\t\t<link>https://comput'
- public_activity: 'NXT-dag i Trondheim!' 2026-09-23 <https://computas.com/feed/> snippet: '<post-id xmlns="com-wordpress:feed-additions:1">27045</post-id>\t</item>\n\t\t<item>\n\t\t<title>NXT-dag i Trondheim!</title>\n\t\t<link>https://compu'
- public_activity: 'Vi fortsetter satsingen på nyutdannede' 2026-09-22 <https://computas.com/feed/> snippet: '<post-id xmlns="com-wordpress:feed-additions:1">74615</post-id>\t</item>\n\t\t<item>\n\t\t<title>Vi fortsetter satsingen på nyutdannede</title>\n\t\t<'
- public_activity: 'JavaZone 2026: Hva skjer når KI-hypen legger seg?' 2026-09-10 <https://computas.com/feed/> snippet: '<post-id xmlns="com-wordpress:feed-additions:1">74586</post-id>\t</item>\n\t\t<item>\n\t\t<title>JavaZone 2026: Hva skjer når KI-hypen legger seg?<'

### SAMEIET HUNDVÅGTUNET (987294345) -> https://hundvagtunet.no/
- identity: identity_gate:organisation_number | snippet: 'ionveien 2 4085 Hundvåg Fakturaadresse Sameiet Hundvågtunet 987294345 Postboks 2714 7439 TRONDHEIM E-post: faktura@bate.no (pdf -'
- contact_email_1: "styret@hundvagtunet.no"
- contact_phone_1: "906 15 001"

### EUROJURIS NORGE AS (987585986) -> https://www.eurojuris.no/
- identity: identity_gate:legal_name+street_address | snippet: 's hjemmeside MEDLEMSFIRMAENE KONTAKT OSS Eurojuris Norge AS Nedre Storgate 19 Pb. 294 Bragernes 3001 Drammen Tlf +47 32 25 55 00 post@eur'
- website_description: "Eurojuris Norge - en landsdekkende sammenslutning av 17 selvstendige advokatfirmaer"
- contact_email_1: "post@eurojurisnorge.no"
- contact_phone_1: "+47 32 25 55 00"
- careers_page: {"kind": "company_page", "url": "https://www.eurojuris.no/no/karriere-karriere/karriere"}

### BRØTTET BARNEHAGE SA (988278750) -> https://brottet.barnehage.no/
- identity: identity_gate:legal_name+postcode_city | snippet: 'ehageår. Kontakt Brøttet Barnehage Kristian Brennersvei 170 3029 DRAMMEN T: 32276250 E: dl@brottetbhg.no Daglig leder : 91818895 Avd'
- contact_email_1: "dl@brottetbhg.no"
- contact_phone_1: "32276250"

### BILRETUR AS (988498572) -> https://www.bilretur.as/
- identity: identity_gate:legal_name+street_address | snippet: 'tur AS er eid av biloppsamlere i hele Norge og har kontor i Strømsveien 287 på Alnabru i Oslo. Administrerende direktør er Arne Hugo El'
- contact_phone_1: "982 82 340"

### WASHINGTON MILLS AS (990022585) -> https://www.washingtonmills.com/
- identity: identity_gate:legal_name+postcode_city | snippet: '4 Email: sales@washingtonmills.co.uk Washington Mills AS NO-7300 Orkanger, Norway Tel: + 47-72-48-35-00 Fax: 47-72-48-35-01 Email: wm'
- website_description: "Global leaders in high-quality abrasive grain, ceramic powder and fused mineral manufacturing since 1868."
- contact_email_1: "info@washingtonmills.com"
- careers_page: {"kind": "company_page", "url": "https://www.washingtonmills.com/company/careers"}

(ambiguous) TORGHALLEN BODØ AS 811564222: not published: legal name not found on page

(ambiguous) INNOSAFE AS 818003072: not published: legal name not found on page

(ambiguous) BORETTSLAGET FJØSANGERVEIEN 161 854710222: not published: page states a different organisation number (946450197)

(ambiguous) SAMEIET MINA BEITEPLUKKSVEI 151-155 888437932: not published: legal name not found on page

(ambiguous) VIKING FOOTWEAR AS 890264212: not published: page states a different organisation number (992933348)

(ambiguous) TRANSURFING GROUP AS 912412237: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) SAMEIET TOU PARK V 912743543: not published: page states a different organisation number (920800572)

(ambiguous) FJELLBY AS 914495644: not published: legal name not found on page

(ambiguous) RE INSPIRE AS 920457894: not published: legal name not found on page

(ambiguous) CENTRA EIENDOM AS 923673601: not published: page states a different organisation number (943438102)

(ambiguous) SAMEIET STORMAST 925257761: not published: page states a different organisation number (946450197)

(ambiguous) KIOSKDRIFT ALEXANDER FREDRIKSEN AS 925926396: not published: legal name not found on page

(ambiguous) INFLYT MEDIA AS 926424378: not published: legal name not found on page

(ambiguous) BOHLIN INVEST AS 927867389: not published: page states a different organisation number (912835405)

(ambiguous) SHIPWRECK HOLDING AS 929215656: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) KONGSLØKKEN EIERSEKSJONSSAMEIE 930517224: not published: page states a different organisation number (920800572)

(ambiguous) LOGISTEA PROPERTIES POLAND AS 931693514: not published: legal name not found on page

(ambiguous) BORETTSLAGET SAXEMARKA IV 932305364: not published: legal name not found on page

(ambiguous) BORETTSLAGET MISJONSVEIEN 6 932305631: not published: legal name not found on page

(ambiguous) TUNET PUB DRIFT AS 932771985: not published: page states a different organisation number (918616039)

(ambiguous) LOOPUP NORWAY NUF 933142256: not published: legal name not found on page

(ambiguous) IKOS BARBERSHOP AS 933269612: not published: identity score 0.70 below 0.90 (signals: legal_name, municipality_only)

(ambiguous) AS PARKTEATERET 933724093: not published: legal name not found on page

(ambiguous) MANTASWRAP DRIFT AS 936242375: not published: page states a different organisation number (936068693)

(ambiguous) FASADE OG TAKVASK AS 936456308: not published: page states a different organisation number (925145645)

(ambiguous) STIFTELSEN HUSFLIDEN NORDMØRE 941003656: not published: legal name not found on page

(ambiguous) ORRELIA BORETTSLAG 942271212: not published: page states a different organisation number (952527827)

(ambiguous) OKSVAL I BORETTSLAG 947807919: not published: page states a different organisation number (950285680)

(ambiguous) AL Brønnerud Borettslag 948840200: not published: page states a different organisation number (950285680)

(ambiguous) BORETTSLAGET SPOREN 951194646: not published: legal name not found on page

(ambiguous) BORETTSLAGET HENRIK IBSENSG 4 951195162: not published: legal name not found on page

(ambiguous) VESTBO EIENDOM AS 954641228: not published: page states a different organisation number (946450197)

(ambiguous) STIFTELSEN DET NORSKE ARBORET 971350008: not published: page states a different organisation number (874789542)

(ambiguous) GENERALLUNDEN BOLIGSAMEIE 971481595: not published: page states a different organisation number (920800572)

(ambiguous) HALDEN SPAREBANKS ÆRESPRIS 150 ÅRS JUBILEUMSFOND STI 974988984: not published: page states a different organisation number (997534484)

(ambiguous) LETSEA AS 976253744: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) JOHN CRANE NORGE Norsk avdeling av utenlandsk foretak NUF 976541871: not published: legal name not found on page

(ambiguous) INGERID, SYNNØVE OG ELIAS FEGERSTENS STIFTELSE FOR NORSKE BILDENDE KUNSTNERE 977120063: not published: page states a different organisation number (971288396)

(ambiguous) GREVLELIA BORETTSLAG 977474833: not published: legal name not found on page

(ambiguous) RUDI BAUMGARTEN NET AS 979679718: not published: legal name not found on page

(ambiguous) P.O.P. AS 979860781: not published: legal name not found on page

(ambiguous) BOLIGSAMEIET CONRADISGATE 1 979945817: not published: page states a different organisation number (950285680)

(ambiguous) BUYANDREAD AS 980039005: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) LANDBRUKSLEGATET I NORGES VEL STI 981104366: not published: page states a different organisation number (965208739)

(ambiguous) SAKSHUS HERREGÅRD BORETTSLAG 984531273: not published: page states a different organisation number (995366517)

(ambiguous) MITEK INDUSTRIES AS 984885881: not published: legal name not found on page

(ambiguous) AMFI BYGG EIDSVOLL AS 985058466: not published: legal name not found on page

(ambiguous) LIFJELLSTUA EIENDOM AS 985186081: not published: legal name not found on page

(ambiguous) VEITVET SKOLE AS 985282005: not published: legal name not found on page

(ambiguous) PERSONAL SERVICE OG SIKKERHET AS 985321876: not published: legal name not found on page

(ambiguous) BERYLLVEIEN SAMEIE 986448411: not published: page states a different organisation number (946450197)

(ambiguous) ELLEFSTOLGATA BORETTSLAG 987264160: not published: legal name not found on page

(ambiguous) BB AGRO AS 987992816: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) TJUVHOLMEN F3 NÆRING AS 988419958: not published: page lists 35 other organisation numbers (group or portfolio site)

(ambiguous) NYGAARDSGATA 55 AS 990222479: not published: identity score 0.70 below 0.90 (signals: legal_name, municipality_only)

(ambiguous) STIFTELSEN ALLMENNMEDISINSK FORSKNINGSFOND 991465618: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) SAMEIET GRIMSRØD GÅRD 991632956: not published: page states a different organisation number (995981378)

(ambiguous) MITT DEKKHOTELL RØA AS 992122714: not published: legal name not found on page

(ambiguous) STICKY FINGERS NORGE AS 992840692: not published: identity score 0.50 below 0.90 (signals: legal_name)

(ambiguous) TORVGATA 10 AS 994920928: not published: legal name not found on page

(ambiguous) SENTRUM EIENDOM TROMSØ AS 996302628: not published: legal name not found on page

(ambiguous) HOVLANDSVEIEN 85/87 996719243: not published: legal name not found on page

(ambiguous) SYVERUD DAGLIGVARE AS 996861260: not published: legal name not found on page

(ambiguous) KLETOR AS 998058643: not published: legal name not found on page

(ambiguous) FRAM KOMBINASJON 998338816: not published: page states a different organisation number (956241308)

(ambiguous) JORDBÆRPIKENE STRØMMEN AS 998507723: not published: page states a different organisation number (919357436)

(ambiguous) HAMMERSBORGGT 12 AS 998585937: not published: legal name not found on page

(ambiguous) ALKEVEIEN 1 AS 999104371: not published: legal name not found on page
