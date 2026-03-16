"""Génère le CSV à partir des données JSON scrapées + nuances officielles du Ministère."""
import json
import csv
import os
import re
import pandas as pd
from nuances_politiques import classify_etiquette, get_famille


def build_official_nuances_index():
    """Construit un index nom_normalise -> nuance depuis le CSV officiel des candidatures."""
    path = "data/candidatures_france_tour1.csv"
    if not os.path.exists(path):
        print("  CSV officiel non trouvé, pas d'enrichissement des nuances.")
        return {}

    off = pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False)

    # Ajouter le CSV PLM (arrondissements Paris/Lyon/Marseille)
    plm_path = "data/plm_candidatures.csv"
    if os.path.exists(plm_path):
        plm = pd.read_csv(plm_path, sep=";", encoding="utf-8", low_memory=False)
        off = pd.concat([off, plm], ignore_index=True)
        print(f"  CSV PLM ajoute : {len(plm):,} lignes")

    # Garder les têtes de liste avec nuance officielle
    tetes = off[off["Tête de liste"] == "OUI"].copy()
    tetes = tetes.dropna(subset=["Code nuance de liste"])

    # Index par (nom normalisé, commune normalisée)
    index = {}
    for _, row in tetes.iterrows():
        nom = normalize(str(row.get("Nom sur le bulletin de vote", "")))
        prenom = normalize(str(row.get("Prénom sur le bulletin de vote", "")))
        nom_complet = f"{prenom} {nom}".strip()
        commune = normalize_commune(str(row.get("Circonscription", "")))
        code = str(row["Code nuance de liste"]).strip()
        nuance = str(row.get("Nuance de liste", "")).strip()
        if nom and commune and code:
            # Indexer par nom complet + commune normalisée
            index[(nom_complet, commune)] = {"code": code, "label": nuance}
            # Aussi par nom seul
            if (nom, commune) not in index:
                index[(nom, commune)] = {"code": code, "label": nuance}

    print(f"  Index nuances officielles : {len(index):,} têtes de liste")
    return index


