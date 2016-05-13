from github import Github
import os
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import glob
import requests

#GitHub authentication
#username = "albaizq"  
#password = "albita1993"
#g = Github(username, password)



client_id = GITHUB_APP_ID  # 'bbfc39dd5b6065bbe53b'
client_secret = GITHUB_API_SECRET  # '60014ba718601441f542213855607810573c391e'
# host = 'http://54.172.63.231'
host = 'http://ontoology.linkeddata.es'

import urlparse
import oauth2 as oauth

consumer_key = GITHUB_APP_ID
consumer_secret = GITHUB_API_SECRET

request_token_url = 'https://github.com/login/oauth/access_token'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# Step 1: Get a request token. This is a temporary token that is used for 
# having the user authorize an access token and to sign the request to obtain 
# said access token.

resp, content = client.request(request_token_url, "GET")
if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])

request_token = dict(urlparse.parse_qsl(content))
access_token = request_token['oauth_token']
print "Request Token:"
print access_token




g = Github(access_token)

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

 
