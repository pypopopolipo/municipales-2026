"""
Scraper des résultats des élections municipales 2026
Source : resultats-municipales-2026.fr (données data.gouv.fr)
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
import os
from nuances_politiques import classify_etiquette, get_famille

BASE_URL = "https://resultats-municipales-2026.fr"

DEPARTMENTS = [
    "01-ain", "02-aisne", "03-allier", "04-alpes-de-haute-provence",
    "05-hautes-alpes", "06-alpes-maritimes", "07-ardeche", "08-ardennes",
    "09-ariege", "10-aube", "11-aude", "12-aveyron",
    "13-bouches-du-rhone", "14-calvados", "15-cantal", "16-charente",
    "17-charente-maritime", "18-cher", "19-correze", "21-cote-dor",
    "22-cotes-darmor", "23-creuse", "24-dordogne", "25-doubs",
    "26-drome", "27-eure", "28-eure-et-loir", "29-finistere",
    "2a-corse-du-sud", "2b-haute-corse", "30-gard", "31-haute-garonne",
    "32-gers", "33-gironde", "34-herault", "35-ille-et-vilaine",
    "36-indre", "37-indre-et-loire", "38-isere", "39-jura",
    "40-landes", "41-loir-et-cher", "42-loire", "43-haute-loire",
    "44-loire-atlantique", "45-loiret", "46-lot", "47-lot-et-garonne",
    "48-lozere", "49-maine-et-loire", "50-manche", "51-marne",
    "52-haute-marne", "53-mayenne", "54-meurthe-et-moselle", "55-meuse",
    "56-morbihan", "57-moselle", "58-nievre", "59-nord", "60-oise",
    "61-orne", "62-pas-de-calais", "63-puy-de-dome",
    "64-pyrenees-atlantiques", "65-hautes-pyrenees",
    "66-pyrenees-orientales", "67-bas-rhin", "68-haut-rhin", "69-rhone",
    "70-haute-saone", "71-saone-et-loire", "72-sarthe", "73-savoie",
    "74-haute-savoie", "75-paris", "76-seine-maritime",
    "77-seine-et-marne", "78-yvelines", "79-deux-sevres", "80-somme",
    "81-tarn", "82-tarn-et-garonne", "83-var", "84-vaucluse",
    "85-vendee", "86-vienne", "87-haute-vienne", "88-vosges",
    "89-yonne", "90-territoire-de-belfort", "91-essonne",
    "92-hauts-de-seine", "93-seine-saint-denis", "94-val-de-marne",
    "95-val-doise",
]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Election-Data-Research/1.0"
})


def parse_number(text):
    """Convertit un texte en nombre."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d,.]", "", text.replace("\u202f", "").replace("\xa0", ""))
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned) if "." in cleaned else int(cleaned)
    except ValueError:
        return None


def get_communes_for_department(dept_slug):
    """Récupère la liste des communes d'un département."""
    url = f"{BASE_URL}/departement/{dept_slug}"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERREUR] Département {dept_slug}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    communes = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/resultats/" in href:
            slug = href.split("/resultats/")[-1].rstrip("/")
            # Extraire le nom propre depuis le premier texte du lien
            # Le lien contient : NomCommune + code postal + population + code INSEE + Maj
            first_text = ""
            for child in link.children:
                t = child.string if hasattr(child, "string") else str(child)
                if t and t.strip():
                    first_text = t.strip()
                    break
            if not first_text:
                first_text = slug.rsplit("-", 1)[0].replace("-", " ").title()
            communes.append({"slug": slug, "name": first_text, "department": dept_slug})

    return communes


