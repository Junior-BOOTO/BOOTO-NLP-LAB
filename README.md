# BOOTO NLP LAB — Version 1.0 (prototype technique)

**Multilingual Text Analyzer | Français · English · Español**

> **État : prototype initial, pas une V1 validée.** Ce dépôt fournit le socle technique et une démonstration expérimentale. Les seuils du cahier des charges ne sont pas encore certifiés sur un jeu de données réel indépendant.

## Objectif
Importer des textes CSV ou PDF et des extraits via l’API Wikimedia, contrôler leur qualité, détecter leur langue (FR/EN/ES), extraire des mots-clés, classer les documents (éducation, technologie, environnement), comparer leur similarité TF-IDF et exporter les résultats.

## Démarrage (Windows / macOS / Linux)

Exécuter avec **Python 3.11 ou 3.12** :

```bash
python -m venv .venv
# Windows PowerShell : .venv\Scripts\Activate.ps1
# macOS / Linux : source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app/main.py
```

Le navigateur ouvre l'application Streamlit. Charger `data/sample/corpus_300_demo.csv` pour découvrir le fonctionnement.

Pour une démonstration sans Streamlit (Python + pandas + scikit-learn) :

```bash
python scripts/run_demo.py
```

## Déploiement sur Render

[**Préparer le déploiement gratuit sur Render**](https://render.com/deploy?repo=https://github.com/Junior-BOOTO/BOOTO-NLP-LAB) · [Guide pas à pas et reprise du projet existant](docs/DEPLOIEMENT_RENDER.md)

Le bouton ouvre la configuration Render ; il ne constitue pas une URL d’application déjà déployée. Vérifier les services existants avant de créer un nouveau service.

Le fichier `render.yaml` configure le tableau de bord Streamlit comme service web Python. Dans Render, choisir **New > Blueprint**, connecter le dépôt `Junior-BOOTO/BOOTO-NLP-LAB`, puis appliquer le Blueprint. Render installera les dépendances et lancera l'application. Le service gratuit peut se mettre en veille après une période d'inactivité.

## Format du CSV

Pour le CSV : la colonne `text` est obligatoire ; `document_id`, `language`, `category` sont facultatives. Encodage UTF-8, limite 5 Mo. Pour le PDF : extraction du texte sélectionnable, une page par document, limite 5 Mo et 1000 pages ; les PDF scannés nécessitent un OCR non inclus. L’API Wikimedia récupère jusqu’à 10 extraits en français, anglais ou espagnol sans clé API.

```csv
document_id,text
1,"Les élèves étudient les langues à l'école."
2,"Software engineers build secure systems."
3,"El bosque necesita protección y conservación."
```

## Statut des fonctions

| Fonction | État du prototype |
|---|---|
| CSV, validation des champs, gestion d'erreurs | Implémenté |
| Import de PDF avec texte sélectionnable | Implémenté ; pas d'OCR pour les scans |
| Recherche via l'API Wikimedia (FR/EN/ES) | Implémentée, sur demande de l'utilisateur |
| Détection linguistique | `langid` si disponible, sinon heuristique de démonstration (non certifiée) |
| Normalisation, tokenisation, mots vides | Implémenté |
| Lemmatisation par modèles linguistiques | Non implémentée (étape suivante) |
| Extraction de mots-clés TF-IDF | Implémenté |
| Classification supervisée TF-IDF + régression logistique | Implémenté, entraîné sur données synthétiques |
| Similarité cosinus TF-IDF | Implémenté, **non sémantique translingue** |
| Dashboard et export CSV | Implémenté via Streamlit (non testé ici) |
| Validation externe 95 % langue / macro-F1 >= 0,75 | **À réaliser sur corpus indépendant** |

## Données

Le jeu `data/sample/corpus_300_demo.csv` contient **300 textes synthétiques construits uniquement pour faire fonctionner la démonstration** : 100 FR / 100 EN / 100 ES, répartis entre trois thèmes. Les formulations artificielles et motifs répétitifs rendent les scores artificiellement optimistes ; **ne pas utiliser ces scores comme mesure de performance réelle**. Aucun texte réel d'élève n'est inclus.

## Structure

```text
app/main.py                Tableau de bord Streamlit
src/booto_nlp/             Traitements réutilisables
data/sample/               Corpus synthétique de démonstration
scripts/run_demo.py        Exécution locale en ligne de commande
tests/                     Tests automatiques
docs/                      Architecture, protocole d'évaluation, cahier des charges
```

## Architecture, évaluation et publication

Lire `docs/ARCHITECTURE.md`, `docs/PLAN_DE_TESTS.md` et `docs/CAHIER_DES_CHARGES_V1.md`.

Le statut des vérifications et les travaux restant à effectuer sont dans `docs/ETAT_ET_PROCHAINES_ETAPES.md`.

## Confidentialité et licences

Pas de transmission automatique à une API distante par le cœur applicatif. Ne pas charger de données personnelles sans droits et protections adéquats. Vérifier les licences des jeux de données externes. **Aucune licence open source n'est fournie pour le moment ; la réutilisation du code n'est donc pas accordée par une licence.**

## Auteur / portefeuille

Projet de portfolio de **Junior BOOTO Waba** — Pôle Python & Data Science ; les futures extensions FLE constituent un autre module du laboratoire.
