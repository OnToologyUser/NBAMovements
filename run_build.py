from github import Github
import os
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import glob


#GitHub authentication
username = "albaizq"  
password = "albita1993"
g = Github(username, password)



############################################################################
#############################ACCEPTANCE TEST################################
############################################################################
for repo in g.get_user().get_repos():
 list_of_files = glob.glob('./*.rq')
 print list_of_files
 # Each file a requirement
 for file in list_of_files:
  req = open(file, 'r')
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  query =  req.read()
  sparql.setQuery(query )
  
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  flag = True
  for result in results["results"]["bindings"]:
   print result
   if result == {}:
    flag = False
  #flag = True
  if flag == False:
   repo.create_issue('Acceptance test bug notification', 'Ontology created did not support ' + os.path.splitext(os.path.basename(file))[0] , labels = ['bug'])
  req.close()

############################################################################
################################UNIT TEST###################################
############################################################################

 
