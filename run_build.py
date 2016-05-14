from github import Github
import os
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import glob
import requests
import myconf

#GitHub authentication
client_id = os.environ['github_username']
client_secret = os.environ['github_password']

g = Github(client_id,client_secret)


for repo in g.get_user().get_repos():
 if repo.has_in_collaborators('OnToologyUser'):
  #create labels for acceptance test notifications
  create_labels(repo)
  ##Acceptance test
  list_of_files = glob.glob('./*.rq')
   # Each file a requirement
   for file in list_of_files:
    results = ont_query(file)
    flag = True
    for result in results["results"]["bindings"]:
     if result == {}:
      flag = False
    if flag == False:
     repo.create_issue('Acceptance test bug notification', 'The ontology created did not support the requirement with ID ' + os.path.splitext(os.path.basename(file))[0].split("_")[1] , labels = ['Acceptance test bug'])
    req.close()
  ##Unit test
  ont_files = glob.glob('./*.owl')
  for file in ont_files:
    ont = open(file, 'r')
    issues_s = get_pitfalls(ont)
    close_old_oops_issues_in_github(repo, ont)
    create_oops_issue_in_github(repo, ont, issues_s)
    
    
 
 
 def ont_query(req_file):
    req = open(req_file, 'r')
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query =  req.read()
    sparql.setQuery(query )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
    
 def create_labels(repo):
     flag_acc = False
   flag_unit = False
   flag_inference = False
   flag_model = False
   flag_metadata = False
   flag_lang = False
   for label in repo.get_labels():
    if label.name == "Acceptance test bug":
      flag_acc = True
    elif label.name == "Unit test":
      flag_unit =True
    elif label.name == "Inference":
      flag_inference =True
    elif label.name = "Modelling":
      flag_model = True
    elif label.name = "Ontology Language":
      flag_lang = True
     
      
   if flag_acc == False:  
    repo.create_label("Acceptance test bug", "F50511")
   if flag_unit == False: 
    repo.create_label("Unit test bug", "F50511")
   if flag_inference == False:
    repo.create_label("Inference",  "F50511")
   if flag_model == False:
    repo.create_label("Modelling",  "F50511")
   if flag_lang == False:
    repo.create_label("Ontology Language",  "F50511")   
    
 def get_pitfalls(ont_file):
  url = 'http://oops-ws.oeg-upm.net/rest'
    xml_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <OOPSRequest>
          <OntologyUrl></OntologyUrl>
          <OntologyContent>%s</OntologyContent>
          <Pitfalls></Pitfalls>
          <OutputFormat></OutputFormat>
    </OOPSRequest>
    """ % (ont_file_content)
    headers = {'Content-Type': 'application/xml',
               'Connection': 'Keep-Alive',
               'Content-Length': len(xml_content),

               'Accept-Charset': 'utf-8'
               }
    print "will call oops webservice"
    oops_reply = requests.post(url, data=xml_content, headers=headers)
    print "will get oops text reply"
    oops_reply = oops_reply.text
    print 'oops reply is: <<' + oops_reply + '>>' 
    print '<<<end of oops reply>>>'
    
    if oops_reply[:50] == '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">':
        if '<title>502 Proxy Error</title>' in oops_reply:
            raise Exception('Ontology is too big for OOPS')
        else:
            raise Exception('Generic error from OOPS')
    issues_s = output_parsed_pitfalls(ont, oops_reply)
    return issues_s
    
 def output_parsed_pitfalls(ont_file, oops_reply):
    issues, interesting_features = parse_oops_issues(oops_reply)
    s = ""
    for i in issues:
        for intfea in interesting_features:
            if intfea in issues[i]:
                val = issues[i][intfea].split('^^')[0]
                key = intfea.split("#")[-1].replace('>', '')
                s += key + ": " + val + "\n"
        s + "\n"
        s += 20 * "="
        s += "\n"
    print 'oops issues gotten'
    return s
    
 def parse_oops_issues(oops_rdf):
    p = rdfxml.parseRDF(oops_rdf)
    raw_oops_list = p.result
    oops_issues = {}

    # Filter #1
    # Construct combine all data of a single elements into one json like format
    for r in raw_oops_list:
        if r['domain'] not in oops_issues:
            oops_issues[r['domain']] = {}
        oops_issues[r['domain']][r['relation']] = r['range']

    # Filter #2
    # get rid of elements without issue id
    oops_issues_filter2 = {}
    for i in oops_issues:
        if '#' not in i:
            oops_issues_filter2[i] = oops_issues[i]

    # Filter #3
    # Only include actual issues (some data are useless to us)
    detailed_desc = []
    oops_issues_filter3 = {}
    for i in oops_issues_filter2:
        if '<http://www.oeg-upm.net/oops#hasNumberAffectedElements>' in oops_issues_filter2[i]:
            oops_issues_filter3[i] = oops_issues_filter2[i]
    
 def close_old_oops_issues_in_github(target_repo, ont_file):
    print 'will close old issues'
    for i in g.get_repo(target_repo).get_issues(state='open'):
        if i.title == ('OOPS! Evaluation for ' + ont_file):
            i.edit(state='closed')
            
 def create_oops_issue_in_github(target_repo, ont_file, oops_issues):
    print 'will create an oops issue'
    try:
        g.get_repo(target_repo).create_issue(
            'OOPS! Evaluation for ' + ont_file, oops_issues)
    except Exception as e:
        print 'exception when creating issue: ' + str(e)



          
          
 