def normalize(text):
    """Normalise un nom pour le matching."""
    text = text.upper().strip()
    # Supprimer accents basiques
    for a, b in [("É", "E"), ("È", "E"), ("Ê", "E"), ("Ë", "E"),
                  ("À", "A"), ("Â", "A"), ("Ä", "A"),
                  ("Ô", "O"), ("Ö", "O"), ("Ù", "U"), ("Û", "U"),
                  ("Ü", "U"), ("Ï", "I"), ("Î", "I"), ("Ç", "C"),
                  ("Œ", "OE"), ("Æ", "AE"), ("Ÿ", "Y"), ("Ñ", "N")]:
        text = text.replace(a, b)
    # Garder que alphanum et espaces
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_commune(text):
    """Normalise un nom de commune pour le matching (plus agressif).
    Gère les variantes d'apostrophes mangées (Dascq→Ascq, Laumone→Aumone)."""
    text = normalize(text)
    # Supprimer SECTEUR/ARRONDISSEMENT et codes postaux AVANT les articles
    text = re.sub(r"\bSECTEUR\b", "", text)
    text = re.sub(r"\bARRONDISSEMENT\b", "", text)
    text = re.sub(r"\b\d{5}\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Supprimer les articles/prepositions courants
    for word in ["L ", "LE ", "LA ", "LES ", "D ", "DU ", "DE ", "DES ",
                 "EN ", "SUR ", "SOUS ", "AUX ", "ET ", "SAINT ", "SAINTE ", "ST "]:
        text = text.replace(word, "")
    # Supprimer les prefixes d'apostrophe colles (DASCQ→ASCQ, LAUMONE→AUMONE, LECOLE→ECOLE)
    words = text.split()
    cleaned = []
    for w in words:
        # Si un mot commence par L/D suivi d'une voyelle, c'est probablement l'/d'
        if len(w) > 2 and w[0] in ("L", "D") and w[1] in ("A", "E", "I", "O", "U", "Y"):
            cleaned.append(w[1:])
        else:
            cleaned.append(w)
    text = " ".join(cleaned)
    # Normaliser les ordinaux : 1ER, 2EME, 6EME → juste le numéro
    text = re.sub(r"(\d+)\s*(ER|ERE|EME|E)\b", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate(input_path="data/resultats_partial.json", output_path="data/resultats_municipales_2026.csv"):
    with open(input_path, encoding="utf-8") as f:
        all_results = json.load(f)

    # Charger les nuances officielles
    official = build_official_nuances_index()

    enriched = 0
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

                # 1. Essayer la nuance officielle du Ministère
                nuance_code = None
                nom_cand = c.get("nom", "")

                # Normaliser le nom complet (pas juste le dernier mot)
                nom_full_norm = normalize(nom_cand) if nom_cand else ""

                # Normaliser la commune depuis le slug
                commune_slug = r.get("slug", "")
                commune_norm = normalize_commune(commune_slug.rsplit("-", 1)[0].replace("-", " "))

                if official and nom_full_norm and commune_norm:
                    # Match exact nom complet + commune
                    key = (nom_full_norm, commune_norm)
                    if key in official:
                        off_nuance = official[key]
                        nuance_code = classify_etiquette_from_code(off_nuance["code"])
                        enriched += 1
                    else:
                        # Match : nom (famille) + commune
                        nom_famille = normalize(nom_cand.split()[-1]) if nom_cand and nom_cand.split() else ""
                        key2 = (nom_famille, commune_norm)
                        if key2 in official:
                            off_nuance = official[key2]
                            nuance_code = classify_etiquette_from_code(off_nuance["code"])
                            enriched += 1
                        else:
                            # Match fuzzy : nom contenu + commune contenue
                            for (n, c_off), off_nuance in official.items():
                                commune_match = (c_off == commune_norm
                                    or commune_norm in c_off
                                    or c_off in commune_norm)
                                nom_match = (n in nom_full_norm or nom_full_norm in n)
                                if commune_match and nom_match:
                                    nuance_code = classify_etiquette_from_code(off_nuance["code"])
                                    enriched += 1
                                    break

                # 2. Fallback : classifier depuis l'étiquette du site
                if not nuance_code:
                    nuance_code = classify_etiquette(c.get("etiquette"))

                row["nuance_code"] = nuance_code
                row["nuance_label"] = get_famille(nuance_code)["label"]
                row["nuance_couleur"] = get_famille(nuance_code)["couleur"]
                row["candidat_voix"] = c.get("voix")
                row["candidat_pourcentage"] = c.get("pourcentage")
                row["candidat_elu"] = c.get("elu")
                row["candidat_sieges"] = c.get("sieges")
                csv_rows.append(row)
        else:
            base["nuance_label"] = "Autres / Sans étiquette"
            base["nuance_code"] = "AUT"
            csv_rows.append(base)

    fieldnames = [
        "commune", "slug", "department", "inscrits", "votants",
        "participation_pct", "abstentions", "abstentions_pct", "blancs_nuls",
        "maire_sortant", "nb_candidats",
        "candidat_rang", "candidat_nom", "candidat_etiquette",
        "nuance_code", "nuance_label", "nuance_couleur",
        "candidat_voix", "candidat_pourcentage", "candidat_elu", "candidat_sieges",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"CSV généré : {output_path} ({len(csv_rows):,} lignes, {len(all_results):,} communes)")
    print(f"  Nuances enrichies via CSV officiel : {enriched:,}")


def classify_etiquette_from_code(code):
    """Convertit un code nuance officiel (LDVD, LRN...) en code famille."""
    from nuances_politiques import CODES_NUANCES
    return CODES_NUANCES.get(code, "AUT")


if __name__ == "__main__":
    if os.path.exists("data/resultats_municipales_2026.json"):
        generate("data/resultats_municipales_2026.json")
    elif os.path.exists("data/resultats_partial.json"):
        generate("data/resultats_partial.json")
    else:
        print("Aucun fichier de données trouvé.")
