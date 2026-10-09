# Non-Tube services as ordered station sequences (names as in tfl_stations.json).
# Each service = one train pattern; changing between services counts as a change.
# Sources: line structure per TfL network as of 2026 (Overground line names from Nov 2024 rebrand).
# Service patterns marked with '#?' are simplified / best estimate.

EXTRA = {
 "elizabeth": {"name": "Elizabeth line", "mode": "elizabeth", "colour": "#6950a1", "wait": 3, "speed": 50,
  "services": [
   ["Reading","Twyford","Maidenhead","Taplow","Burnham","Slough","Langley","Iver","West Drayton","Hayes & Harlington","Southall","Hanwell","West Ealing","Ealing Broadway","Acton Main Line","Paddington","Bond Street","Tottenham Court Road","Farringdon","Liverpool Street","Whitechapel","Canary Wharf","Custom House","Woolwich","Abbey Wood"],
   ["Heathrow Terminal 5","Heathrow Terminals 2 & 3","Hayes & Harlington","Southall","Hanwell","West Ealing","Ealing Broadway","Acton Main Line","Paddington","Bond Street","Tottenham Court Road","Farringdon","Liverpool Street","Whitechapel","Canary Wharf","Custom House","Woolwich","Abbey Wood"],
   ["Heathrow Terminal 4","Heathrow Terminals 2 & 3","Hayes & Harlington","Southall","Hanwell","West Ealing","Ealing Broadway","Acton Main Line","Paddington","Bond Street","Tottenham Court Road","Farringdon","Liverpool Street","Whitechapel","Stratford","Maryland","Forest Gate","Manor Park","Ilford","Seven Kings","Goodmayes","Chadwell Heath","Romford","Gidea Park","Harold Wood","Brentwood","Shenfield"],  #?
  ]},
 "liberty": {"name": "Liberty line", "mode": "overground", "colour": "#5d6061", "wait": 15, "speed": 45,
  "services": [["Romford","Emerson Park","Upminster"]]},
 "lioness": {"name": "Lioness line", "mode": "overground", "colour": "#faa61a", "wait": 10, "speed": 45,
  "services": [["Euston","South Hampstead","Kilburn High Road","Queen's Park","Kensal Green","Willesden Junction","Harlesden","Stonebridge Park","Wembley Central","North Wembley","South Kenton","Kenton","Harrow & Wealdstone","Headstone Lane","Hatch End","Carpenders Park","Bushey","Watford High Street","Watford Junction"]]},
 "mildmay": {"name": "Mildmay line", "mode": "overground", "colour": "#437ec1", "wait": 4, "speed": 40,
  "services": [
   ["Richmond","Kew Gardens","Gunnersbury","South Acton","Acton Central","Willesden Junction","Kensal Rise","Brondesbury Park","Brondesbury","West Hampstead","Finchley Road & Frognal","Hampstead Heath","Gospel Oak","Kentish Town West","Camden Road","Caledonian Road & Barnsbury","Highbury & Islington","Canonbury","Dalston Kingsland","Hackney Central","Homerton","Hackney Wick","Stratford"],
   ["Clapham Junction","Imperial Wharf","West Brompton","Kensington (Olympia)","Shepherd's Bush","Willesden Junction","Kensal Rise","Brondesbury Park","Brondesbury","West Hampstead","Finchley Road & Frognal","Hampstead Heath","Gospel Oak","Kentish Town West","Camden Road","Caledonian Road & Barnsbury","Highbury & Islington","Canonbury","Dalston Kingsland","Hackney Central","Homerton","Hackney Wick","Stratford"],
  ]},
 "suffragette": {"name": "Suffragette line", "mode": "overground", "colour": "#39b97a", "wait": 7, "speed": 40,
  "services": [["Gospel Oak","Upper Holloway","Crouch Hill","Harringay Green Lanes","South Tottenham","Blackhorse Road","Walthamstow Queen's Road","Leyton Midland Road","Leytonstone High Road","Wanstead Park","Woodgrange Park","Barking","Barking Riverside"]]},
 "weaver": {"name": "Weaver line", "mode": "overground", "colour": "#972861", "wait": 8, "speed": 40,
  "services": [
   ["Liverpool Street","Bethnal Green","Cambridge Heath","London Fields","Hackney Downs","Rectory Road","Stoke Newington","Stamford Hill","Seven Sisters","Bruce Grove","White Hart Lane","Silver Street","Edmonton Green","Bush Hill Park","Enfield Town"],
   ["Liverpool Street","Bethnal Green","Cambridge Heath","London Fields","Hackney Downs","Rectory Road","Stoke Newington","Stamford Hill","Seven Sisters","Bruce Grove","White Hart Lane","Silver Street","Edmonton Green","Southbury","Turkey Street","Theobalds Grove","Cheshunt"],
   ["Liverpool Street","Bethnal Green","Cambridge Heath","London Fields","Hackney Downs","Clapton","St James Street","Walthamstow Central","Wood Street","Highams Park","Chingford"],
  ]},
 "windrush": {"name": "Windrush line", "mode": "overground", "colour": "#ee2e24", "wait": 4, "speed": 38,
  "services": [
   ["Highbury & Islington","Canonbury","Dalston Junction","Haggerston","Hoxton","Shoreditch High Street","Whitechapel","Shadwell","Wapping","Rotherhithe","Canada Water","Surrey Quays","New Cross Gate","Brockley","Honor Oak Park","Forest Hill","Sydenham","Penge West","Anerley","Norwood Junction","West Croydon"],
   ["Highbury & Islington","Canonbury","Dalston Junction","Haggerston","Hoxton","Shoreditch High Street","Whitechapel","Shadwell","Wapping","Rotherhithe","Canada Water","Surrey Quays","New Cross Gate","Brockley","Honor Oak Park","Forest Hill","Sydenham","Crystal Palace"],
   ["Dalston Junction","Haggerston","Hoxton","Shoreditch High Street","Whitechapel","Shadwell","Wapping","Rotherhithe","Canada Water","Surrey Quays","New Cross"],
   ["Dalston Junction","Haggerston","Hoxton","Shoreditch High Street","Whitechapel","Shadwell","Wapping","Rotherhithe","Canada Water","Surrey Quays","Queens Road Peckham","Peckham Rye","Denmark Hill","Clapham High Street","Wandsworth Road","Clapham Junction"],
  ]},
 "dlr": {"name": "DLR", "mode": "dlr", "colour": "#00afad", "wait": 3, "speed": 32,
  "services": [
   ["Bank","Shadwell","Limehouse","Westferry","West India Quay","Canary Wharf","Heron Quays","South Quay","Crossharbour","Mudchute","Island Gardens","Cutty Sark","Greenwich","Deptford Bridge","Elverson Road","Lewisham"],
   ["Stratford","Pudding Mill Lane","Bow Church","Devons Road","Langdon Park","All Saints","Poplar","West India Quay","Canary Wharf","Heron Quays","South Quay","Crossharbour","Mudchute","Island Gardens","Cutty Sark","Greenwich","Deptford Bridge","Elverson Road","Lewisham"],
   ["Tower Gateway","Shadwell","Limehouse","Westferry","Poplar","Blackwall","East India","Canning Town","Royal Victoria","Custom House","Prince Regent","Royal Albert","Beckton Park","Cyprus","Gallions Reach","Beckton"],
   ["Bank","Shadwell","Limehouse","Westferry","Poplar","Blackwall","East India","Canning Town","West Silvertown","Pontoon Dock","London City Airport","King George V","Woolwich Arsenal"],  #?
   ["Stratford International","Stratford","Stratford High Street","Abbey Road","West Ham","Star Lane","Canning Town","West Silvertown","Pontoon Dock","London City Airport","King George V","Woolwich Arsenal"],
   ["Stratford International","Stratford","Stratford High Street","Abbey Road","West Ham","Star Lane","Canning Town","Royal Victoria","Custom House","Prince Regent","Royal Albert","Beckton Park","Cyprus","Gallions Reach","Beckton"],  #?
  ]},
 "tram": {"name": "Trams", "mode": "tram", "colour": "#7dbe2c", "wait": 4, "speed": 24,
  "services": [
   ["Wimbledon","Dundonald Road","Merton Park","Morden Road","Phipps Bridge","Belgrave Walk","Mitcham","Mitcham Junction","Beddington Lane","Therapia Lane","Ampere Way","Waddon Marsh","Wandle Park","Reeves Corner","Church Street","George Street","East Croydon","Lebanon Road","Sandilands","Addiscombe","Blackhorse Lane","Woodside","Arena","Harrington Road","Birkbeck","Avenue Road","Beckenham Road","Beckenham Junction"],
   ["Wimbledon","Dundonald Road","Merton Park","Morden Road","Phipps Bridge","Belgrave Walk","Mitcham","Mitcham Junction","Beddington Lane","Therapia Lane","Ampere Way","Waddon Marsh","Wandle Park","Reeves Corner","Church Street","George Street","East Croydon","Lebanon Road","Sandilands","Addiscombe","Blackhorse Lane","Woodside","Arena","Elmers End"],
   ["West Croydon","Wellesley Road","East Croydon","Lebanon Road","Sandilands","Lloyd Park","Coombe Lane","Gravel Hill","Addington Village","Fieldway","King Henry's Drive","New Addington"],
   ["Reeves Corner","Centrale","West Croydon"],  # Croydon town-centre loop (one-way in reality)
  ]},
}

TUBE_META = {
 "bakerloo": ("Bakerloo", "#a65a2a", 3, 38),
 "central": ("Central", "#e1251b", 2.5, 45),
 "circle": ("Circle", "#ffcd00", 4, 32),
 "district": ("District", "#007a33", 3, 38),
 "hammersmith-city": ("Hammersmith & City", "#ec9bad", 4, 32),
 "jubilee": ("Jubilee", "#7b868c", 2, 48),
 "metropolitan": ("Metropolitan", "#870f54", 4, 60),
 "northern": ("Northern", "#000000", 2.5, 42),
 "piccadilly": ("Piccadilly", "#000f9f", 2.5, 45),
 "victoria": ("Victoria", "#00a0df", 1.5, 50),
 "waterloo-city": ("Waterloo & City", "#6bcdb2", 2.5, 30),
}