def scrape_commune_results(commune_info):
    """Scrape les résultats d'une commune depuis le HTML."""
    slug = commune_info["slug"]
    url = f"{BASE_URL}/resultats/{slug}"

    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"commune": commune_info["name"], "slug": slug, "error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")
    result = {
        "commune": commune_info["name"],
        "slug": slug,
        "department": commune_info["department"],
    }

    # --- Participation ---
    # Structure : <dt>Inscrits</dt><dd>503</dd>
    for dt in soup.find_all("dt"):
        label = dt.get_text(strip=True).lower()
        dd = dt.find_next_sibling("dd")
        if not dd:
            continue
        val = dd.get_text(strip=True)

        if "inscrit" in label:
            result["inscrits"] = parse_number(val)
        elif "votant" in label:
            result["votants"] = parse_number(val)
        elif "abstention" in label:
            result["abstentions"] = parse_number(val)
            # Cherche le % dans le dd suivant
            dd2 = dd.find_next_sibling("dd")
            if dd2:
                pct_text = dd2.get_text(strip=True)
                if "%" in pct_text:
                    result["abstentions_pct"] = parse_number(pct_text.replace("%", ""))
        elif "blanc" in label or "nul" in label:
            result["blancs_nuls"] = parse_number(val)

    # Taux de participation depuis le SVG/texte "XX.X% participation"
    participation_el = soup.find("span", string=re.compile(r"participation", re.I))
    if participation_el:
        parent = participation_el.parent
        if parent:
            pct_span = parent.find("span", class_=re.compile(r"font-bold"))
            if pct_span:
                result["participation_pct"] = parse_number(
                    pct_span.get_text(strip=True).replace("%", "")
                )

    # Si pas trouvé via span, cherche dans le texte brut
    if "participation_pct" not in result:
        text = soup.get_text()
        match = re.search(r"([\d,]+)\s*%\s*participation", text, re.I)
        if match:
            result["participation_pct"] = parse_number(match.group(1))

    # --- Candidats / Résultats ---
    # Structure : <li class="rounded-lg p-3 bg-green-50...">
    #   <span class="text-sm font-semibold...">Nom</span>
    #   <span class="...">XX,X%</span>
    #   <div class="text-xs...">273 voix</div>
    candidates = []
    results_section = soup.find("div", id="candidats")
    if results_section:
        for li in results_section.find_all("li"):
            candidate = {}

            # Nom du candidat
            name_span = li.find("span", class_=re.compile(r"font-semibold"))
            if name_span:
                candidate["nom"] = name_span.get_text(strip=True)

            # Étiquette politique
            etiquette_p = li.find("p", class_=re.compile(r"text-xs.*text-gray"))
            if etiquette_p:
                candidate["etiquette"] = etiquette_p.get_text(strip=True)

            # Élu ?
            elu_span = li.find("span", string=re.compile(r"Élu", re.I))
            candidate["elu"] = elu_span is not None
            if elu_span:
                elu_text = elu_span.get_text(strip=True)
                sieges_match = re.search(r"(\d+)\s*siège", elu_text)
                if sieges_match:
                    candidate["sieges"] = int(sieges_match.group(1))

            # Pourcentage
            pct_span = li.find("span", class_=re.compile(r"font-bold"))
            if pct_span:
                pct_text = pct_span.get_text(strip=True)
                candidate["pourcentage"] = parse_number(pct_text.replace("%", "").replace(",", "."))

            # Voix
            voix_div = li.find("div", string=re.compile(r"voix", re.I))
            if voix_div:
                voix_text = voix_div.get_text(strip=True)
                voix_match = re.search(r"([\d\s\u202f\xa0]+)\s*voix", voix_text)
                if voix_match:
                    candidate["voix"] = parse_number(voix_match.group(1))

            if candidate.get("nom"):
                candidates.append(candidate)

    result["candidats"] = candidates
    result["nb_candidats"] = len(candidates)

    # --- Maire sortant ---
    maire_section = soup.find("h2", string=re.compile(r"Maire sortant", re.I))
    if maire_section:
        maire_card = maire_section.find_parent("div", class_=re.compile(r"shadow"))
        if maire_card:
            identite_dd = None
            for dt in maire_card.find_all("dt"):
                if "identit" in dt.get_text(strip=True).lower():
                    identite_dd = dt.find_next_sibling("dd")
                    break
            if identite_dd:
                result["maire_sortant"] = identite_dd.get_text(strip=True)

    return result


