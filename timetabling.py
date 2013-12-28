import json,copy
from time import clock
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

    def addTimeSlot(self, *source):
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
        self.group = group
        self.module = module
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

        self.lessons[type(lesson).__name__].remove(lesson);

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
        for period in lesson:
            for timeslot in period:
                for lesson in self.getOccupyingLesson(timeslot):
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
        if(code == "BN4101R"):
            print(module)
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
    
class Timetable(object):
    def __init__(self,source=None):
        ##create a timetable with day names as rows and the int representation of the 24 hr clock as columns
        
        Days = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
        Times = []
        stime = 600
        while stime <= 2400:
                Times.append(stime)
                stime += 30 if stime%100 == 0 else 70
        
        self.field = {Day:{Time:[] for Time in Times} for Day in Days}
        if source !=None:
            if type(source) == ModuleSet:
                self.addModuleSet(source)
            elif type(source) == Module:
                self.addModule(Module)
            else:
                raise TypeError("Given source parameter is not of type Module or ModuleSet")

    def __iter__(self):
        for day in self.field.values():
            yield day;
    
    def getSlot(self, day, time):    
        return self.field[day][time]

    def __getitem__(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        return self.getSlot(timeslot.getDay(), timeslot.getTime())

    ## combine these functions using polymorphism
    def addModuleSet(self, moduleset):
        if not type(moduleset) == ModuleSet:
            raise TypeError("The given parameter is not of type ModuleSet")

        for module in moduleset:
            self.addModule(module)

    def addModule(self, module):
        if not type(module) == Module:
            raise TypeError("The given parameter is not of type Module")

        for lesson in module:
            self.addLesson(lesson)

    def addLesson(self, lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not of type Lesson")
        for period in lesson:
            self.addLessonP(period, lesson)

    def addLessonP(self, period, lesson):
        if not type(period) == Period:
            raise TypeError("Given parameter is not of type Period")
        for timeslot in period:
            self.addLessonT(timeslot, lesson)

    def addLessonT(self, timeslot, lesson):
        if not type(timeslot) == TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        self[timeslot].append(lesson)

    def removeLesson(self,lesson):
        for period in lesson:
            self.removeLessonP(period,lesson)

    def removeLessonP(self, period, lesson):
        for timeslot in period:
            self.removeLessonT(timeslot, lesson)

    def removeLessonT(self, timeslot, lesson):
        Slot = self[timeslot]

        for self_lesson in Slot:
            if self_lesson == lesson:
                Slot.remove(lesson);

    def getLessonsCount(self, timeslot):
        return len(self[timeslot])

    def print(self):
        for day in self.field:
            print (day)
            for time in self.field[day]:
                if len(self.field[day][time]) > 0:
                    print(time,len(self.field[day][time]))
                    ##for lesson in self.field[day][time]:
                      ##  print(lesson.getId())

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

def checkModuleAdding(testCode):
    filemods = open('modsData.txt')
    fileLtypes = open('LtypesData.txt')

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
                    newlesson = Laboratory(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=lesson['DayText']))
                else:
                    print(lesson['LessonType'])
                    newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=lesson['DayText']))
                newmod.addLesson(newlesson)
        except KeyError:
            noTimetableModCount += 1

    return newmod
        

def loadAllModData():
    fileMods = open('modsData.txt')
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
    
    for modData in modsJson:
        modcode = modData['ModuleCode']
        examDate = modData.get('ExamDate','')
        modDept = modData.get('Department','')
        newmod = Module(modcode,examDate,modDept)
        try:
            for lesson in modData['Timetable']:
                if lesson['LessonType'] == 'LABORATORY':
                    newlesson = Laboratory(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=lesson['DayText']))
                else:
                    newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=lesson['DayText']))
                newmod.addLesson(newlesson)
        except KeyError:
            noTimetableModCount += 1
        modSet.addModule(newmod)
    return (modSet,deptToFac)
    

def generateBaseTimetable(modList,masterModset):
    
    modSet = ModuleSet()
    for modcode in modList:
        newmod = masterModset.getModule(modcode)
        modSet.addModule(newmod)

    baseTT = Timetable(modSet)
    removeConflicts(baseTT,modSet)
    
    return (baseTT,modSet)

def removeConflicts(baseTT,modSet):
    flag = False

    for mod in modSet:
        for lesson in mod.getCompulsoryLessons():
            for mod_del in modSet:
                if mod_del != mod:
                    for lesson_del in mod_del.getClashingLessons(lesson):
                        mod_del.removeLesson(lesson_del)
                        baseTT.removeLesson(lesson_del)
                        flag = True

    if flag:
        return (removeConflicts(baseTT,modSet) + 1)
    else:
        return 1

def generatePossibleModules(modCodeList,masterModset):
    moduleList = [module for module in masterModset if module.getCode() in modCodeList]
    masterModset = removeExamConflicts(modCodeList,removeByFacultyFilter(modCodeList,masterModset))
    
    flag = True
    while(flag):
        flag = False
        for mod in moduleList:
            for lesson in mod.getCompulsoryLessons():
                for mod_del in masterModset:
                    lessonIdSet = set()
                    lessonList = []
                    for lesson_del in mod_del.getClashingLessons(lesson):
                        if lessonIdSet.add(lesson_del.getId()):
                            lessonList.append(lesson_del)
                        flag = True
                    for lessonToDelete in lessonList:                        
                        mod_del.removeLesson(lessonToDelete)

    print("done removing")
    
    if any(masterModset.getModule(modCode).getNumChoices() == 0 for modCode in modCodeList):
        print("Pre allocated Modules cannot be taken together!!")
        exit
    modCounter = 0
    possibleMods = [];
    for mod in masterModset:
        if (mod not in moduleList) and mod.getNumChoices() != 0:
            possibleMods.append(mod.getCode())

    return possibleMods

def removeExamConflicts(mainModList,masterModSet):
    
    examSlots = [masterModSet.getModule(modCode).getExamDate() for modCode in mainModList]
    tempModSet = ModuleSet()
    for mod in masterModSet:
        if(mod.getCode() not in mainModList and mod.getExamDate() != '' and mod.getExamDate() in examSlots):
            tempModSet.addModule(mod)

    for mod in tempModSet:
        masterModSet.removeModule(mod.getCode())
    
    return masterModSet

def removeByFacultyFilter(mainModCodeList,masterModSet):
    tempModSet = ModuleSet()
    for mod in masterModSet:
        if (mod.getCode() not in mainModCodeList) and deptToFac[mod.getDepartment()] in facRestriction:
            tempModSet.addModule(mod)
    for mod in tempModSet:
        masterModSet.removeModule(mod.getCode())
    return masterModSet

def removeByTimeFilter():
    return None

loadedData,deptToFac = loadAllModData()
##modData = copy.deepcopy(loadedData)
facRestriction = []##'SCIENCE',"ENGINEERING",'ARTS & SOCIAL SCIENCES']
modCodeList = ['MA1505','PC1432','PC1431','MA1506','CS1231','CS2103']
print("starting now...")
modList = generatePossibleModules(modCodeList,loadedData)
##mod = checkModuleAdding("YLS1201")
##mod.setBaseparams()
