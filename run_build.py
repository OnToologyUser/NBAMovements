from github import Github
import os
from SPARQLWrapper import SPARQLWrapper, JSON
import glob


#GitHub authentication
username = "albaizq"  
password = "albita1993"
g = Github(username, password)



for repo in g.get_user().get_repos():
    print repo.name
    repo.create_issue('Travis CI test', repo.name)
 


############################################################################
#############################ACCEPTANCE TEST################################
############################################################################

list_of_files = glob.glob('./*.rq')
# Each file a requirement
for file in list_of_files:
 req = open(file, 'r')
 sparql = SPARQLWrapper("http://dbpedia.org/sparql")
 query =  req.read()
 sparql.setQuery(query )
 sparql.setReturnFormat(JSON)
 results = sparql.query().convert()
 for result in results["results"]["bindings"]:
   print(result["label"]["value"])
   
 repo.create_issue('Acceptance test bug notification', body =  'Ontology created did not support Requiremnt 1 ' , label = 'Acceptance test bug')
 req.close()

############################################################################
################################UNIT TEST###################################
############################################################################

 
