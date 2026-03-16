"""
Mapping des étiquettes et nuances politiques - Municipales 2026
Sources : Ministère de l'Intérieur, codes nuances officiels
"""

# Mapping des étiquettes descriptives (grandes communes 1000+ hab)
ETIQUETTES_MAPPING = {
    # Extrême gauche
    "Liste d'extrême-gauche": "EXG",
    "Liste Lutte ouvrière": "EXG",
    "Lutte ouvrière": "EXG",
    "Lutte ouvrière - Le camp des travailleurs": "EXG",
    "LUTTE OUVRIERE - LE CAMP DES TRAVAILLEURS": "EXG",
    "LUTTE OUVRIERE - LE CAMPS DES TRAVAILLEURS": "EXG",
    "NPA": "EXG",
    "NPA -Révolutionnaires": "EXG",

    # La France insoumise
    "Liste de La France insoumise": "FI",
    "La France insoumise": "FI",

    # Parti communiste
    "Liste du Parti communiste": "COM",
    "Parti communiste": "COM",

    # Parti socialiste
    "Liste du Parti socialiste": "SOC",
    "Parti socialiste": "SOC",

    # Ecologistes
    "Liste Les Ecologistes": "ECO",
    "Les Ecologistes": "ECO",
    "Liste écologiste": "ECO",

    # Union de la gauche
    "Liste d'union à gauche": "UG",
    "Liste d'union de la gauche": "UG",

    # Divers gauche
    "Liste divers gauche": "DVG",

    # Union au centre
    "Liste d'union au centre": "UC",

    # Divers centre
    "Liste divers centre": "DVC",

    # Modem
    "Liste du Mouvement Démocrate": "MDM",

    # Renaissance / Ensemble
    "Liste Renaissance": "REN",
    "Renaissance": "REN",
    "Ensemble": "REN",

    # Divers
    "Liste Divers": "DIV",
    "Divers": "DIV",

    # Les Républicains
    "Liste des Républicains": "LR",
    "Les Républicains": "LR",

    # Union de la droite
    "Liste d'union à droite": "UD",
    "Liste d'union de la droite": "UD",

    # Divers droite
    "Liste divers droite": "DVD",

    # Rassemblement National
    "Liste du Rassemblement National": "RN",
    "Rassemblement National": "RN",

    # Reconquête
    "Liste Reconquête !": "REC",
    "Reconquête !": "REC",
    "Reconquête": "REC",

    # Extrême droite
    "Liste d'extrême-droite": "EXD",
    "Liste d'extrême droite": "EXD",

    # Union extrême droite
    "Liste d'union à l'extrême-droite": "EXD",

    # Régionaliste
    "Liste régionaliste": "DIV",

    # UDI
    "Liste de l'Union des Démocrates et des Indépendants": "UC",

    # Horizons
    "Liste Horizons": "DVD",

    # Union des droites
    "Liste d'union des droites pour la République": "UD",

    # Droite souverainiste
    "Liste de droite souverainiste": "DVD",

    # Écologiste (variante)
    "Liste écologiste": "ECO",
}

# Codes nuances officiels du Ministère de l'Intérieur
CODES_NUANCES = {
    # Extrême gauche
    "LEXG": "EXG", "EXG": "EXG",

    # Communiste
    "LCOM": "COM", "COM": "COM", "PC": "COM",

    # France insoumise
    "LFI": "FI", "FI": "FI",

    # Socialiste
    "LSOC": "SOC", "SOC": "SOC", "PS": "SOC",

    # Ecologiste
    "LECO": "ECO", "ECO": "ECO", "LVEC": "ECO", "VEC": "ECO", "EELV": "ECO",

    # Union gauche
    "LUG": "UG", "UG": "UG",

    # Divers gauche
    "LDVG": "DVG", "DVG": "DVG",

    # Divers centre
    "LDVC": "DVC", "DVC": "DVC",

    # Union centre
    "LUC": "UC", "UC": "UC",

    # Modem
    "LMDM": "MDM", "MDM": "MDM",

    # UDI
    "LUDI": "UC", "UDI": "UC",

    # Horizons
    "LHOR": "DVD", "HOR": "DVD",

    # Renaissance
    "LREN": "REN", "REN": "REN",

    # Divers
    "LDIV": "DIV", "DIV": "DIV",

    # Régionaliste
    "LREG": "DIV", "REG": "DIV",

    # Républicains
    "LLR": "LR", "LR": "LR",

    # Union droite
    "LUD": "UD", "UD": "UD",

    # Union des droites pour la République
    "LUDR": "UD",

    # Divers droite
    "LDVD": "DVD", "DVD": "DVD",

    # Droite souverainiste
    "LDRS": "DVD", "LDSV": "DVD",

    # Rassemblement National
    "LRN": "RN", "RN": "RN",

    # Reconquête
    "LREC": "REC", "REC": "REC",

    # Union extrême droite
    "LUXD": "EXD",

    # Extrême droite
    "LEXD": "EXD", "EXD": "EXD",
}

