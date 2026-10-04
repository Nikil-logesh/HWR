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
- website_description: 45
- contact_email_1: 40
- contact_phone_1: 45
- social_linkedin: 8
- social_facebook: 11
- social_instagram: 7
- products_services: 44
- careers_page: 8
- open_positions: 0
- hiring_status: 1
- public_activity: 8
- latest_activity_date: 8
- open_positions states: {'not_available': 47, 'ambiguous': 1}
- public_activity states: {'not_available': 38, 'available': 8, 'ambiguous': 1, 'failed': 1}
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
- 1 x products_services: snippet not found in page

## requests
- website-listing companies: mean 8.0, max 15; verified: mean 9.7

## samples to inspect by hand (verified sites)

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
