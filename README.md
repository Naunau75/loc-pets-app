# Application de Signalement d'Animaux Perdus

Cette application permet aux utilisateurs de signaler des animaux perdus en fournissant leurs coordonnées GPS et d'autres informations pertinentes. Elle offre également une visualisation des animaux perdus sur une carte interactive. L'application utilise Convex comme plateforme de base de données.

## Fonctionnalités

- Ajout d'animaux perdus avec leurs coordonnées GPS, description, date de perte et espèce
- Visualisation des animaux perdus sur une carte interactive
- API RESTful pour la gestion des données
- Authentification des utilisateurs

## Prérequis

- Python 3.7+
- Un compte Convex et un déploiement Convex

## Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/votre-nom/animaux-perdus-app.git
   cd animaux-perdus-app
   ```

2. Créez un environnement virtuel et activez-le :
   ```
   python -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
   ```

3. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

4. Configurez Convex :
   - Créez un fichier `.env` à la racine du projet
   - Ajoutez votre URL de déploiement Convex : `CONVEX_URL=https://votre-deploiement.convex.cloud`

5. Lancez l'application :
   ```
   python main.py
   ```

L'application sera accessible à l'adresse `http://localhost:8000`.

## Utilisation

### API Endpoints

- `POST /token` : Obtenir un token d'authentification
- `POST /animaux-perdus/` : Ajouter un nouvel animal perdu
- `GET /animaux-perdus/` : Obtenir la liste des animaux perdus
- `GET /animaux-perdus/{animal_id}` : Obtenir les détails d'un animal perdu spécifique
- `GET /carte-animaux-perdus` : Afficher la carte des animaux perdus

### Authentification

Pour utiliser les endpoints protégés, vous devez d'abord obtenir un token en envoyant une requête POST à `/token` avec un nom d'utilisateur et un mot de passe.

### Carte des Animaux Perdus

Accédez à `http://localhost:8000/carte-animaux-perdus` dans votre navigateur pour voir la carte interactive des animaux perdus.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.