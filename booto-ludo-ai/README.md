# BOOTO LUDO AI

Application Streamlit de création d'activités ludiques pour l'apprentissage du français, de l'anglais et de l'espagnol, du CECRL A1 à C2.

## Format et contenus
- Le format scolaire PEP, basé sur le modèle fourni par Junior BOOTO WABA, est sélectionné par défaut : titre PEP, classe/Grado, période, année, nom, cours, date, département/matière, puis exercices numérotés et ressources.
- Une fiche libre est disponible si elle est explicitement sélectionnée.
- Les activités comportent observation visuelle, écoute, lecture, oral, écrit, différenciation et barème sur 20.
- Pour l'écoute, la recherche web cible des pages pédagogiques de diffuseurs/éditeurs reconnus contenant des voix humaines enregistrées. L'application affiche les URLs citées par la recherche, sans fabriquer de lien ni générer de voix de synthèse. L'enseignant vérifie le lecteur et la pertinence avant la classe.
- L'application crée à la demande 20 illustrations originales distinctes, haute définition, chacune signée par bandeau avec « Junior BOOTO WABA ».
- Téléchargement du contenu de l'activité en Markdown et du JSON + 20 images dans une archive ZIP.

## Démarrage local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="..."
streamlit run app.py
```

## Déploiement Render
Créer un Blueprint depuis `render-booto-ludo.yaml`, sélectionner la branche voulue, puis ajouter `OPENAI_API_KEY` dans les variables d'environnement Render. La génération d'images requiert un compte API OpenAI autorisé pour le modèle d'images sélectionné et peut entraîner des frais d'API selon le compte et l'utilisation.

Variables facultatives : `IMAGE_MODEL`, `TEXT_MODEL` et `SEARCH_MODEL`.
