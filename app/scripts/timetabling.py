import json,copy
from time import clock
##Start of class hierarchy

currentSem = 'Sem2'

class TimeSlot(object):
    def __init__(self, day, time):
        self.day = day
        self.time = time

    def __str__(self):
        message = "Day: " + str(self.day) + ","
        message += "Time: " + str(self.time)
        return message

    def __getitem__(self, key):
        if type(key) != int:
            raise TypeError("Index is not of type Integer")
        elif not 0 <= key <= 1:
            raise IndexError("Key is not found!")

        return (self.day if key == 0 else self.time)

    def getDay(self):
        return self.day

    def getTime(self):
        return self.time

    def __eq__(self, timeslot):
        return self.day == timeslot.day and self.time == timeslot.time

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
class Period(object):
    def __init__(self, weeks, *timeslots,**StartEndTimes):

        ## StartEndTimes takes stime and etime as 24hr str times and converts them respective timeslots
        ## timeslots takes in a list of timeslots to directly add to the attribute
        
        if not all(type(timeslot) == TimeSlot for timeslot in timeslots):
            raise TypeError("One or more of the given parameters is not of type TimeSlot")
        
        self.timeslots = []
        
        if len(StartEndTimes) > 0:
            
            stime,etime,day = int(StartEndTimes['stime']),int(StartEndTimes['etime']),StartEndTimes['day']
            
            if etime == 0:
                etime = 2400
            
            while stime < etime:
                self.timeslots.append(TimeSlot(day,stime))
                stime += 30 if stime%100 == 0 else 70

        if(len(timeslots) > 0):
            self.timeslots += list(timeslots)

        self.weeks = weeks

    def addTimeSlot(self, *sources):
        if not all((type(source) == TimeSlot or type(source) == Period) for source in sources):
            raise TypeError("One of the given parameter was not an acceptable source for periods (eg Periods, TimeSlots)")
        
        for source in sources:
            if type(source) == TimeSlot:
                self.periods.append(source)
            elif type(source) == Period:
                for timeslot in source:
                    self.periods.append(timeslot)
    
    def hasSlot(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        return any(t == timeslot for t in self.timeslots)

    def DoClash(self, anotherPeriod):
        if not type(anotherPeriod) == Period:
            raise TypeError("Given parameter is not a Period!")

        #compare the days and the odd/even week setting
        if not (self.timeslots[0][0] == anotherPeriod.timeslots[0][0] and self.weeks == anotherPeriod.weeks):
            return False
        else:
            # check if either the start or the end of one of the periods is between the start and the end of the other
            return (anotherPeriod.timeslots[0][1] <= self.timeslots[0][1] <= anotherPeriod.timeslots[-1][1]) or (
            anotherPeriod.timeslots[0][1] <= self.timeslots[-1][1] <= anotherPeriod.timeslots[-1][1])

    def getStart(self):
        return self.timeslots[0];

    def getEnd(self):
        return self.timeslots[-1];
    
    def __str__(self):
        message = ""
        for t in self:
            #message+="Day: "+str(t[0])+", Time: "+str(t[1])+"\n"
            message += str(t)

        return message

    def __eq__(self,period):
        return self.getStart() == period.getStart() and self.getEnd() == period.getEnd()

    def __iter__(self):
        for timeslot in self.timeslots:
            yield timeslot

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
    
class Lesson(object):
    def __init__(self,group,module,*periods):
        if not all(type(period) == Period for period in periods):
            raise TypeError("One or more of the parameters given is not of type Period")

        self.periods = list(periods)
        self.group = str(group)
        self.module = str(module)
        self.alternatives = []

    def addPeriod(self, *sources):
        if not all((type(source) == Period or issubclass(type(source),Lesson)) for source in sources):
            raise TypeError("One of the given parameter was not an acceptable source for period group (eg Periods, Lessons)")
        
        for source in sources:
            if type(source) == Period:
                self.periods.append(source)
            elif issubclass(type(source),Lesson):
                for period in source:
                    self.periods.append(period)

    def addAlternative(self,*alts):
        if not all(type(alt) == type(self) for alt in alts):
            raise TypeError("One or more of the given parameters is not of the same type as this lesson")

        for alt in alts:
            self.alternatives.append(alt)

    def hasSlot(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")
        return any(period.hasSlot(timeslot) for period in self.periods)

    def getModule(self):
        return self.module

    def getGroup(self):
        return self.group

    def getId(self):
        return self.module + "_" + type(self).__name__ + "_" + self.group

    def getAlternatives(self):
        for lesson in self.alternatives:
            yield lesson

    def getAlternativeCount(self):
        return len(self.alternatives)

    def isAlternative(self,lesson):
        ##return set(self.periods) == set(lesson.periods)
        if len(self.periods) == len(lesson.periods):
            return all(selfp == lessonp for selfp,lessonp in zip(lesson,self))
        else:
            return False

##   Special functions:

    def __str__(self):
        return "ID: "+self.getId()
    
    def __iter__(self):
        for period in self.periods:
            yield period

    def __eq__(self, other):
        return self.getId() == other.getId()
    def __lt__(self, other):
        return self.getId() < other.getId()
    def __le__(self, other):
        return self.getId() <= other.getId()
    def __ne__(self, other):
        return self.getId() != other.getId()
    def __gt__(self, other):
        return self.getId() > other.getId()
    def __ge__(self, other):
        return self.getId() >= other.getId()
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
    
class Lecture(Lesson):
    def __init__(self, group, module, *periods):
        if len(periods) > 0:
            Lesson.__init__(self,group, module, periods[0])
        else:
            Lesson.__init__(self,group, module)

class Tutorial(Lesson):
    def __init__(self, group, module, *periods):
        if len(periods) > 0:
            Lesson.__init__(self,group, module, periods[0])
        else:
            Lesson.__init__(self,group, module)

class Laboratory(Lesson):
    def __init__(self, group, module, *periods):
        if len(periods) > 0:
            Lesson.__init__(self,group, module, periods[0])
        else:
            Lesson.__init__(self,group, module)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
    
class Module(object):
    def __init__(self, code,examDate,dept):
        if not isinstance(code,str):
            raise TypeError("Given code is not of type string!")

        self.lessons = {"Lecture":[],"Tutorial":[],"Laboratory":[]}
        self.code = code
        self.examDate = examDate
        self.dept = dept

    def addLesson(self, lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")

        ## check if this is a second period to an existing lesson
        if self.hasLesson(lesson=lesson):
            internalLesson = self.getLesson(lesson.getId())
            internalLesson.addPeriod(lesson)           
        else:
            if not self.hasAlternativeLesson(lesson):
                self.lessons[lesson.getId().split("_")[1]].append(lesson)

    def removeLesson(self,lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")

        self.lessons[type(lesson).__name__].remove(lesson)

    def removeAllBut(self,lessonType,group):
        ##print(group)
        ##print([lesson.getGroup() for lesson in self.lessons[lessonType]])
        self.lessons[lessonType] = [lesson for lesson in self.lessons[lessonType] if group in [lesson.getGroup()]+[tempLesson.getGroup() for tempLesson in lesson.getAlternatives()]]
            
    def hasAlternativeLesson(self,lesson):
        for self_lesson in self.__iter__(type(lesson)):
            if self_lesson != lesson and self_lesson.isAlternative(lesson):
                self_lesson.addAlternative(lesson)
                return True
        return False

    def hasLesson(self,**lessonData):
        try:
            if issubclass(type(lessonData['lesson']),Lesson):
                lesson = lessonData['lesson']
                return any(lesson == self_lesson for self_lesson in self.lessons[lesson.getId().split("_")[1]])
            else:
                raise TypeError("Given parameter is not a valid lesson")
        except KeyError:
            try:
                if lessonData['lessonid'] !=None:
                    lessonid = lessonData['lessonid']
                    return any(lessonid == self_lesson.getId() for self_lesson in self.lessons[lessonid.split("_")[1]])
                else:
                    raise TypeError("Given 'None' as lesson id")
            except KeyError:
                raise KeyError("No lesson data provided")

    def getChoices(self,setc):
        for lec in (self.__iter__(Lecture,setc) if self.leccount > 0 else [Lecture("Test","Test")]):
            for tut in (self.__iter__(Tutorial,setc) if self.tutcount > 0 else [Tutorial("Test","Test")]):
                for lab in (self.__iter__(Laboratory,setc) if self.labcount > 0 else [Laboratory("Test","Test")]):
                    yield set((lec.getId(),tut.getId(),lab.getId()));

    def getOccupyingLesson(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        for lesson in self:
            if lesson.hasSlot(timeslot):
                yield lesson

    def getClashingLessons(self,lesson):
        conflictSet = set()
        for period in lesson:
            for timeslot in period:
                for lesson in self.getOccupyingLesson(timeslot):
                    conflictSet.add(lesson.getId())
        for lesson in self:
            if(lesson.getId() in conflictSet):
                yield lesson
    
    def getLesson(self, Lid):
        ## only check in the list of lessons that are of the same type (Lec/Tut/Lab)
        for lesson in self.lessons[Lid.split("_")[1]]:
            if lesson.getId() == Lid:
                return lesson

    def getDepartment(self):
        return self.dept
    def getNumChoices(self):
        return (1 if 0 == self.leccount else len(self.lessons["Lecture"])) * (1 if 0 == self.tutcount else len(self.lessons["Tutorial"])) * (1 if 0 == self.labcount else len(self.lessons["Laboratory"]))
    
    def getCode(self):
        return self.code

    def getExamDate(self):
        return self.examDate
    
    ## this function is used to set the count of lessons in the actual module as, to optimise we would be removing some of the lessons prematurely
    def setBaseparams(self):
        for lesson in self:
            if self.hasAlternativeLesson(lesson):
                self.removeLesson(lesson)
        
        self.leccount = len(self.lessons["Lecture"])
        self.tutcount = len(self.lessons["Tutorial"])
        self.labcount = len(self.lessons["Laboratory"])

    def getCompulsoryLessons(self):
        try:
            self.leccount = self.leccount
        except AttributeError:
            self.setBaseparams()
            
        if (self.leccount == 1 and len(self.lessons["Lecture"]) > 0) or len(self.lessons["Lecture"]) == 1:
            yield self.lessons["Lecture"][0]
        if (self.tutcount == 1 and len(self.lessons["Tutorial"]) > 0) or len(self.lessons["Tutorial"]) == 1:
            yield self.lessons["Tutorial"][0]
        if (self.tutcount == 1 and len(self.lessons["Laboratory"]) > 0) or len(self.lessons["Laboratory"]) == 1:
            yield self.lessons["Laboratory"][0]
            
    
    def __eq__(self, other):
        return self.getCode() == other.getCode()
    def __lt__(self, other):
        return self.getCode() < other.getCode()
    def __le__(self, other):
        return self.getCode() <= other.getCode()
    def __ne__(self, other):
        return self.getCode() != other.getCode()
    def __gt__(self, other):
        return self.getCode() > other.getCode()
    def __ge__(self, other):
        return self.getCode() >= other.getCode()

    def __iter__(self, FilterType=object,ExcludeList=set()):
        if FilterType != object:
            for lesson in self.lessons[FilterType.__name__]:
                if lesson.getId() not in ExcludeList:
                    yield lesson
        else:
            for ltype in self.lessons:
                for lesson in self.lessons[ltype]:
                    if lesson.getId() not in ExcludeList :
                        yield lesson;

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
    
class ModuleSet(object):

##    Created = False
    def __init__(self):
    ##        if ModuleSet.Created:
    ##           raise RuntimeError("A moduleset has already been created")
        self.modules = []
        self.count = 0

    def addModule(self, module):
        if not type(module) == Module:
            raise TypeError("The given parameter is not of type Module")
        
        module.setBaseparams()
        self.modules.append(module)
        self.count += 1

    def removeModule(self, code):
        module = self.getModule(code)
        if module:
            self.modules.remove(module)
            self.count -= 1

    def getModuleCount(self):
        return self.count
    
    def getModule(self,code):
        for module in self:
            if module.getCode() == code:
                return module;

    def __iter__(self):
        for module in self.modules:
            yield module

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

##Constants or hardcoded variables
dayToInt = {"MONDAY":1,"TUESDAY":2,"WEDNESDAY":3,"THURSDAY":4,"FRIDAY":5,"SATURDAY":6,"SUNDAY":7}
facChoices = ['ENGINEERING']
modCodeList = {'ST2334':{"Lecture":"SL1","Tutorial":"T1"},'SSA2209':{"Tutorial":"D1"},'EE2024':{"Tutorial":"T9",'Laboratory':'B1'},'EE2023':{},"EE2031":{'Laboratory':'B2'}}
timeRestrictionPairs = [(2,800),(2,900)]
timeRestrictions = []
for day,time in timeRestrictionPairs:
    timeRestrictions.append(TimeSlot(day,time))

def checkModuleAdding(testCode, noTimetableModCount):
    filemods = open('timetabling/modsData.txt')
    fileLtypes = open('timetabling/LtypesData.txt')

    modsJson = json.load(filemods)
    LtypesJson = json.load(fileLtypes)

    filemods.close()
    fileLtypes.close()

    modSet = ModuleSet()
    
    for modData in modsJson:
        modcode = modData['ModuleCode']
        if(modcode != testCode):
            continue
        examDate = modData.get('ExamDate','')
        newmod = Module(modcode,examDate)
        try:
            for lesson in modData['Timetable']:
                if lesson['LessonType'] == 'LABORATORY':
                    newlesson = Laboratory(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=dayToInt[lesson['DayText']]))
                else:
                    print(lesson['LessonType'])
                    newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=dayToInt[lesson['DayText']]))
                newmod.addLesson(newlesson)
        except KeyError:
            noTimetableModCount += 1

    return newmod
        

def loadAllModData():
    fileMods = open('../data/modInfo.json')
    fileLtypes = open('LtypesData.txt')
    fileDeptToFac = open('DepartmentToFaculty.txt')

    modsJson = json.load(fileMods)
    LtypesJson = json.load(fileLtypes)
    deptToFac = json.load(fileDeptToFac)

    fileMods.close()
    fileLtypes.close()
    fileDeptToFac.close()

    modSet = ModuleSet()
    noTimetableModCount = 0

    preReqData = {}
    
    for modData in modsJson:
        modcode = str(modData['ModuleCode'])
        examDate = modData.get('ExamDate','')
        modDept = modData.get('Department','')
        newmod = Module(modcode,examDate,modDept)
        try:
            preReqData[modcode] = 
            for lesson in modData['Timetable'][currentSem]:
                if lesson['LessonType'] == 'LABORATORY':
                    newlesson = Laboratory(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=dayToInt[lesson['DayText']]))
                else:
                    newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=dayToInt[lesson['DayText']]))
                newmod.addLesson(newlesson)
        except KeyError:
            noTimetableModCount += 1
        modSet.addModule(newmod)
    return (modSet,deptToFac)

