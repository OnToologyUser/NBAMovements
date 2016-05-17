from github import Github
import os
from SPARQLWrapper import SPARQLWrapper, JSON, XML, RDF
import glob
import requests
import myconf
import rdfxml  as rdfxml

#GitHub authentication
client_id = os.environ['github_username']
client_secret = os.environ['github_password']

g = Github(client_id,client_secret)


for repo in g.get_user().get_repos():
 if repo.has_in_collaborators('OnToologyUser'):
  #create labels for acceptance test notifications
  create_labels(repo)
  ##########TESTS#########
  ##Acceptance test
  list_of_files = glob.glob('./*.rq')
  close_old_acc_issues_in_github(repo)
   # Each file has a requirement
  for file in list_of_files:
    results = ont_query(file)
    flag = True
    for result in results["results"]["bindings"]:
     if result == {}:
      flag = False
    #if flag == False:
    # repo.create_issue('Acceptance test bug notification', 'The ontology created did not support the requirement with ID ' + os.path.splitext(os.path.basename(file))[0].split("_")[1] , labels = ['Acceptance test bug'])
   
  ##Unit test
  ont_files = glob.glob('./*.owl')
  for file in ont_files:
    f = open(file, 'r')
    ont = f.read()
    issues_s = get_pitfalls(ont)
    close_old_oops_issues_in_github(repo, file)
    nicer_oops_output(issues_s,file)
    #create_oops_issue_in_github(repo, ont, issues_s)
    
    
 
 
 def ont_query(req_file):
    req = open(req_file, 'r')
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query =  req.read()
    sparql.setQuery(query )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    req.close()
    return results
    
 def create_labels(repo):
   flag_acc = False
   flag_unit = False
   flag_inference = False
   flag_model = False
   flag_metadata = False
   flag_lang = False
   flag_en = False
   for label in repo.get_labels():
    if label.name == "Acceptance test bug":
      flag_acc = True
    elif label.name == "Unit test bug":
      flag_unit =True
    elif label.name == "Inference":
      flag_inference =True
    elif label.name == "Modelling":
      flag_model = True
    elif label.name == "Ontology Language":
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
    """ % (ont_file)
    headers = {'Content-Type': 'application/xml',
               'Connection': 'Keep-Alive',
               'Content-Length': len(xml_content),

               'Accept-Charset': 'utf-8'
               }
    print "will call oops webservice"

    oops_reply = requests.post(url, data=xml_content, headers = headers)
   # print "will get oops text reply"
    oops_reply = oops_reply.text
   # print 'oops reply is: <<' + oops_reply + '>>' 
    #print '<<<end of oops reply>>>'
    
    if oops_reply[:50] == '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">':
        if '<title>502 Proxy Error</title>' in oops_reply:
            raise Exception('Ontology is too big for OOPS')
        else:
            raise Exception('Generic error from OOPS')
    issues_s = output_parsed_pitfalls(ont_file, oops_reply)
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
    # Filter #4
    # Only include data of interest about the issue
    oops_issues_filter4 = {}
    issue_interesting_data = [
        '<http://www.oeg-upm.net/oops#hasName>',
        '<http://www.oeg-upm.net/oops#hasCode>',
        '<http://www.oeg-upm.net/oops#hasDescription>',
        '<http://www.oeg-upm.net/oops#hasNumberAffectedElements>',
        '<http://www.oeg-upm.net/oops#hasImportanceLevel>',
        #'<http://www.oeg-upm.net/oops#hasAffectedElement>',
        '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
    ]
    for i in oops_issues_filter3:
        oops_issues_filter4[i] = {}
        for intda in issue_interesting_data:
            if intda in oops_issues_filter3[i]:
                oops_issues_filter4[i][intda] = oops_issues_filter3[i][intda]
    return oops_issues_filter4, issue_interesting_data
    
 def nicer_oops_output(issues,ont_file):
    sugg_flag = '<http://www.oeg-upm.net/oops#suggestion>'
    pitf_flag = '<http://www.oeg-upm.net/oops#pitfall>'
    warn_flag = '<http://www.oeg-upm.net/oops#warning>'
    num_of_suggestions = issues.count(sugg_flag)
    num_of_pitfalls = issues.count(pitf_flag)
    num_of_warnings = issues.count(warn_flag)
    #create suggestions issue
    if num_of_suggestions > 0 or num_pitfalls > 0 :
     s = " OOPS! has some suggestions to improve the ontology.\n" 
     p = " OOPS! has encountered some pitfalls. \n" 
     p += "The Pitfalls are the following: \n"
     nodes = issues.split("====================")
     suggs = []
     m_pitf = []
     inf_pitf = []
     mod_pitf = []
     met_pitf = []
     lang_pitf = []
     desc = ""
     for node in nodes[:-1]:
        attrs = node.split("\n")
        if pitf_flag in node: 
          for attr in attrs:
           desc = ""
           #minor pitfalls
           if  'hasDescription' in attr:
            desc = attr.replace('hasDescription: ', '')
           if  'hasImportanceLevel: \"Minor\"' in attr and desc != "":
                m_pitf.append(desc)
                break
           #inference pitfalls
           if 'hasCode' in attr:
            if attr == 'P06' or attr == 'P19' or attr == 'P29' or attr == 'P28' or attr == 'P31' or attr == 'P05' or attr == 'P27' or attr == 'P15' or attr == 'P01' or attr == 'P16' or attr == 'P18' or attr == 'P11' or attr == 'P12' or attr == 'P30':
              desc = attr
           if 'hasDescription' in attr and desc != "": 
              inf_pitf.append(attr.replace('hasDescription: ', ''))
           #modelling pitfalls
           if 'hasCode' in attr:
            if attr == 'P03' or attr == 'P14' or attr == 'P24' or attr == 'P25' or attr == 'P26' or attr == 'P17' or attr == 'P23' or attr == 'P10':
              desc = attr
           if 'hasDescription' in attr and desc != "" : 
              mod_pitf.append(attr.replace('hasDescription: ', ''))
           #metadata pitfalls
           if 'hasCode' in attr:
            if attr == 'P39' or attr == 'P40' or attr == 'P38' or attr == 'P41':
              desc = attr
           if 'hasDescription' in attr and desc != "": 
              met_pitf.append(attr.replace('hasDescription: ', ''))
           #language pitfalls
           if 'hasCode' in attr:
            if attr == 'P34' or attr == 'P35':
              desc = attr
           if 'hasDescription' in attr and desc != "": 
              lang_pitf.append(attr.replace('hasDescription: ', ''))
           
        if sugg_flag in node:
            for attr in attrs:
                if 'hasDescription' in attr:
                    suggs.append(attr.replace('hasDescription: ', ''))
                    break
                   
     if len(suggs) > 0:
        s += "The Suggestions are the following:\n"
        for i in range(len(suggs)):
            s += "%d. " % (i + 1) + suggs[i] + "\n"
        labels = ["enhancement"]
        create_oops_issue_in_github(repo, ont_file, s, labels) 
     if len(inf_pitf) > 0:
        i_p = p
        for i in range(len(inf_pitf)):
            i_p += "%d. " % (i + 1) + inf_pitf[i] + "\n"
        labels = ["Unit test bug", "Inference"]
        create_oops_issue_in_github(repo, ont_file, i_p, labels)
     if len(mod_pitf) > 0:
        #p += "The Pitfalls are the following: \n"
        m_p = p
        for i in range(len(mod_pitf)):
            m_p += "%d. " % (i + 1) + mod_pitf[i] + "\n"
        labels = ["Unit test bug", "Modelling"]
        create_oops_issue_in_github(repo, ont_file, m_p, labels)
     if len(met_pitf) > 0:
        #i_p += "The Pitfalls are the following: \n"
        met_p = p
        for i in range(len(met_pitf)):
            met_p += "%d. " % (i + 1) + met_pitf[i] + "\n"
        labels = ["Unit test bug", "Metadata"]
        create_oops_issue_in_github(repo, ont_file, met_p, labels)
     if len(lang_pitf) > 0:
        l_p  = p
        for i in range(len(lang_pitf)):
            l_p += "%d. " % (i + 1) + lang_pitf[i] + "\n"
        labels = ["Unit test bug", "Language"]
        create_oops_issue_in_github(repo, ont_file, l_p, labels)
         
             
    
    
 def close_old_oops_issues_in_github(repo, ont_file):
    print 'will close old issues'
    print repo.get_issues(state='open')
    for i in repo.get_issues(state='open'):
        if i.title == ('OOPS! Evaluation for ' + os.path.splitext(os.path.basename(ont_file))[0]):
            i.edit(state='closed')
            
 def close_old_acc_issues_in_github(repo):
    print 'will close old issues'
    print repo.get_issues(state='open')
    for i in repo.get_issues(state='open'):
        print i.title
        if i.title == ('Acceptance test bug notification'):
            i.edit(state='closed')
            
 def create_oops_issue_in_github(repo, ont_file, oops_issues,label):
    print 'will create an oops issue'
    try:
        repo.create_issue(
            'OOPS! Evaluation for ' + os.path.splitext(os.path.basename(ont_file))[0], oops_issues, labels = label)
    except Exception as e:
        print 'exception when creating issue: ' + str(e)



          
          
 
