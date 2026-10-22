# BOOTO LUDO AI

Application Streamlit de création d'activités ludiques pour l'apprentissage du français, de l'anglais et de l'espagnol, du CECRL A1 à C2.

## Fonctionnalités
- Activités structurées autour de l'observation, l'écoute, la lecture, l'oral et l'écrit.
- Différenciation et barème transparent sur 20 points.
- Génération à la demande de 20 illustrations originales distinctes, haute définition, chacune signée par bandeau avec « Junior BOOTO WABA ».
- Téléchargement du JSON d'activité et des 20 illustrations dans une archive ZIP.

## Démarrage local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="..."
streamlit run app.py
```

## Déploiement Render
Créer un Web Service depuis ce dépôt, laisser `render.yaml` configurer la compilation et le démarrage, puis ajouter `OPENAI_API_KEY` dans les variables d'environnement Render. La génération d'images requiert un compte API OpenAI autorisé à utiliser le modèle d'images sélectionné et peut entraîner des frais API selon le compte et l'utilisation.

`IMAGE_MODEL` et `TEXT_MODEL` peuvent être définis comme variables d'environnement.
