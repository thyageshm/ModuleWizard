import urllib, json, os

def loadModuleList():
    moduleList = json.loads(urllib.urlopen("http://api.nusmods.com/2013-2014/2/moduleCodes.json").read())
    newModuleList = []
    for module in moduleList:
        print module
        newModuleList.append({
            "value": data[module]["ModuleCode"] + " " + data[module]["ModuleTitle"],
            "tokens": data[module]["ModuleTitle"].split(" ")+[data[module]["ModuleCode"]]
        })

    with open('../data/mod_list.json', 'w') as outfile:
        json.dump(newModuleList, outfile, sort_keys=True, indent=4)

    moduleCodeList = json.loads(urllib.urlopen("http://api.nusmods.com/2013-2014/2/moduleList.json").read())
    with open('../data/modcodes_list.json', 'w') as outfile_list:
        json.dump(moduleCodeList, outfile_list, sort_keys=True, indent=4)


# def reduceChild(currentChild):
#     if currentChild["name"] in ["and", "or"]:
#         new_data = []
#         for child in currentChild["children"]:
#             new_data += reduceChild(child)
#         return new_data if currentChild["name"] == "and" else [new_data]
#     elif data.has_key(currentChild["name"]) and isinstance(data[currentChild["name"]]["Preclusion"], list):
#         return [currentChild["name"]]+data[currentChild["name"]]["Preclusion"]
#     else:
#         return [currentChild["name"]]
#
#
# def convertData(data):
#     new_data = {}
#     for mod in modCodes:
#         newData = []
#         for child in data[mod]["Tree"]["children"]:
#             newData += reduceChild(child)
#         new_data[mod] = newData
#     print new_data
#     return new_data
#

# def convertData():
#     convertedData = {}
#     for testMod in data.values():
#         if len(testMod['children']) > 0:
#             convertedData[str(testMod['name'])] = [reduceChild(testMod['children'][0])]
#         else:
#             convertedData[str(testMod['name'])] = [{}]
#
#     return convertedData
#
# def reduceChild(currentChild):
#     ##print currentChild
#     if not currentChild:
#         return currentChild
#     currentChildName = str(currentChild.get('name',''))
#     ##print currentChildName
#     if currentChildName in ["and","or"]:
#         return {"name":currentChildName,"children": [reduceChild(c) for c in currentChild['children']]}
#     else:
#         return {"name":currentChildName}

data = json.load(open("../data/modInfo.json"))
if not os.path.isfile("../data/mod_list.json"):
    loadModuleList()
# finalData = convertData(data)
# with open('../data/prereq_data.json', 'w') as outfile:
#     json.dump(finalData, outfile, sort_keys=True, indent=4)

