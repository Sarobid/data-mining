import requests
import json
import pandas as pd

def getListeMarque():
    api_url = "https://alg19o0iek-dsn.algolia.net/1/indexes/prod_supercat_FRfr/query"
    todo = {    "query": "",
    "hitsPerPage": 0,
    "facets": ["marque"],
    "maxValuesPerFacet": 10000,
    "facetFilters": [],
    "responseFields": ["facets"],
    "attributesToHighlight": False
    }
    headers =  {"Content-Type":"application/json",
                "x-algolia-agent": "Algolia for JavaScript (4.10.5); Browser (lite)",
                "x-algolia-api-key": "a55d921ec94745696eaec4a1a9bdf4b0",
                "x-algolia-application-id": "ALG19O0IEK"
                }
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    list = response.json()
    return list['facets']['marque']

def getListeModel(marque):
    queryMar = "marque:"+marque
    api_url = "https://alg19o0iek-dsn.algolia.net/1/indexes/prod_supercat_FRfr/query"
    todo = {    "query": "",
    "hitsPerPage": 0,
    "facets": ["modele"],
    "maxValuesPerFacet": 10000,
    "facetFilters": [[queryMar]],
    "responseFields": ["facets"],
    "attributesToHighlight": False
    }
    headers =  {"Content-Type":"application/json",
                "x-algolia-agent": "Algolia for JavaScript (4.10.5); Browser (lite)",
                "x-algolia-api-key": "a55d921ec94745696eaec4a1a9bdf4b0",
                "x-algolia-application-id": "ALG19O0IEK"
                }
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    list = response.json()
    return list

def getListeMotorolisation(marque,model):
    queryMar = "marque:"+marque
    queryModel = "modele:"+model
    api_url = "https://alg19o0iek-1.algolianet.com/1/indexes/prod_supercat_FRfr/query"
    todo = { 	"query":"",
	"hitsPerPage":0,
	"facets":["type"],
	"maxValuesPerFacet":1000,
	"facetFilters":[[queryMar],
	[queryModel]],
	"responseFields":["facets"],
	"attributesToHighlight":False
    }
    headers =  {"Content-Type":"application/json",
                "x-algolia-agent": "Algolia for JavaScript (4.10.5); Browser (lite)",
                "x-algolia-api-key": "a55d921ec94745696eaec4a1a9bdf4b0",
                "x-algolia-application-id": "ALG19O0IEK"
                }
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    list = response.json()
    return list

def getInformationVehicule(marque,model,type):
    queryMar = "marque:"+marque
    queryModel = "modele:"+model
    queryType = "type:"+type
    api_url = "https://alg19o0iek-dsn.algolia.net/1/indexes/prod_supercat_FRfr/query"
    todo = {"query":"",
		"hitsPerPage":1,
		"facetFilters":[
		[queryMar],
		[queryModel],
		[queryType]],
		"attributesToRetrieve":["carburant","ktypenr","marque","modele","type","url","url_generiques","app_type_debut","app_type_fin"],
		"responseFields":["hits"],
		"attributesToHighlight":False
	}
    headers =  {"Content-Type":"application/json",
                "x-algolia-agent": "Algolia for JavaScript (4.10.5); Browser (lite)",
                "x-algolia-api-key": "a55d921ec94745696eaec4a1a9bdf4b0",
                "x-algolia-application-id": "ALG19O0IEK"
                }
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    try:
        return response.json()
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        print("Contenu de la réponse :")
        print(response.text[:1000])  # affiche les 1000 premiers caractères pour débogage
        return {}  # ou None ou [] selon ce que tu veux que ça retourne

def getListePieces(marque,model,type,keyVehicule):
    api_url = "https://www.mister-auto.com/nwsAjax/ProductListingAlgolia"
    todo = {
			"pageType": "search/algolia",
			"references": [],
			"user_vehicle_id": keyVehicule,
			"withoutAdherence": False
		}
    headers =  {"Content-Type":"application/json",
                "x-request-type": "product-data",
               }
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    list = response.json()
    return list


def getAllProductMarqueVehicule(marque):
    print(marque)
    models = getListeModel(marque)
    resultats = []
    for model in models["facets"]["modele"]:
        types = getListeMotorolisation(marque,model)
        for type in types["facets"]["type"]:
            printage = "{\"marque\":\""+marque+"\", \"modele\":\""+model+"\", \"type\":\""+type+"\"}"
            infVehicles = getInformationVehicule(marque,model,type)
            for vehicule in infVehicles["hits"]:
                keyVehicule = vehicule['ktypenr']
                products = getListePieces(marque,model,type,keyVehicule)
                if products["products"] :
                    for keyProduct, valueProduct in products["products"].items():
                        obj = {"marque-Vehicle":marque,"modele-Vehicle":model,"type-Vehicle":type,"carburant-Vehicle":vehicule['carburant']}
                        obj['productID'] = keyProduct          
                        obj['articleID'] = valueProduct['articleID']
                        obj['artNr'] = valueProduct['artNr']
                        obj['clean_ref'] = valueProduct['clean_ref']
                        obj['libelle'] = valueProduct['libelle']
                        obj['publicPrice'] = valueProduct['price']['publicPrice']
                        obj['salePrice'] = valueProduct['price']['salePrice']
                        obj['devis'] = valueProduct['price']['currency']
                        obj['image_thumbnail'] = valueProduct['image_thumbnail']
                        obj['objectID'] = valueProduct['objectID']
                        obj['typologie'] = valueProduct['typologie']
                        obj['category'] = valueProduct['category']['label']
                        obj['family'] = valueProduct['family']['label']
                        obj['manufacturer'] = valueProduct['manufacturer']['label']
                        caraca_str = "; ".join([f"{c['libelle']}: {c['value']}" for c in valueProduct['caraca'] if 'libelle' in c and 'value' in c])
                        obj['autre_information'] = caraca_str
                        # print(obj)
                        resultats.append(obj)
            print("terminer",printage)
            df = pd.DataFrame(resultats)
            # Afficher un aperçu
            print(df.head())
            # Export en CSV
            df.to_csv(".//data//raw//resultats_"+marque+"-"+str(keyVehicule)+".csv", index=False, encoding="utf-8")
                            
marques = getListeMarque()
# print(marques)
for key, value in marques.items():
    print(key,value)
    getAllProductMarqueVehicule(key)