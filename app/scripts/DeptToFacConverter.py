import json
fileFac = open('../../app/scripts/FacultyToDepartment.txt')

facJson = json.load(fileFac)

fileFac.close()

deptToFac = {}
for fac,depts in facJson.items():
    for dept in depts:
        deptToFac[dept] = fac
newFile = open('../../app/scripts/DepartmentToFaculty.txt',"w+")
newFile.write(json.dumps(deptToFac, sort_keys=True,indent=4, separators=(',', ': ')))
newFile.close()
##print (json.dumps(deptToFac, sort_keys=True,indent=4, separators=(',', ': ')))
