# Projet de recommandation de films et visualisation RDF

Ce projet Django est conçu pour recommander des films basés sur les préférences de genre des utilisateurs et pour visualiser un graphe RDF à partir d'un fichier `.rdf`.

## Fonctionnalités

- **Recommandation de films** : L'application recommande des films en fonction du genre préféré de l'utilisateur. Les recommandations sont basées sur une requête SPARQL exécutée contre DBpedia.
- **Gestion du profil utilisateur** : Les utilisateurs peuvent enregistrer leur nom et leurs genres favoris pour recevoir des recommandations de films.
- **Exécution de requêtes SPARQL sur un graphe RDF** : Les utilisateurs peuvent soumettre des requêtes SPARQL personnalisées pour interroger un graphe RDF local.
- **Visualisation d'un graphe RDF** : Le graphe RDF peut être visualisé sous forme de réseau avec des nœuds et des arêtes représentant les relations dans le graphe.
