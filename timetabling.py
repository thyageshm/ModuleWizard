import json


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
    def __init__(self, weeks, *timeslots, **StartEndTimes):

        ## StartEndTimes takes stime and etime as 24hr str times and converts them respective timeslots
        ## timeslots takes in a list of timeslots to directly add to the attribute

        if not all(type(timeslot) == TimeSlot for timeslot in timeslots):
            raise TypeError("One or more of the given parameters is not of type TimeSlot")

        if len(StartEndTimes) > 0:
            self.timeslots = []

            stime, etime, day = int(StartEndTimes['stime']), int(StartEndTimes['etime']), StartEndTimes['day']

            if etime == 0:
                etime = 2400

            while stime < etime:
                self.timeslots.append(TimeSlot(day, stime))
                stime += 30 if stime % 100 == 0 else 70

        else:
            self.timeslots = list(timeslots)
            self.weeks = weeks

    def addTimeSlot(self, *sources):
        if not all((type(source) == TimeSlot or type(source) == Period) for source in sources):
            raise TypeError(
                "One of the given parameter was not an acceptable source for periods (eg Periods, TimeSlots)")

        for source in sources:
            if type(source) == TimeSlot:
                self.periods.append(source)
            elif type(source) == Period:
                for timeslot in source:
                    self.periods.append(timeslot)

    def __str__(self):
        message = ""
        for t in self:
            #message+="Day: "+str(t[0])+", Time: "+str(t[1])+"\n"
            message += str(t)

        return message

    def __iter__(self):
        for timeslot in self.timeslots:
            yield timeslot

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

    def hasSlot(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        return any(t == timeslot for t in self.timeslots)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

class PeriodGroup(object):
    def __init__(self, *periods):
        if not all(type(period) == Period for period in periods):
            raise TypeError("One or more of the parameters given is not of type Period")
        self.periods = list(periods)

    def addPeriod(self, *sources, **StartEndTimes):
        if not all((type(source) == PeriodGroup or type(source) == Period) for source in sources):
            raise TypeError(
                "One of the given parameter was not an acceptable source for periods (eg Periodgroups, Lessons)")

        if len(StartEndTimes) > 0:
            try:
                self.periods.append(
                    Period(stime=StartEndTimes['stime'], etime=StartEndTimes['etime'], day=StartEndTimes['day']))
            except KeyError:
                raise KeyError("Given named parameters do not contain 'stime', 'etime' and 'day'")
        else:
            for source in sources:
                if type(source) == Period:
                    self.periods.append(source)
                elif type(source) == PeriodGroup:
                    for period in source:
                        self.periods.append(period)

    def DoClash(self, anotherGroup):
        return any(selftime.DoClash(anothertime) for selftime, anothertime in zip(self.periods, anotherGroup.periods))

    def __iter__(self):
        for period in self.periods:
            yield period

    def hasSlot(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        return any(period.hasSlot(timeslot) for period in self.periods)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

class Lesson(object):
    def __init__(self, group, module, *periodgroups):
        if not all(type(periodgroup) == PeriodGroup for periodgroup in periodgroups):
            raise TypeError("One or more of the parameters given is not of type PeriodGroup")

        self.periodgroups = list(periodgroups)

        self.group = group
        self.module = module
        self.alternatives = len(periodgroups)

    def addPeriodGroup(self, *sources):
        if not all((type(source) == PeriodGroup or issubclass(type(source), Lesson)) for source in sources):
            raise TypeError(
                "One of the given parameter was not an acceptable source for period group (eg Periodgroups, Lessons)")

        for source in sources:
            if type(source) == PeriodGroup:
                self.periodgroups.append(source)
            elif issubclass(type(source), Lesson):
                for pg in source:
                    self.periodgroups.append(pg)

    def __iter__(self):
        for pg in self.periodgroups:
            yield pg

    def __eq__(self, anotherLesson):
        return self.getId() == anotherLesson.getId()

    def hasSlot(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")
        return any(periodgroup.hasSlot(timeslot) for periodgroup in self.periodgroups)

    def getModule(self):
        return self.module

    def getGroup(self):
        return self.group

    def getId(self):
        return self.module + "_" + type(self).__name__ + "_" + self.group

    def getAlternatives(self, timeslot):
        for pg in self:
            if not pg.hasSlot(timeslot):
                yield pg

    def getAlternativeCount(self):
        return self.alternatives

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

class Lecture(Lesson):
    def __init__(self, group, module, *periodgroups):
        Lesson.__init__(self, group, module, periodgroups[0])


class Tutorial(Lesson):
    def __init__(self, group, module, *periodgroups):
        Lesson.__init__(self, group, module, periodgroups[0])


class Laboratory(Lesson):
    def __init__(self, group, module, *periodgroups):
        Lesson.__init__(self, group, module, periodgroups[0])

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

class Module(object):
    def __init__(self, code):
        if not isinstance(code, str):
            raise TypeError("Given code is not of type string!")

        self.lessons = {"Lecture": [], "Tutorial": [], "Laboratory": []}
        self.code = code

    def getOccupingLessonID(self, timeslot):
        if type(timeslot) != TimeSlot:
            raise TypeError("Given parameter is not of type TimeSlot")

        for lesson in self:
            if lesson.hasSlot(timeslot):
                yield lesson.getId()

    def getLesson(self, Lid):
        ## only check in the list of lessons that are of the same type (Lec/Tut/Lab)
        for lesson in self.lessons[Lid.split("_")[1]]:
            if lesson.getId() == Lid:
                return lesson

    def getCode(self):
        return self.code

    def addLesson(self, lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")

        if self.hasLesson(lesson=lesson):
            internalLesson = self.getLesson(lesson.getId())
            internalLesson.addPeriodGroup(lesson)
        else:
            self.lessons[lesson.getId().split("_")[1]].append(lesson)

    def hasLesson(self, **lessonData):
        try:
            if issubclass(type(lessonData['lesson']), Lesson):
                lesson = lessonData['lesson']
                return any(lesson == self_lesson for self_lesson in self.lessons[lesson.getId().split("_")[1]])
            else:
                raise TypeError("Given parameter is not a valid lesson")
        except KeyError:
            try:
                if lessonData['lessonid'] != None:
                    lessonid = lessonData['lessonid']
                    return any(lessonid == self_lesson.getId() for self_lesson in self.lessons[lessonid.split("_")[1]])
                else:
                    raise TypeError("Given 'None' as lesson id")
            except KeyError:
                raise KeyError("No lesson data provided")

    def getChoices(self):
        for lec in self.__iter__(Lecture):
            for tut in self.__iter__(Tutorial):
                for lab in self.__iter__(Laboratory):
                    yield ((lec, tut, lab))

    def __eq__(self, anotherModule):
        return self.getCode() == anotherModule.getCode()

    def __iter__(self, FilterType=object):
        if FilterType != object:
            for lesson in self.lessons[FilterType.__name__]:
                yield lesson
        else:
            for ltype in self.lessons:
                for lesson in self.lessons[ltype]:
                    yield lesson

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

    def __iter__(self):
        for module in self.modules:
            yield module

    def addModule(self, module):
        if not type(module) == Module:
            raise TypeError("The given parameter is not of type Module")

        self.modules.append(module)

    def removeModule(self, code):
        for module in self:
            if module.getCode() == code:
                self.modules.remove(module)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

class Timetable(object):
    def __init__(self, source=None):
        ##create a timetable with day names as rows and the int representation of the 24 hr clock as columns

        Days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        Times = []
        stime = 800
        while stime <= 2400:
            Times.append(stime)
            stime += 30 if stime % 100 == 0 else 70

        self.field = {Day: {Time: [] for Time in Times} for Day in Days}
        if source != None:
            if type(source) == ModuleSet:
                self.addModuleSet(source)
            elif type(source) == Module:
                self.addModule(Module)
            else:
                raise TypeError("Given source parameter is not of type Module or ModuleSet")

    def __iter__(self):
        for day in self.field.values():
            yield day

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
        for periodgroup in lesson:
            self.addLessonPG(periodgroup, lesson)

    def addLessonPG(self, periodgroup, lesson):
        if not type(periodgroup) == PeriodGroup:
            raise TypeError("Given parameter is not of type PeriodGroup")
        for period in periodgroup:
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

    def removeLessonT(self, timeslot, lessonid):
        Slot = self[timeslot]

        for lesson in Slot:
            if lesson.getId() == lessonid:
                Slot.remove(lesson)

    def removeLessonP(self, period, lessonid):
        for timeslot in period:
            self.removeLessonT(timeslot, lessonid)

    def removeLessonPG(self, periodgroup, lessonid):
        for period in periodgroup:
            self.removeLessonP(period, lessonid)

    def getLessonsCount(self, timeslot):
        return len(self[timeslot])

    def removeAlternatives(self, lesson, timeslot):
        for pg in lesson.getAlternatives(timeslot):
            self.removeLessonPG(pg, lesson)

    def AddAlternatives(self, lesson, timeslot):
        for pg in lesson.getAlternatives(timeslot):
            self.addLessonPG(pg, lesson)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

def generateBaseTimetable(modList):
    filemods = open('modsData.txt')
    fileLtypes = open('LtypesData.txt')

    modsJson = json.load(filemods)
    LtypesJson = json.load(fileLtypes)

    filemods.close()
    fileLtypes.close()

    modSet = ModuleSet()
    for modcode in modList:
        newmod = Module(modcode)
        ##print(modsJson[modcode])
        for lesson in modsJson[modcode]['Timetable']:
            if lesson['LessonType'] == 'LABORATORY':
                newlesson = Laboratory(lesson['ClassNo'], modcode, PeriodGroup(
                    Period(0, stime=lesson['StartTime'], etime=lesson['EndTime'], day=lesson['DayText'])))
            else:
                newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'], modcode, PeriodGroup(
                    Period(0, stime=lesson['StartTime'], etime=lesson['EndTime'], day=lesson['DayText'])))
            newmod.addLesson(newlesson)
        modSet.addModule(newmod)

        for choice in newmod.getChoices():
            print(choice)
        exit()

    return Timetable(modSet)


def generatePossibleTimetables(modList):
    baseTT = generateBaseTimetable(modList)

    conflicts = {}
    for mod in modList:
        conflicts[mod] = {}

    ## go through the whole timetable and for each timeslot, create a dict of "conflicts" tuples
    for day in baseTT:
        for time in day.values():
            for lesson in time:
                conflicts[lesson.getModule()][lesson.getId()] = conflicts[lesson.getModule()].get(lesson.getId(),
                                                                                                  set()) | set([lesson.getId() for lesson in time])

    conflictlist = []
    for mod in conflicts:
        conflictlist.append((sum([len(l) for l in conflicts[mod].values()]), mod))

    conflictlist = sorted(conflictlist, reverse=True)
    for conflictcount, mod in conflictlist:
        print(mod, conflictcount)
