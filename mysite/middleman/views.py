from django.http import HttpResponse
from django.shortcuts import render
from pyes import *
from django.utils import simplejson
from django.template.loader import render_to_string

#simple view file that peforms queries on elasticsearch
def filter(request):
        # connect to elastic search
        # elastic search has log files in json format stored and indexed
        conn = ES('127.0.0.1:9200')
        conn.default_indices=["logstash-2012.07.20"]
        conn.refresh()
        #set up for a query to return mobile phones count(agent field in search engine)
        query_1 = MatchAllQuery()
        query_1 = query_1.search()
        # we only want 4 agent fields with the highest count returned
        query_1.facet.add_term_facet(field='agent',size=4)
        # perform query on data to return mobile phones with the highest count
        results = conn.search(query = query_1)
        results_filter= results.facets['agent']['terms'][0]['term']
        if results_filter == '"Java/1.5.0_15"' :
          results.facets.agent.terms.pop(0)
        else :
          results.facets.agent.terms.pop(3)
          
        output= [{},{},{}] #list to store the output 
        count=0
        #for each mobile phone returned in the list results , return a hsitogram showing the usage over time .
        for item in results.facets['agent']['terms']:
           mystr = item['term']
           mystr = mystr[:mystr.find('/') ]
           mystr = mystr[1:]
           mystr2 = "*" + mystr +"*"
           query_4 = WildcardQuery("agent", mystr2)
           query_4  = query_4.search()
           query_4.facet.facets.append(facets.DateHistogramFacet('date_facet',field='timestamp',interval='hour'))
           results4 = conn.search(query = query_4)
           output[count]={u'term' : mystr ,u'entries' : results4.facets.date_facet.entries}
           count = count + 1
        output[0]['entries'].pop(len(output[0]['entries'])-1)
        #convert output to json format
        entry = simplejson.dumps(output)
        #finals=output
        #send output to stream.html for visalization
        return render(request, 'stream.html', {'finals': output,'results':results,'entry':entry})
       
