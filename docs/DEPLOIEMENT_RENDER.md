# Déployer BOOTO NLP LAB sur Render

Dépôt de référence : https://github.com/Junior-BOOTO/BOOTO-NLP-LAB

## Reprendre le projet existant

Ouvrir https://dashboard.render.com/project/prj-dbckkfvb9u1s73c0iqqg.
Si un service BOOTO NLP LAB existe déjà, ouvrir ses paramètres et vérifier le dépôt et les valeurs ci-dessous. Utiliser ensuite **Manual Deploy > Deploy latest commit**, plutôt que créer un doublon. Si le service est géré par un Blueprint, synchroniser son Blueprint existant.

Si le projet est vide, créer un **Web Service**, connecter le dépôt dédié et reprendre les valeurs ci-dessous. Le lien Blueprint prérempli constitue une autre voie pour une première création : https://render.com/deploy?repo=https://github.com/Junior-BOOTO/BOOTO-NLP-LAB. Ne pas utiliser les deux voies pour créer deux services.

## Valeurs à vérifier

| Champ | Valeur |
| --- | --- |
| Dépôt | Junior-BOOTO/BOOTO-NLP-LAB |
| Branche | main |
| Runtime | Python |
| Root Directory | Laisser vide |
| Plan / Instance Type | Free |
| Build Command | `python -m pip install -r requirements.txt` |
| Start Command | `python -m streamlit run app/main.py --server.address 0.0.0.0 --server.port $PORT --server.headless true` |
| Health Check Path | `/_stcore/health` |
| PYTHON_VERSION | `3.12.8` |
| OMP_NUM_THREADS | `1` |
| OPENBLAS_NUM_THREADS | `1` |

Le Blueprint `render.yaml` contient ces paramètres. Aucune clé d'API, base de données ni disque persistant n'est nécessaire. Garder le type Free ; ne pas sélectionner une offre payante. Si Render exige une carte, interrompre la création et vérifier le plan sélectionné : l'absence de demande de carte n'est pas garantie pour tous les comptes.

## Vérifier après déploiement

1. Attendre le statut **Live** et copier l'URL réellement fournie par Render. Ne pas déduire l'URL du nom du service.
2. Ouvrir l'application : les 300 textes synthétiques doivent se charger.
3. Vérifier les onglets Langues, Thèmes, Mots-clés et Similarité.
4. Exporter les résultats CSV, puis essayer un petit CSV UTF-8 contenant une colonne `text`.
5. Vérifier que `https://<adresse-attribuée>/_stcore/health` renvoie `ok`. Ce contrôle vérifie le serveur ; les étapes précédentes vérifient l'application.

Le service Free se met en veille après 15 minutes sans trafic et son réveil peut prendre environ une minute. Les fichiers locaux ne sont pas durables. Télécharger les résultats avant de fermer la session.

## En cas d'erreur

- **ModuleNotFoundError** : vérifier le dépôt dédié, la racine vide et la commande d'installation.
- **No open ports detected** : vérifier `--server.address 0.0.0.0 --server.port $PORT`.
- **Fichier de corpus introuvable** : vérifier que `data/sample/corpus_300_demo.csv` figure dans le commit déployé.
- **Échec de build** : consulter les logs Build ; **échec au démarrage** : consulter les logs du service. Copier le message exact pour le diagnostic.

Documentation officielle : https://render.com/docs/free · https://render.com/docs/health-checks · https://render.com/docs/blueprint-spec
