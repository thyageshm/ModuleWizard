import json, copy
from time import clock
##Start of class hierarchy

currentSem = 'Sem2'


class TimeSlot(object):
    """
        This class represents each half an hour slot in the timetable in a week
        It holds values of the day and the start time of the slot
    """
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

        return self.day if key == 0 else self.time

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
    """
        This class holds a list of continuous timeslots to make a "period"
        This forms the time aspect of a lecture/tutorial/laboratory
    """
    def __init__(self, weeks, *timeslots, **StartEndTimes):
        """

        @param weeks: specifies the recurrence of the lesson ("ALL WEEKS", "ODD WEEKS", "EVEN WEEKS")
        @param timeslots: A list of TimeSlot objects that forms this period
        @param StartEndTimes:
        @return:
        """

        ## StartEndTimes takes stime and etime as 24hr str times and converts them respective timeslots
        ## timeslots takes in a list of timeslots to directly add to the attribute

        if not all(type(timeslot) == TimeSlot for timeslot in timeslots):
            raise TypeError("One or more of the given parameters is not of type TimeSlot")

        self.timeslots = []

        if len(StartEndTimes) > 0:

            stime, etime, day = int(StartEndTimes['stime']), int(StartEndTimes['etime']), StartEndTimes['day']

            if etime == 0:
                etime = 2400

            while stime < etime:
                self.timeslots.append(TimeSlot(day, stime))
                stime += 30 if stime % 100 == 0 else 70

        if (len(timeslots) > 0):
            self.timeslots += list(timeslots)

        self.weeks = weeks

    def addTimeSlot(self, *sources):
        if not all((type(source) == TimeSlot or type(source) == Period) for source in sources):
            raise TypeError("One of the parameters was not an acceptable source for periods (eg Periods, TimeSlots)")

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
            # message+="Day: "+str(t[0])+", Time: "+str(t[1])+"\n"
            message += str(t)

        return message

    def __eq__(self, period):
        return self.getStart() == period.getStart() and self.getEnd() == period.getEnd()

    def __iter__(self):
        for timeslot in self.timeslots:
            yield timeslot

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

class Lesson(object):
    def __init__(self, group, module, *periods):
        if not all(type(period) == Period for period in periods):
            raise TypeError("One or more of the parameters given is not of type Period")

        self.periods = list(periods)
        self.group = str(group)
        self.module = str(module)
        self.alternatives = []

    def addPeriod(self, *sources):
        if not all((type(source) == Period or issubclass(type(source), Lesson)) for source in sources):
            raise TypeError("One of the parameters was not an acceptable source for period group (eg Periods, Lessons)")

        for source in sources:
            if type(source) == Period:
                self.periods.append(source)
            elif issubclass(type(source), Lesson):
                for period in source:
                    self.periods.append(period)

    def addAlternative(self, *alts):
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

    def isAlternative(self, lesson):
        ##return set(self.periods) == set(lesson.periods)
        if len(self.periods) == len(lesson.periods):
            return all(selfp == lessonp for selfp, lessonp in zip(lesson, self))
        else:
            return False

            ##   Special functions:

    def __str__(self):
        return "ID: " + self.getId()

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

##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------


class Lecture(Lesson):
    def __init__(self, group, module, *periods):
        if len(periods) > 0:
            Lesson.__init__(self, group, module, periods[0])
        else:
            Lesson.__init__(self, group, module)


class Tutorial(Lesson):
    def __init__(self, group, module, *periods):
        if len(periods) > 0:
            Lesson.__init__(self, group, module, periods[0])
        else:
            Lesson.__init__(self, group, module)


class Laboratory(Lesson):
    def __init__(self, group, module, *periods):
        if len(periods) > 0:
            Lesson.__init__(self, group, module, periods[0])
        else:
            Lesson.__init__(self, group, module)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------