# Familles politiques regroupées
FAMILLES = {
    "EXG": {"label": "Extrême gauche", "couleur": "#BB1840", "ordre": 1},
    "COM": {"label": "Parti communiste", "couleur": "#DD0000", "ordre": 2},
    "FI":  {"label": "La France insoumise", "couleur": "#CC2443", "ordre": 3},
    "SOC": {"label": "Parti socialiste", "couleur": "#FF8080", "ordre": 4},
    "ECO": {"label": "Écologistes", "couleur": "#00C000", "ordre": 5},
    "UG":  {"label": "Union de la gauche", "couleur": "#FF6680", "ordre": 6},
    "DVG": {"label": "Divers gauche", "couleur": "#FFC0C0", "ordre": 7},
    "DVC": {"label": "Divers centre", "couleur": "#FF9900", "ordre": 8},
    "UC":  {"label": "Union au centre", "couleur": "#FFCC00", "ordre": 9},
    "MDM": {"label": "MoDem", "couleur": "#FF9900", "ordre": 10},
    "REN": {"label": "Renaissance", "couleur": "#FFEB00", "ordre": 11},
    "DIV": {"label": "Divers", "couleur": "#C0C0C0", "ordre": 12},
    "LR":  {"label": "Les Républicains", "couleur": "#0066CC", "ordre": 13},
    "UD":  {"label": "Union de la droite", "couleur": "#0044CC", "ordre": 14},
    "DVD": {"label": "Divers droite", "couleur": "#7799FF", "ordre": 15},
    "RN":  {"label": "Rassemblement National", "couleur": "#0D378A", "ordre": 16},
    "REC": {"label": "Reconquête", "couleur": "#1A237E", "ordre": 17},
    "EXD": {"label": "Extrême droite", "couleur": "#404040", "ordre": 18},
    "AUT": {"label": "Autres / Sans étiquette", "couleur": "#999999", "ordre": 19},
}


def classify_etiquette(etiquette):
    """Classifie une étiquette en nuance politique standardisée."""
    if not etiquette:
        return "AUT"

    raw = etiquette.strip()

    # 1. Cherche dans le mapping descriptif exact
    if raw in ETIQUETTES_MAPPING:
        return ETIQUETTES_MAPPING[raw]

    # 2. Cherche dans les codes nuances
    upper = raw.upper()
    if upper in CODES_NUANCES:
        return CODES_NUANCES[upper]

    # 3. Recherche par mots-clés dans l'étiquette (pour les noms de listes locales)
    lower = raw.lower()

    if any(w in lower for w in ["lutte ouvrière", "npa", "révolutionnaire", "ouvriere", "ouvrière"]):
        return "EXG"
    if "insoumise" in lower or "insoumis" in lower:
        return "FI"
    if "communiste" in lower:
        return "COM"
    if "socialiste" in lower:
        return "SOC"
    if any(w in lower for w in ["écologi", "ecologi", "vert"]):
        return "ECO"
    if "rassemblement national" in lower:
        return "RN"
    if "reconquête" in lower or "reconquete" in lower:
        return "REC"
    if "républicain" in lower or "republicain" in lower:
        return "LR"
    if "renaissance" in lower:
        return "REN"
    if "modem" in lower or "mouvement démocrate" in lower:
        return "MDM"

    # Patterns gauche/droite/centre
    if "union" in lower and "gauche" in lower:
        return "UG"
    if "union" in lower and "droite" in lower:
        return "UD"
    if "union" in lower and "centre" in lower:
        return "UC"
    if "gauche" in lower and "divers" not in lower:
        return "UG"
    if "divers gauche" in lower:
        return "DVG"
    if "divers droite" in lower:
        return "DVD"
    if "divers centre" in lower:
        return "DVC"
    if "front populaire" in lower:
        return "UG"

    # 4. Par défaut
    return "AUT"


def get_famille(nuance_code):
    """Retourne les infos de la famille politique."""
    return FAMILLES.get(nuance_code, FAMILLES["AUT"])
