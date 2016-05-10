#from github import Github
#import os

#username = "albaizq"  
#password = "albita1993"
#g = Github(username, password)
#ontoology_home_name = 'OnToology'



#for repo in g.get_user().get_repos():
#    print repo.name
 #   repo.create_issue('Travis CI test', repo.name)
from SPARQLWrapper import SPARQLWrapper, JSON


file = open('Requisito1.rq', 'r')
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
print file.read()
sparql.setQuery(    """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label
        WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
    """)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["label"]["value"])
