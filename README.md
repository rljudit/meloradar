# Melóradar

A Sajtóművek AI hírfigyelője munkavállalóknak és álláskeresőknek: globális munkaerőpiaci hírek, és hogy mit jelentenek neked itthon. Naponta frissítve.

Élő oldal: https://rljudit.github.io/meloradar/

A motor a HR monitoré (rljudit/hr-monitor); a megjelenés a Profession.hu B2C Design Systemre épül (navy, teal, sky, teal→sky átmenet, Montserrat, a design system vonalikonjai), tegező, gyakorlati „Mit jelent ez neked?” értelmezéssel.

## Felépítés

| Mappa / fájl | Mi ez |
| --- | --- |
| `data/articles.json` | Az összes hír és trend. Ezt bővíti minden reggel az automata frissítés. |
| `src/config.json` | Oldalnév, alcím, témák és színeik, ikonkészlet, impresszum adatai. |
| `src/style.css`, `src/app.js` | A megjelenés és a főoldal szűrői. |
| `src/og.png` | Megosztási kép (újragenerálás: `python3 src/make_og.py <Montserrat.ttf>`). |
| `build.py` | Statikus generátor: a fentiekből elkészíti a `docs/` mappát. |
| `docs/` | A kész weboldal, ezt szolgálja ki a GitHub Pages. Kézzel ne szerkeszd. |

## Frissítés kézzel

```
python3 build.py
git add -A && git commit -m "Frissítés" && git push
```

## Saját domain

A `src/config.json`-ban a `site.url` legyen az új cím, és add hozzá: `"domain": "meloradar.example.hu"`. A build ebből `docs/CNAME`-et ír; a DNS-ben egy CNAME rekord kell `rljudit.github.io` értékkel.

## Kapcsolódó Profession.hu-cikkek

- `data/profession_cikkek.json`: a Profession.hu álláskeresési tanácsainak jegyzéke (cím, link, rovat, címkék). Hetente frissíti a „Melóradar – Profession cikkjegyzék” feladat.
- Minden hírnél a `related` mező 1–2 linket tartalmaz ebből a jegyzékből. A build UTM-paramétert tesz rájuk: `utm_source=meloradar&utm_medium=referral&utm_campaign=kapcsolodo_cikk&utm_content=<hír azonosító>`.
- Megjelenés: a cikkoldalon „Olvass tovább a Profession.hu-n” doboz, a kártyákon az első link.
