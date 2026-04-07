# TP Backend — Construire une messagerie simple avec FastAPI

## Contexte

Vous allez développer une petite application de **messagerie non instantanée**.  
L’objectif est de permettre à des utilisateurs de :

- créer un compte,
- se connecter,
- envoyer des messages à d’autres utilisateurs,
- consulter leur boîte de réception,
- lire leurs messages envoyés,
- marquer un message comme lu.

Dans cette première version, toute l’application repose sur **HTTP**.  
À la fin du TP, vous devrez analyser ce que ce modèle permet… et surtout ce qu’il ne permet pas de faire facilement lorsqu’on veut du **temps réel**.

## Objectifs pédagogiques

Ce TP doit vous permettre de manipuler :

- **FastAPI** pour construire une API REST,
- **Pydantic** pour valider les données d’entrée et de sortie,
- **SQLModel** pour définir les modèles et accéder à la base,
- **SQLite** pour stocker les données,
- les principes classiques d’une API backend :
  - routes,
  - schémas de validation,
  - persistance,
  - gestion d’erreurs,
  - séparation entre modèles de base de données et modèles d’API.

## Fonctionnalités attendues

Votre API doit permettre les actions suivantes.

### Gestion des utilisateurs
- Créer un utilisateur
- Lister les utilisateurs
- Consulter un utilisateur par son identifiant

### Gestion des messages
- Envoyer un message
- Consulter la boîte de réception d’un utilisateur
- Consulter les messages envoyés par un utilisateur
- Consulter le détail d’un message
- Marquer un message comme lu

## Contraintes de modélisation

### Utilisateur
Un utilisateur possède au minimum :

- un identifiant,
- un nom d’utilisateur unique,
- une adresse e-mail.

### Message
Un message possède au minimum :

- un identifiant,
- un expéditeur,
- un destinataire,
- un sujet,
- un contenu,
- une date d’envoi,
- un statut `lu / non lu`.

## Travail demandé

## Partie 1 — Mise en place du projet

Créer un projet FastAPI avec une base SQLite.

Le projet devra contenir au minimum :

- un fichier principal `main.py`,
- un modèle SQLModel pour les utilisateurs,
- un modèle SQLModel pour les messages,
- une initialisation automatique de la base au démarrage.

## Partie 2 — Définition des schémas

Mettre en place des schémas adaptés pour séparer :

- les données reçues en entrée,
- les données enregistrées en base,
- les données renvoyées par l’API.

On attend notamment :

- un schéma de création d’utilisateur,
- un schéma de lecture d’utilisateur,
- un schéma de création de message,
- un schéma de lecture de message.

Vous devez utiliser **Pydantic / SQLModel** proprement pour éviter d’exposer inutilement tous les champs de la base.

## Partie 3 — API utilisateurs

Implémenter les routes suivantes :

### Créer un utilisateur
`POST /users`

Exemple de corps de requête :

```json
{
  "username": "alice",
  "email": "alice@example.com"
}
```

Contraintes :
- le nom d’utilisateur doit être unique,
- l’e-mail doit être valide.

Exemple avec `httpie` :

```bash
http POST :8000/users username=alice email=alice@example.com
```

### Lister les utilisateurs
`GET /users`

Exemple avec `httpie` :

```bash
http GET :8000/users
```

### Obtenir un utilisateur
`GET /users/{user_id}`

Exemple avec `httpie` :

```bash
http GET :8000/users/1
```

Gestion d’erreurs attendue :
- retourner une erreur adaptée si l’utilisateur n’existe pas,
- retourner une erreur adaptée si le nom d’utilisateur existe déjà.

## Partie 4 — API messages

Implémenter les routes suivantes.

### Envoyer un message
`POST /messages`

Exemple :

```json
{
  "sender_id": 1,
  "receiver_id": 2,
  "subject": "Bonjour",
  "body": "Peux-tu m'envoyer le document ?"
}
```

Contraintes :
- l’expéditeur doit exister,
- le destinataire doit exister,
- un utilisateur ne peut pas s’envoyer un message à lui-même,
- le sujet et le corps ne doivent pas être vides.

Exemple avec `httpie` :

```bash
http POST :8000/messages sender_id:=1 receiver_id:=2 subject="Bonjour" body="Peux-tu m'envoyer le document ?"
```