class Module(object):
    """
        This class models a module which contains different lessons in it.
        The lessons are kept in list within a bigger dict with keys as lesson type ("Lecture","Tutorial","Laboratory")

        Stores all other attributes like module code and exam date as member variables

        Add all associated lessons and then call setBaseParams() to set the lesson related count values
    """
    def __init__(self, code, examDate, dept):
        """
            @param code: refers to the module code in string
            @param examDate: the examDate in string ("DD/MM/YYYY hh:mm AM/PM")
            @param dept: refers to the department the module belongs to, in string
            @return: creates a module object with given params
        """

        # Test if given code is valid
        if not isinstance(code, str):
            raise TypeError("Given code is not of type string!")

        # Create the member variables to hold module's info
        self.lessons = {"Lecture": [], "Tutorial": [], "Laboratory": []}    # The dict that holds the lessons
        self.code = code                                                    # The module code
        self.examDate = examDate                                            # The exam date
        self.dept = dept                                                    # The department
        self.leccount = -1                                                  # The num of lectures in the module
        self.tutcount = -1
        self.labcount = -1

    def addLesson(self, lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")

        ## check if this is a second period to an existing lesson
        if self.hasLesson(lesson=lesson):
            internalLesson = self.getLesson(lesson.getId())
            internalLesson.addPeriod(lesson)
        elif not self.hasAlternativeLesson(lesson):
            self.lessons[lesson.getId().split("_")[1]].append(lesson)

    def removeLesson(self, lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")

        self.lessons[type(lesson).__name__].remove(lesson)

    def removeAllBut(self, lessonType, group):
        ##print(group)
        ##print([lesson.getGroup() for lesson in self.lessons[lessonType]])
        self.lessons[lessonType] = []
        for lesson in self.lessons[lessonType]:
            if group in [lesson.getGroup()] + [tempLesson.getGroup()
                                               for tempLesson in lesson.getAlternatives()]:
                self.lessons[lessonType].append(lesson)

    def hasAlternativeLesson(self, lesson):
        for self_lesson in self.__iter__(type(lesson)):
            if self_lesson != lesson and self_lesson.isAlternative(lesson):
                self_lesson.addAlternative(lesson)
                return True
        return False

    def hasLesson(self, **lessonData):
        try:
            if issubclass(type(lessonData['lesson']), Lesson):
                lesson = lessonData['lesson']
                return any(lesson == self_lesson for self_lesson in self.lessons[lesson.getId().split("_")[1]])
            else:
                raise TypeError("Given parameter is not a valid lesson")
        except KeyError:
            try:
                if lessonData['lessonid'] is not None:
                    lessonid = lessonData['lessonid']
                    return any(lessonid == self_lesson.getId() for self_lesson in self.lessons[lessonid.split("_")[1]])
                else:
                    raise TypeError("Given 'None' as lesson id")
            except KeyError:
                raise KeyError("No lesson data provided")

    def getChoices(self, setc):
        for lec in (self.__iter__(Lecture, setc) if self.leccount > 0 else [Lecture("Test", "Test")]):
            for tut in (self.__iter__(Tutorial, setc) if self.tutcount > 0 else [Tutorial("Test", "Test")]):
                for lab in (self.__iter__(Laboratory, setc) if self.labcount > 0 else [Laboratory("Test", "Test")]):
                    yield {lec.getId(), tut.getId(), lab.getId()}

    def getOccupyingLesson(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        for lesson in self:
            if lesson.hasSlot(timeslot):
                yield lesson

    def getClashingLessons(self, otherLesson):
        conflictSet = set()
        for period in otherLesson:
            for timeslot in period:
                for otherLesson in self.getOccupyingLesson(timeslot):
                    conflictSet.add(otherLesson.getId())
        for otherLesson in self:
            if otherLesson.getId() in conflictSet:
                yield otherLesson

    def getLesson(self, Lid):
        ## only check in the list of lessons that are of the same type (Lec/Tut/Lab)
        for lesson in self.lessons[Lid.split("_")[1]]:
            if lesson.getId() == Lid:
                return lesson

    def getDepartment(self):
        return self.dept

    def getNumChoices(self):
        return (1 if 0 == self.leccount else len(self.lessons["Lecture"])) * (
            1 if 0 == self.tutcount else len(self.lessons["Tutorial"])) * (
                   1 if 0 == self.labcount else len(self.lessons["Laboratory"]))

    def getCode(self):
        return self.code

    def getExamDate(self):
        return self.examDate

    ## this function is used to set the count of lessons in the actual module as,
    ## to optimise we would be removing some of the lessons prematurely
    def setBaseparams(self):
        for lesson in self:
            if self.hasAlternativeLesson(lesson):
                self.removeLesson(lesson)

        self.leccount = len(self.lessons["Lecture"])
        self.tutcount = len(self.lessons["Tutorial"])
        self.labcount = len(self.lessons["Laboratory"])

    def getCompulsoryLessons(self):
        if self.leccount is -1:
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

    def __iter__(self, FilterType=object, ExcludeList=set()):
        if FilterType != object:
            for lesson in self.lessons[FilterType.__name__]:
                if lesson.getId() not in ExcludeList:
                    yield lesson
        else:
            for ltype in self.lessons:
                for lesson in self.lessons[ltype]:
                    if lesson.getId() not in ExcludeList:
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

    def getModule(self, code):
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
dayToInt = {"MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3, "THURSDAY": 4, "FRIDAY": 5, "SATURDAY": 6, "SUNDAY": 7}
facChoices = ['ENGINEERING']
modCodeList = {'ST2334': {"Lecture": "SL1", "Tutorial": "T1"}, 'SSA2209': {"Tutorial": "D1"},
               'EE2024': {"Tutorial": "T9", 'Laboratory': 'B1'}, 'EE2023': {}, "EE2031": {'Laboratory': 'B2'}}


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
        if modcode != testCode:
            continue
        examDate = modData.get('ExamDate', '')
        newmod = Module(modcode, examDate)
        try:
            for lesson in modData['Timetable']:
                if lesson['LessonType'] == 'LABORATORY':
                    newlesson = Laboratory(lesson['ClassNo'], modcode,
                                           Period(0, stime=lesson['StartTime'], etime=lesson['EndTime'],
                                                  day=dayToInt[lesson['DayText']]))
                else:
                    print(lesson['LessonType'])
                    newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'], modcode,
                                                                       Period(0, stime=lesson['StartTime'],
                                                                              etime=lesson['EndTime'],
                                                                              day=dayToInt[lesson['DayText']]))
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

    for modcode, modData in modsJson.items():
        modcode = str(modcode)
        if type(modData) == list or modData['ExamDate'] == "Not Applicable." or modData['ExamDate'].get(currentSem,
                                                                                                        '') == '' or \
                        modData['Timetable'] == "Not Applicable.":
            continue
        examDate = modData['ExamDate'][currentSem]
        modDept = modData['Department']
        newmod = Module(modcode, examDate, modDept)
        preReqData[modcode] = modData['Tree']['children']
        try:
            if isinstance(modData['Timetable'], dict):
                if modData['Timetable'] == "Not Applicable.":
                    continue
                else:
                    if not modData['Timetable'].get(currentSem, []):
                        continue
                    else:
                        for lesson in [lessons for lessons in modData['Timetable'][currentSem] if
                                       modData['Timetable'][currentSem] != "Not Available."]:
                            newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'], modcode,
                                                                               Period(0, stime=lesson['StartTime'],
                                                                                      etime=lesson['EndTime'],
                                                                                      day=dayToInt[lesson['DayText']]))
                            newmod.addLesson(newlesson)
        except KeyError:
            pass
        modSet.addModule(newmod)
    return (modSet, deptToFac, preReqData)


def generatePossibleModules(modInfoDict, masterModset):
    modList, masterModset = getPreallocatedModuleList(masterModset, modInfoDict)
    masterModset = removeConflicts(modInfoDict.keys(), masterModset)

    clock()
    flag = True

    while (flag):
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

    possibleMods = []
    for mod in masterModset:
        if (mod not in modList) and mod.getNumChoices() != 0:
            possibleMods.append(mod.getCode())

    return possibleMods, modList


def getPreallocatedModuleList(masterModset, modInfoDict):
    modList = []
    for mod in masterModset:
        if mod.getCode() in modInfoDict.keys():
            for lessonType, group in modInfoDict[mod.getCode()].items():
                mod.removeAllBut(lessonType, group)
            modList.append(mod)

    return (modList, masterModset)


def removeConflicts(mainModCodeList, masterModSet):
    examSlots = [masterModSet.getModule(modCode).getExamDate() for modCode in mainModCodeList]
    tempModSet = ModuleSet()

    for mod in masterModSet:
        if mod.getCode() not in mainModCodeList:
            if hasNoExamConflict(mod, examSlots) and isOfRightFaculty(mod):
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


def filterByPrereq(modCodeList, masterModSet):
    modsToRemove = []
    for mod in masterModSet:
        modCode = mod.getCode()
        if not isEligibleByPrereq(modCode, modCodeList):
            modsToRemove.append(modCode)

    for modCode in modsToRemove:
        masterModSet.removeModule(modCode)

    return masterModSet


def isEligibleByPrereq(modCodeToTake, modCodesAlreadyTaken):
    preReqDict = preReqData[modCodeToTake]
    return satisfiesPrereq(preReqDict, modCodesAlreadyTaken)


def hasNoExamConflict(mod, examSlots):
    return mod.getExamDate() == "Not Available." or mod.getExamDate() not in examSlots


def isOfRightFaculty(mod):
    return deptToFac[mod.getDepartment()] in facChoices


def isAtWrongTime(lesson):
    return any(lesson.hasSlot(timeslot) for timeslot in timeRestrictions)


def satisfiesPrereq(child, modList):
    if not child:
        return True
    if child['name'] == "and":
        return all(satisfiesPrereq(c1, modList) for c1 in child['children'])
    elif child['name'] == "or":
        return any(satisfiesPrereq(c1, modList) for c1 in child['children'])
    else:
        return child['name'] in modList


def createTimeBasedModules(timeRestraints):
    i = 1
    modset = ModuleSet()
    for restraint in timeRestraints:
        mod = Module("TimeRestrainModule " + str(i), "Not Available.", "COMPUTING & ENGINEERING")
        stime = restraint["StartTime"]
        while (stime + restraint["TimeNeeded"]) <= restraint["EndTime"]:
            tempPeriod = Period("ALL WEEKS", day=dayToInt[restraint["Day"]], stime=stime,
                                etime=(stime + restraint["TimeNeeded"]))
            tempLesson = Lecture(stime, "TimeRestrainModule " + str(i), tempPeriod)
            mod.addLesson(tempLesson)
            stime += 30 if stime % 100 == 0 else 70
        i += 1
        modset.addModule(mod)

    return modset

def getClashingModuleCount(allModuleSet, clashingModuleSet):
    clashingModuleCount = {}
    for clashingMod in clashingModuleSet:
        clashingModuleCount[clashingMod.getCode()] = 0
        for clashingLesson in clashingMod:
            print clashingLesson.getId()
            for mod in allModuleSet:
                for lesson in mod.getClashingLessons(clashingLesson):
                    clashingModuleCount[clashingMod.getCode()] += 1
                    break

    return clashingModuleCount

def saveGeneratedListToFile(modList):
    fileN = open("test.txt", 'w')
    for mod in modList:
        fileN.write(mod + '\n')
    fileN.close()


loadedData, deptToFac, preReqData = loadAllModData()
print "done loading... deep copying..."
modData = copy.deepcopy(loadedData)
print "Num of mods: "+str(modData.getModuleCount())


print("starting now...")
# modList, testMods = generatePossibleModules(modCodeList, loadedData)
# saveGeneratedListToFile(modList)

# mod = checkModuleAdding("YLS1201", 0)
# mod.setBaseparams()

timeRestrictionsFile = open("../data/timeRestrictionsTestData.json")
timeRestrictions = json.load(timeRestrictionsFile)

## timeRestrictions = [{"Day": "MONDAY", "StartTime": 1200, "EndTime": 1400, "TimeNeeded": 30}]

testModSet = createTimeBasedModules(timeRestrictions)
clashingDict = getClashingModuleCount(modData, testModSet)
print clashingDict
# for mod in testModSet:
    # for lesson in mod:
    #     for p in lesson:
            # print p