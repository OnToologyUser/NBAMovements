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
 if repo.has_in_collaborators('OnToologyUser'):
  #create labels
   flag2 = False
   for label in repo.get_labels():
    if label.name == "Acceptance test bug":
      flag2 = True
   if flag2 == False:  
    repo.create_label("Acceptance test bug", "F50511")
    
   list_of_files = glob.glob('./*.rq')
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
     if result == {}:
      flag = False
  
    if flag == False:
     repo.create_issue('Acceptance test bug notification', 'The ontology created did not support the requirement with ID ' + os.path.splitext(os.path.basename(file))[0].split("_")[1] , labels = ['Acceptance test bug'])
    req.close()

############################################################################
################################UNIT TEST###################################
############################################################################

 
