import urllib, json
modCodes = ["CS1020","CS3230","CS1231"]
data = {}

def getPreReqDataFromURL():
    data = {}
    for code in modCodes:
        url = "http://nusmodmaven.appspot.com/gettree?modName="+code
        response = urllib.urlopen(url);
        data[code] = json.loads(response.read())
    return data
    preReqFile = open('preReqTestData.txt','w')
    preReqFile.write(json.dumps(data, sort_keys=True,indent=4, separators=(',', ': ')))
    preReqFile.close()

def loadPreReqDataFromFile():
    preReqFile = open('preReqTestData.txt')
    data = json.loads(preReqFile.read())
    preReqFile.close()
    return data

def loadModuleList():
    url = "http://api.nusmods.com/2013-2014/2/moduleList.json"
    response = urllib.urlopen(url);
    moduleList = json.loads(response.read())
    return moduleList.keys()

def convertData():
    convertedData = {}
    for testMod in data.values():
        if len(testMod['children']) > 0:
            convertedData[str(testMod['name'])] = [reduceChild(testMod['children'][0])]
        else:
            convertedData[str(testMod['name'])] = [{}]

    return convertedData

def reduceChild(currentChild):
    ##print currentChild
    if not currentChild:
        return currentChild
    currentChildName = str(currentChild.get('name',''))
    ##print currentChildName
    if currentChildName in ["and","or"]:
        return {"name":currentChildName,"children": [reduceChild(c) for c in currentChild['children']]}
    else:
        return {"name":currentChildName}


data = loadPreReqDataFromFile()
## modCodes = loadModuleList()
## data = getPreReqDataFromURL()
finalData = convertData()
preReqFile = open('preReqData.txt','w')
preReqFile.write(json.dumps(finalData, sort_keys=True,indent=4, separators=(',', ': ')))
preReqFile.close()
