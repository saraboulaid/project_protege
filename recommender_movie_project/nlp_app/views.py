from django.shortcuts import render

# Create your views here.
import spacy
from django.shortcuts import render
from .models import AnalyzedText
from rdflib import Graph

# Charger le modèle NLP
nlp = spacy.load("en_core_web_sm")


def analyze_text(request):
    if request.method == "POST":
        input_text = request.POST.get("text", "")

        # Analyse NLP
        doc = nlp(input_text)

        # Extraction des mots-clés
        keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]

        # Reconnaissance d'entités nommées
        entities = {ent.text: ent.label_ for ent in doc.ents}

        # Enregistrer dans la base de données
        analyzed = AnalyzedText.objects.create(
            text=input_text,
            keywords=", ".join(keywords),
            entities=", ".join([f"{k}: {v}" for k, v in entities.items()])
        )

        # Interrogation d'un graphe RDF (exemple simple)
        g = Graph()
        g.parse("https://dbpedia.org/resource/Semantic_Web", format="xml")
        rdf_query = """
        SELECT ?s ?p ?o WHERE {
          ?s ?p ?o .
        } LIMIT 10
        """
        query_results = g.query(rdf_query)

        # Passer les résultats à la vue
        return render(request, "analyze_results.html", {
            "text": analyzed.text,
            "keywords": keywords,
            "entities": entities,
            "rdf_results": query_results
        })

    return render(request, "analyze_text.html")
