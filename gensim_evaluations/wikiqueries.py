"""Automatic generation of test sets for OddOneOut and Topk methods using Wikidata"""
import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client
import re

def construct_query(item, language):
    """Constructs a basic SPARQL query using the 'instance of' property.

    Parameters
    ----------
    item : str 
        Wikidata item
    lang : str
        two-letter wikimedia language code

    Returns
    -------
    str
        the new language appropriate SPARQL query
    str
        a category title corresponding to the query

    """
    # use the 'instance of' property to construct categories
    instance_of = 'P31'
    #Wikidata client
    client = Client()
    entity_label = str(client.get(item).label)
    title = 'instance of '+entity_label   
    query = """#"""+title+"""
        SELECT DISTINCT ?item ?label
        WHERE
        {
        ?item wdt:"""+instance_of+""" wd:"""+item+""".
        # Only keep single words - move back into query if needed
        filter(!contains(?label," "))
        # Language
        ?item rdfs:label ?label filter(lang(?label) = '"""+language+"""').
        }
        ORDER BY ?label"""

    # queries.update({title:query})
    return query, title

# result = construct_query(['Q1369421'])
# print(result)

# returns results of the SPARQL query
def get_results(query, endpoint_url):
    """makes request to Wikidata SPARQL endpoint and returns result of query.

    Parameters
    ----------
    query : str 
        SPARQL query
    endpoint_url : str
        the url for the appropriate SPARQL endpoint

    Returns
    -------
    dict
        the results of the SPARQL query

    """
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

# format SPARQL results for a single category (a single query)
def get_category(query, endpoint_url="https://query.wikidata.org/sparql"):
    """query wikidata to get the list of words belonging to a category

    Parameters
    ----------
    query : str 
        the SPARQL query representing the category to be constructed
    endpoint_url : str, optional
        the appropriate SPARQL endpoint (default Wikidata endpoint)

    Returns
    -------
    list
        a list of words which make up the desired category

    """
    # form the query
    # query = construct_query(item)[0]
    results_dict = get_results(query, endpoint_url)
    values = []
    for result in results_dict["results"]["bindings"]:
        item = result['label']['value'].lower()
        # handle sparql queries that return synonyms '/' separated
        if re.search('/',item):
            # split into two words and append both
            split = item.split('/')
            values.append(split[0])
            values.append(split[1])
        else:
            values.append(item)        
    return values


# create a separate test set for each language from queries.
# test set formatted to be compatible with OddOneOut and Topk
def generate_test_set(items, languages, filename, lemmatized=False, all=False):
    """Generate a complete test set for use with OddOneOut and Topk

    Parameters
    ----------
    query : list of str 
        list of wikidata categories to be included in the test set
    languages : list of str
        list of all wikimedia languages to translate test set into
    filename : str
        location to save test sets

    Returns
    -------
    None
        .txt files will be generated and saved at location specified in filename parameter
    """
    for lang in languages:
        with open(filename+'_'+lang+'.txt','w') as f:
            for i in items:
                # creates a query
                query_obj = construct_query(i,lang)
                query = query_obj[0]
                title = query_obj[1]
                # Get the items in the category formed by current query
                values = get_category(query)
                # print('query=',query)
                # print('title=',title)
                # print('values=',values)
                f.write(':'+title+' ('+lang+')')
                f.write('\n')
                f.writelines('%s ' % item for item in values)
                f.write('\n')