def generatePossibleModules(modInfoDict,masterModset):
    modList,masterModset = getPreallocatedModuleList(masterModset,modInfoDict)
    masterModset = removeConflicts(modInfoDict.keys(),masterModset)

    clock()
    flag = True
    
    while(flag):
        flag = False
        for mod in modList:
            for lesson in mod.getCompulsoryLessons():
                for mod_del in masterModset:
                    if mod is mod_del:
                        continue
                    lessonList = []
                    for lesson_del in mod_del.getClashingLessons(lesson):
                        lessonList.append(lesson_del)
                        flag = True
                    for lessonToDelete in lessonList:
                        mod_del.removeLesson(lessonToDelete)
        for tempMod in modList:
            if tempMod.getNumChoices() == 0:
                print(tempMod.getCode())
                print("Pre allocated Modules cannot be taken together!!")
    

    possibleMods = [];
    for mod in masterModset:
        if (mod not in modList) and mod.getNumChoices() != 0:
            possibleMods.append(mod.getCode())

    return possibleMods,modList

def getPreallocatedModuleList(masterModset,modInfoDict):
    modList = []
    for mod in masterModset:
        if mod.getCode() in modInfoDict.keys():
            for lessonType,group in modInfoDict[mod.getCode()].items():
                mod.removeAllBut(lessonType,group)
            modList.append(mod)

    return (modList,masterModset)