### Voir la boîte de réception d’un utilisateur
`GET /users/{user_id}/inbox`

Cette route doit retourner tous les messages reçus par l’utilisateur, idéalement triés du plus récent au plus ancien.

Exemple avec `httpie` :

```bash
http GET :8000/users/2/inbox
```

### Voir les messages envoyés par un utilisateur
`GET /users/{user_id}/sent`

Exemple avec `httpie` :

```bash
http GET :8000/users/1/sent
```

### Voir le détail d’un message
`GET /messages/{message_id}`

Exemple avec `httpie` :

```bash
http GET :8000/messages/1
```

### Marquer un message comme lu
`PATCH /messages/{message_id}/read`

Cette route doit modifier l’état du message.

Exemple avec `httpie` :

```bash
http PATCH :8000/messages/1/read
```

## Partie 5 — Filtres et améliorations HTTP

Ajouter au moins deux améliorations parmi les suivantes :

- filtrer la boîte de réception pour n’afficher que les messages non lus,
- ajouter une pagination sur les listes,
- rechercher un message par mot-clé dans le sujet,
- supprimer un message,
- compter le nombre de messages non lus d’un utilisateur.

Exemples possibles :

- `GET /users/{user_id}/inbox?unread_only=true`
- `GET /users/{user_id}/inbox?limit=20&offset=0`
- `GET /users/{user_id}/inbox?search=projet`

Exemples avec `httpie` :

```bash
http GET ':8000/users/2/inbox?unread_only=true'
http GET ':8000/users/2/inbox?limit=20&offset=0'
http GET ':8000/users/2/inbox?search=projet'
```

## Partie 6 — Tests manuels

Tester l’API avec Swagger UI ou un client HTTP.

Vous devez être capables de démontrer le scénario suivant :

1. création de deux utilisateurs,
2. envoi de plusieurs messages entre eux,
3. consultation de la boîte de réception,
4. lecture d’un message,
5. mise à jour de son statut,
6. vérification qu’il apparaît comme lu.

Exemple de scénario complet avec `httpie` :

```bash
http POST :8000/users username=alice email=alice@example.com
http POST :8000/users username=bob email=bob@example.com

http POST :8000/messages sender_id:=1 receiver_id:=2 subject="Bonjour" body="Salut Bob"
http POST :8000/messages sender_id:=2 receiver_id:=1 subject="Re: Bonjour" body="Salut Alice"

http GET :8000/users/1/inbox
http GET :8000/users/2/inbox

http GET :8000/messages/1
http PATCH :8000/messages/1/read
http GET :8000/messages/1
```

## Travail d’analyse demandé en fin de TP

Répondre brièvement aux questions suivantes :

### 1. En quoi HTTP convient-il bien à cette application ?
Donner des exemples d’actions qui fonctionnent très bien avec un modèle requête/réponse.

### 2. Quelles limites apparaissent si l’on veut une vraie messagerie “vivante” ?
Par exemple :

- comment savoir immédiatement qu’un nouveau message est arrivé ?
- comment mettre à jour automatiquement l’interface sans recharger la page ?
- comment notifier en direct qu’un message a été lu ?

### 3. Quelle solution pourrait-on introduire ensuite ?
Expliquer en quelques lignes pourquoi **WebSocket** serait une évolution naturelle pour ajouter du temps réel.

## Livrables attendus

Vous rendrez :

- le code source du projet,
- une base SQLite fonctionnelle,
- une courte note expliquant :
  - vos choix de modélisation,
  - les routes disponibles,
  - les limites de votre solution HTTP.

## Conseils de conception

- Commencez simple.
- Faites fonctionner d’abord les routes principales avant d’ajouter les filtres.
- Séparez bien :
  - modèle base de données,
  - schéma de création,
  - schéma de lecture.
- Soignez les codes de statut HTTP :
  - `200 OK`
  - `201 Created`
  - `404 Not Found`
  - `400 Bad Request`

## Extension possible pour la séance suivante

Une fois cette version terminée, on pourra se poser la question suivante :

> “Comment faire pour que le destinataire soit informé immédiatement qu’il a reçu un nouveau message, sans avoir à relancer une requête HTTP en boucle ?”

Ce sera l’occasion d’introduire :

- le **polling** comme solution imparfaite,
- puis les **WebSockets** comme solution plus adaptée au temps réel.
