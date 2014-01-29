import urllib, json, os

sampleModuleCode = "CG3002"

def loadModuleList():

    #moduleList_sem1 = json.loads(urllib.urlopen("http://api.nusmods.com/2013-2014/2/moduleCodes.json").read())
    #moduleList_sem2 = json.loads(urllib.urlopen("http://api.nusmods.com/2013-2014/1/moduleCodes.json").read())

    allModuleCodeList = []
    allModuleCodeTitleList = {}
    currentYearModuleCodeList = {"Sem1": [], "Sem2": []}
    currentYearModuleCodeList_sem1 = json.loads(urllib.urlopen("http://api.nusmods.com/2013-2014/1/moduleList.json").read())
    currentYearModuleCodeList_sem2 = json.loads(urllib.urlopen("http://api.nusmods.com/2013-2014/2/moduleList.json").read())

    for module in data:
        if  module != "ModList":
            allModuleCodeList.append({
                "value": data[module]["ModuleCode"] + " " + data[module]["ModuleTitle"],
                "tokens": data[module]["ModuleTitle"].split(" ")+[data[module]["ModuleCode"]]
            })
            allModuleCodeTitleList[module] = data[module]["ModuleTitle"]

    for module in currentYearModuleCodeList_sem1:
        currentYearModuleCodeList["Sem1"].append({
            "value": module + " " + currentYearModuleCodeList_sem1[module],
            "tokens": currentYearModuleCodeList_sem1[module].split(" ")+[module]
        })

    for module in currentYearModuleCodeList_sem2:
        currentYearModuleCodeList["Sem2"].append({
            "value": module + " " + currentYearModuleCodeList_sem2[module],
            "tokens": currentYearModuleCodeList_sem2[module].split(" ")+[module]
        })

    with open('../data/modInfo_Sample.json', 'w') as outfile:
        json.dump(data[sampleModuleCode], outfile, sort_keys=True, indent=4, encoding="ascii")
    with open('../data/mod_list_all.json', 'w') as outfile:
        json.dump(allModuleCodeList, outfile, sort_keys=True, indent=4)
    with open('../data/modcodes_list_all.json', 'w') as outfile:
        json.dump(allModuleCodeTitleList, outfile, sort_keys=True, indent=4)
    with open('../data/modcodes_list_sem1.json', 'w') as outfile:
        json.dump(currentYearModuleCodeList_sem1, outfile, sort_keys=True, indent=4)
    with open('../data/modcodes_list_sem2.json', 'w') as outfile:
        json.dump(currentYearModuleCodeList_sem2, outfile, sort_keys=True, indent=4)
    with open('../data/mod_list_sem1.json', 'w') as outfile:
        json.dump(currentYearModuleCodeList["Sem1"], outfile, sort_keys=True, indent=4)
    with open('../data/mod_list_sem2.json', 'w') as outfile:
        json.dump(currentYearModuleCodeList["Sem2"], outfile, sort_keys=True, indent=4)


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

data = json.load(open("../data/modInfo.json"), encoding="ascii")
#if not os.path.isfile("../data/mod_list_all.json"):
loadModuleList()
# finalData = convertData(data)
# with open('../data/prereq_data.json', 'w') as outfile:
#     json.dump(finalData, outfile, sort_keys=True, indent=4)

