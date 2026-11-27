# affichage.py
# Textes et couleurs communs à toutes les pages.
# Pas de Streamlit ici : on renvoie du texte, les pages l'affichent avec st.caption.

# en dessous de 50 répondants, on n'affiche pas de chiffre
SEUIL = 50

# couleurs communes, celles des TP
GRIS = "#BDBDBD"    # le contexte
ACCENT = "#C2410C"  # ce qui compte, une seule couleur forte
ENCRE = "#1A2331"   # le texte


def assez_de_reponses(df):
    # True si le groupe est assez grand pour afficher un chiffre
    return len(df) >= SEUIL


def legende_population(df, qui, annee):
    # phrase à mettre sous chaque figure : qui, quelle année, combien de répondants
    # f"{3376:,}" donne "3,376" : on remplace la virgule par une espace -> "3 376"
    nombre = f"{len(df):,}".replace(",", " ")
    return f"{qui} · {annee} · {nombre} répondants · volontaires, non représentatifs de tous les développeurs"