def removeConflicts(mainModCodeList,masterModSet):
    examSlots = [masterModSet.getModule(modCode).getExamDate() for modCode in mainModCodeList]
    tempModSet = ModuleSet()
    
    for mod in masterModSet:
        if mod.getCode() not in mainModCodeList:
            if hasNoExamConflict(mod,examSlots) and isOfRightFaculty(mod):
                lessonList = []
                for lesson in mod:
                    if isAtWrongTime(lesson):
                        lessonList.append(lesson)
                for lesson in lessonList:
                    mod.removeLesson(lesson)
                if mod.getNumChoices() == 0:
                    tempModSet.addModule(mod)
            else:
                tempModSet.addModule(mod)

    for mod in tempModSet:
        masterModSet.removeModule(mod.getCode())

    return masterModSet

def filterByPrereq(modCodeList,masterModSet):
    modsToRemove = []
    for mod in masterModSet:
        modCode = mod.getCode()
        if not isEligibleByPrereq(modCode,modCodeList):
            modsToRemove.append(modCode)

    for modCode in modsToRemove:
        masterModSet.removeModule(modCode)

    return masterModSet

def isEligibleByPrereq(modCodeToTake,modCodesAlreadyTaken):
    preReqDict = preReqData[modCodeToTake]
    return satisfiesPrereq(preReqDict,modCodesAlreadyTaken)

def hasNoExamConflict(mod,examSlots):
    return mod.getExamDate() == '' or mod.getExamDate() not in examSlots

def isOfRightFaculty(mod):
    return deptToFac[mod.getDepartment()] in facChoices

def isAtWrongTime(lesson):
    return any(lesson.hasSlot(timeslot) for timeslot in timeRestrictions)

def satisfiesPrereq(child, modList):
    if child == []:
        return True
    if child['name'] == "and":
       return all(satisfiesPrereq(c1,modList) for c1 in child['children'])
    elif child['name'] == "or":
       return any(satisfiesPrereq(c1, modList) for c1 in child['children'])
    else:
        return child['name'] in modList

loadedData,deptToFac = loadAllModData()
##modData = copy.deepcopy(loadedData)
    
print("starting now...")
modList,testMods = generatePossibleModules(modCodeList,loadedData)

for mod in testMods:
    for l in mod.getCompulsoryLessons():
        print(l)
fileN = open("test.txt",'w')
for mod in modList:
    fileN.write(mod+'\n')
fileN.close()
##mod = checkModuleAdding("YLS1201", 0)
##mod.setBaseparams()
