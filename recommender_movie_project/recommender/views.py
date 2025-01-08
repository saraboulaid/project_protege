from django.shortcuts import render
from SPARQLWrapper import SPARQLWrapper, JSON
from .models import UserProfile
import logging
from rdflib import Graph
# Charger le graphe RDF au démarrage
import os
current_dir = os.path.dirname(os.path.abspath(__file__))  # Obtenir le répertoire actuel
rdf_file_path = os.path.join(current_dir, 'project_final_amechenoue.rdf')
graph = Graph()
graph.parse(rdf_file_path, format="xml")

# graph.parse("project_final_amechenoue.rdf", format="xml")  # Remplacez par le chemin de votre fichier RDF


logger = logging.getLogger(__name__)
def profile(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        username = request.POST.get("username")
        favorite_genre = request.POST.get("favorite_genre")
        favorite_authors = request.POST.get("favorite_authors", "")  # Facultatif, peut être vide

        if username and favorite_genre:  # Assurez-vous que le nom d'utilisateur et le genre sont fournis
            # Créer ou mettre à jour le profil utilisateur
            user, created = UserProfile.objects.get_or_create(username=username)
            user.favorite_genres = favorite_genre  # Mettre à jour les genres favoris
            user.favorite_authors = favorite_authors  # Mettre à jour les auteurs favoris (facultatif)
            user.save()

            # Obtenir les recommandations de films basées sur le genre
            films = recommend_based_on_genre(favorite_genre)

            # Rendre la page avec les films recommandés
            return render(request, "recommender/recommendations.html", {"username": username, "films": films})

        else:
            # Si un champ est manquant, afficher un message d'erreur
            return render(request, "recommender/profile.html", {"error": "Veuillez remplir tous les champs requis."})

    return render(request, "recommender/profile.html")



def recommend_based_on_genre(user_genre):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    SELECT ?film ?title WHERE {{
        ?film rdf:type dbo:Film.
        ?film rdfs:label ?title.
        ?film dbo:genre dbr:{user_genre}.
        FILTER(LANG(?title) = "en")
    }}
    LIMIT 5
    """
    logger.info(f"SPARQL Query: {query}")  # Log de la requête
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except Exception as e:
        logger.error(f"Erreur SPARQL : {e}")
        return []

    films = []
    for result in results.get("results", {}).get("bindings", []):
        logger.info(f"Film trouvé : {result['title']['value']}")
        films.append(result["title"]["value"])

    return films

def sparql_query(request):
    if request.method == "POST":
        query = request.POST.get("sparql_query", "").strip()  # Récupérer la requête de l'utilisateur

        if not query:
            return render(request, "recommender/sparql_query.html", {"error": "Veuillez entrer une requête SPARQL."})

        try:
            # Exécuter la requête sur le graphe RDF
            results = graph.query(query)

            # Préparer les résultats pour l'affichage
            formatted_results = [list(row) for row in results]
            return render(request, "recommender/sparql_query.html", {"results": formatted_results, "query": query})

        except Exception as e:
            logger.error(f"Erreur SPARQL : {e}")
            return render(request, "recommender/sparql_query.html", {"error": f"Erreur lors de l'exécution de la requête : {e}"})

    return render(request, "recommender/sparql_query.html")