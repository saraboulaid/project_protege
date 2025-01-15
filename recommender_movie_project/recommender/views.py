from django.shortcuts import render
from SPARQLWrapper import SPARQLWrapper, JSON
from .models import UserProfile
import matplotlib.pyplot as plt
import json
import io
import graphviz
import base64
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


def truncate_description(description, max_sentences=3):
    sentences = description.split('.')
    truncated = '. '.join(sentences[:max_sentences]) + ('.' if len(sentences[:max_sentences]) > 0 else '')
    return truncated


def recommend_based_on_genre(user_genre):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    SELECT ?film ?title ?image ?abstract WHERE {{
        ?film rdf:type dbo:Film.
        ?film rdfs:label ?title.
        ?film dbo:genre dbr:{user_genre}.
        ?film dbo:thumbnail ?image.
        ?film dbo:abstract ?abstract.
        FILTER(LANG(?title) = "en" && LANG(?abstract) = "en")
    }}
    LIMIT 5
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    films = []
    for result in results.get("results", {}).get("bindings", []):
        title = result["title"]["value"]
        image_url = result.get("image", {}).get("value")
        abstract = result.get("abstract", {}).get("value")

        if image_url:
            # Convertir l'URL pour l'affichage
            image_url = image_url.replace("http://commons.wikimedia.org/wiki/Special:FilePath/",
                                          "https://upload.wikimedia.org/wikipedia/commons/")

        truncated_abstract = truncate_description(abstract)  # Limiter la description à 3 phrases

        films.append({
            "title": title,
            "image": image_url,
            "abstract": truncated_abstract,
            "full_abstract": abstract  # Conserver l'abstract complet pour affichage ultérieur
        })

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

def home(request):
    # Ici, vous pouvez ajouter des données dynamiques si nécessaire
    return render(request, "recommender/index.html")

def about(request):
    # Ici, vous pouvez ajouter des données dynamiques si nécessaire
    return render(request, "recommender/about.html")


def visualize_rdf_graph(request):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Corrected to use __file__
        rdf_file_path = os.path.join(current_dir, 'project_final_amechenoue.rdf')
        graph = Graph()
        graph.parse(rdf_file_path, format="xml")

        # Dictionnaire des prédicats spécifiques à remplacer
        predicate_mapping = {
            "untitled-ontology-8#awards": "Awards",
            "untitled-ontology-8#duree": "Duration",
        }

        # Préparer une liste pour les nœuds et les arêtes
        nodes = []
        edges = []

        for subj, pred, obj in graph:
            pred_str = str(pred)
            label = predicate_mapping.get(pred_str, pred_str.split('/')[-1])

            # Ajouter les nœuds et les arêtes
            nodes.append({"id": str(subj)})
            nodes.append({"id": str(obj)})
            edges.append({"source": str(subj), "target": str(obj), "label": label})

        # Supprimer les doublons dans les nœuds
        unique_nodes = list({node["id"]: node for node in nodes}.values())

        # Construire le graphdata en JSON
        graphdata = {"nodes": unique_nodes, "edges": edges}

        # Passer les données au template
        return render(request, "recommender/rdf_graph.html", {"graph_data": json.dumps(graphdata)})

    except Exception as e:
        return render(request, "recommender/rdf_graph.html", {"error": f"Erreur : {e}"})