def main():
    os.makedirs("data", exist_ok=True)

    print("=" * 60)
    print("SCRAPER - Résultats Municipales 2026")
    print("=" * 60)

    # Étape 1 : Récupérer toutes les communes par département
    all_communes = []
    print(f"\n[1/2] Récupération des communes pour {len(DEPARTMENTS)} départements...")

    for i, dept in enumerate(DEPARTMENTS):
        communes = get_communes_for_department(dept)
        all_communes.extend(communes)
        print(f"  [{i+1:2d}/{len(DEPARTMENTS)}] {dept}: {len(communes)} communes")
        time.sleep(0.3)

    print(f"\nTotal : {len(all_communes)} communes trouvées")

    with open("data/communes_list.json", "w", encoding="utf-8") as f:
        json.dump(all_communes, f, ensure_ascii=False, indent=2)

    # Étape 2 : Scraper les résultats de chaque commune
    print(f"\n[2/2] Scraping des résultats pour {len(all_communes)} communes...")
    all_results = []
    errors = []

    for i, commune in enumerate(all_communes):
        result = scrape_commune_results(commune)
        if "error" in result:
            errors.append(result)
        else:
            all_results.append(result)

        if (i + 1) % 50 == 0:
            print(f"  Progression : {i+1}/{len(all_communes)} "
                  f"({len(all_results)} OK, {len(errors)} erreurs)")
            # Sauvegarde intermédiaire
            with open("data/resultats_partial.json", "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)

        time.sleep(0.2)

    # Sauvegarde JSON
    print(f"\nSauvegarde...")
    with open("data/resultats_municipales_2026.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # Export CSV
    csv_rows = []
    for r in all_results:
        base = {
            "commune": r.get("commune"),
            "slug": r.get("slug"),
            "department": r.get("department"),
            "inscrits": r.get("inscrits"),
            "votants": r.get("votants"),
            "participation_pct": r.get("participation_pct"),
            "abstentions": r.get("abstentions"),
            "abstentions_pct": r.get("abstentions_pct"),
            "blancs_nuls": r.get("blancs_nuls"),
            "maire_sortant": r.get("maire_sortant"),
            "nb_candidats": r.get("nb_candidats"),
        }
        if r.get("candidats"):
            for j, c in enumerate(r["candidats"]):
                row = {**base}
                row["candidat_rang"] = j + 1
                row["candidat_nom"] = c.get("nom")
                row["candidat_etiquette"] = c.get("etiquette")
                nuance = classify_etiquette(c.get("etiquette"))
                row["nuance_code"] = nuance
                row["nuance_label"] = get_famille(nuance)["label"]
                row["nuance_couleur"] = get_famille(nuance)["couleur"]
                row["candidat_voix"] = c.get("voix")
                row["candidat_pourcentage"] = c.get("pourcentage")
                row["candidat_elu"] = c.get("elu")
                row["candidat_sieges"] = c.get("sieges")
                csv_rows.append(row)
        else:
            csv_rows.append(base)

    fieldnames = [
        "commune", "slug", "department", "inscrits", "votants",
        "participation_pct", "abstentions", "abstentions_pct", "blancs_nuls",
        "maire_sortant", "nb_candidats",
        "candidat_rang", "candidat_nom", "candidat_etiquette",
        "nuance_code", "nuance_label", "nuance_couleur",
        "candidat_voix", "candidat_pourcentage", "candidat_elu", "candidat_sieges",
    ]
    with open("data/resultats_municipales_2026.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    # Résumé
    print("\n" + "=" * 60)
    print("TERMINÉ !")
    print(f"  Communes scrapées : {len(all_results)}")
    print(f"  Erreurs : {len(errors)}")
    print(f"  Fichiers :")
    print(f"    - data/communes_list.json")
    print(f"    - data/resultats_municipales_2026.json")
    print(f"    - data/resultats_municipales_2026.csv")
    print("=" * 60)

    if errors:
        with open("data/erreurs.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        print(f"  Erreurs dans data/erreurs.json")


if __name__ == "__main__":
    main()
