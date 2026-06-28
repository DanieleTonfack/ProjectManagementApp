# Audit Frontend - état actuel et travail restant

Ce document sert de feuille de route pour le développement du front.
Le backend sera traité séparément, donc ce fichier se concentre uniquement sur l’interface, la navigation et la structure des pages.

## 1. État actuel du front

### Ce qui existe aujourd’hui

- Une seule page d’affichage dans `frontend/src/App.jsx`
- Aucun routage
- Aucun layout public / connecté
- Aucun formulaire d’authentification
- Aucun composant métier réutilisable
- Aucun écran projet, tâche, dashboard ou profil
- Aucune vraie navigation

### Conclusion rapide

Le front est encore au stade de prototype très minimal.
On est sur une base vide à structurer avant d’ajouter les vrais écrans métier.

## 2. Ce que le front doit contenir

### Pages publiques

1. `/` - page d’accueil
2. `/login` - connexion
3. `/register` - inscription
4. `/forgot-password` - mot de passe oublié, optionnel pour la première version

### Pages utilisateur connecté

5. `/dashboard` - vue d’ensemble
6. `/projects` - liste des projets
7. `/projects/new` - création de projet
8. `/projects/:id` - détail projet
9. `/projects/:id/kanban` - tableau Kanban
10. `/projects/:id/settings` - paramètres projet
11. `/projects/:id/members` - membres du projet
12. `/tasks/:id` - détail tâche
13. `/profile` - profil utilisateur
14. `/notifications` - notifications
15. `/activity` - historique d’activité
16. `/settings` - paramètres généraux du compte

## 3. Priorité recommandée

### Phase 1 - MVP

Objectif: avoir une version utilisable avec les parcours essentiels.

1. `/login`
2. `/register`
3. `/dashboard`
4. `/projects`
5. `/projects/new`
6. `/projects/:id/kanban`
7. `/tasks/:id`

### Phase 2 - Version propre et plus complète

Objectif: ajouter les pages de gestion et de collaboration.

1. `/projects/:id`
2. `/projects/:id/settings`
3. `/projects/:id/members`
4. `/profile`
5. `/notifications`
6. `/activity`
7. `/settings`
8. `/forgot-password`

## 4. Ce qu’il reste à faire côté front

### A. Base technique

- Mettre en place le routage
- Créer un layout public
- Créer un layout authentifié
- Gérer les routes protégées
- Organiser le code par dossiers métier

### B. Design system

- Définir les couleurs
- Définir la typographie
- Définir les boutons
- Définir les cartes
- Définir les formulaires
- Définir les badges de statut

### C. Composants réutilisables

- Header
- Sidebar
- Navbar
- Card projet
- Card tâche
- Form input
- Select
- Modal
- Empty state
- Loading state
- Error state

### D. Écrans à construire en priorité

- Accueil
- Connexion
- Inscription
- Dashboard
- Liste des projets
- Création de projet
- Kanban
- Détail tâche

## 5. Fonctionnel attendu par page

### Accueil `/`

- Présentation rapide du produit
- Bouton se connecter
- Bouton créer un compte
- Explication courte des fonctionnalités

### Connexion `/login`

- Email
- Mot de passe
- Bouton de connexion
- Lien vers inscription
- Lien mot de passe oublié

### Inscription `/register`

- Nom ou pseudo
- Email
- Mot de passe
- Confirmation mot de passe
- Bouton de création de compte

### Dashboard `/dashboard`

- Projets récents
- Tâches assignées
- Tâches en retard
- Notifications récentes
- Activité récente

### Projets `/projects`

- Liste des projets
- Carte par projet
- Nom
- Description courte
- Nombre de tâches
- Nombre de membres
- Bouton créer un projet

### Création projet `/projects/new`

- Nom du projet
- Description
- Visibilité
- Membres à inviter, optionnel

### Kanban `/projects/:id/kanban`

- Colonnes à faire, en cours, terminé
- Cartes de tâche
- Drag and drop
- Création, modification, suppression de tâche

### Détail tâche `/tasks/:id`

- Titre
- Description
- Statut
- Priorité
- Deadline
- Assigné
- Projet lié
- Commentaires
- Historique

## 6. Structure conseillée du front

```txt
frontend/src
├── assets
├── components
├── layouts
├── pages
│   ├── public
│   ├── auth
│   ├── dashboard
│   ├── projects
│   ├── tasks
│   └── account
├── routes
├── services
├── styles
└── utils
```

## 7. Ordre de travail conseillé

1. Mettre le router en place
2. Créer les layouts
3. Faire les pages d’authentification
4. Construire le dashboard
5. Construire la liste des projets
6. Construire la page de création de projet
7. Construire le Kanban
8. Construire le détail tâche
9. Ajouter les pages de collaboration et paramètres

## 8. Définition de fini pour le front

Le front peut être considéré comme propre quand:

- les routes existent
- la navigation est claire
- les pages MVP sont accessibles
- les composants sont réutilisables
- l’UI est responsive
- les états vides et d’erreur sont prévus
- le code est organisé par domaines

## 9. Ce qu’il ne faut pas faire maintenant

- Ne pas commencer par le backend
- Ne pas surcharger l’UI avec trop de logique d’un coup
- Ne pas garder le placeholder Vite comme écran principal
- Ne pas mélanger les composants de test avec les vrais écrans

## 10. Résumé

Le front doit évoluer dans cet ordre:

1. socle technique
2. navigation
3. pages MVP
4. composants réutilisables
5. pages avancées
6. intégration backend plus tard

Le meilleur objectif immédiat est de livrer un front propre sur les 7 pages MVP, puis d’étendre progressivement vers la version complète.
