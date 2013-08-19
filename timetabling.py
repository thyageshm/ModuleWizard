import json
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
    
    def __str__(self):
        message = ""
        for t in self:
            #message+="Day: "+str(t[0])+", Time: "+str(t[1])+"\n"
            message += str(t)

        return message

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

    def addPeriod(self, *sources):
        if not all((type(source) == Period or issubclass(type(source),Lesson)) for source in sources):
            raise TypeError("One of the given parameter was not an acceptable source for period group (eg Periods, Lessons)")
        
        for source in sources:
            if type(source) == Period:
                self.periods.append(source)
            elif issubclass(type(source),Lesson):
                for period in source:
                    self.periods.append(period)

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

##   Special functions:
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
    def __init__(self, code):
        if not isinstance(code,str):
            raise TypeError("Given code is not of type string!")

        self.lessons = {"Lecture":[],"Tutorial":[],"Laboratory":[]}
        self.code = code

    def addLesson(self, lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")
        
        if self.hasLesson(lesson=lesson):
            internalLesson = self.getLesson(lesson.getId())
            internalLesson.addPeriod(lesson)
        else:
            self.lessons[lesson.getId().split("_")[1]].append(lesson)

    def removeLesson(self,lesson):
        if not issubclass(type(lesson), Lesson):
            raise TypeError("Given parameter is not a lesson")

        if self.code != lesson.getModule():
            raise TypeError("Given Lesson does not belong to this Module")

        self.lessons[type(lesson).__name__].remove(lesson);

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

    def getNumChoices(self):
        return (1 if 0 == self.leccount else len(self.lessons["Lecture"])) * (1 if 0 == self.tutcount else len(self.lessons["Tutorial"])) * (1 if 0 == self.labcount else len(self.lessons["Laboratory"]))
    
    def getCode(self):
        return self.code
                
    ## this function is used to set the count of lessons in the actual module as to optimise we would be removing some of the lessons prematurely
    def setBaseparams(self):
        self.leccount = len(self.lessons["Lecture"])
        self.tutcount = len(self.lessons["Tutorial"])
        self.labcount = len(self.lessons["Laboratory"])

    def getCompulsoryLessons(self):
        try:
            self.leccount = self.leccount
        except AttributeError:
            self.Baseparams()
            
        if self.leccount == 1:
            yield self.lessons["Lecture"][0]
        if self.tutcount == 1:
            yield self.lessons["Tutorial"][0]
        if self.labcount == 1:
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

    def __iter__(self, FilterType=object,FilterList=set()):
        if FilterType != object:
            for lesson in self.lessons[FilterType.__name__]:
                if lesson.getId() not in FilterList:
                    yield lesson
        else:
            for ltype in self.lessons:
                for lesson in self.lessons[ltype]:
                    if lesson.getId() not in FilterList :
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

    def addModule(self, module):
        if not type(module) == Module:
            raise TypeError("The given parameter is not of type Module")
        
        module.setBaseparams()
        self.modules.append(module)

    def removeModule(self, code):
        for module in self:
            if module.getCode() == code:
                self.modules.remove(module)
    
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
        stime = 800
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
        for lesson in modsJson[modcode]['Timetable']:
            if lesson['LessonType'] == 'LABORATORY':
                newlesson = Laboratory(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=lesson['DayText']))
            else:
                newlesson = eval(LtypesJson[lesson['LessonType']])(lesson['ClassNo'],modcode,Period(0,stime=lesson['StartTime'],etime=lesson['EndTime'],day=lesson['DayText']))
            newmod.addLesson(newlesson)
        modSet.addModule(newmod)

    baseTT = Timetable(modSet)

    removeConflicts(baseTT,modSet)
    
    return (Timetable(modSet),modSet)

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

def generatePossibleTimetables(modList):   
    baseTT,modSet = generateBaseTimetable(modList);

    conflictlist = {};
    for mod in modList:
        conflictlist[mod] = {};
      
    ## go through the whole timetable and for each timeslot, create a dict of "conflicts" tuples
    for day in baseTT:
        for time in day.values():
            if len(time) > 1:
                for lesson in time:
                    conflictlist[lesson.getModule()][lesson.getId()] = conflictlist[lesson.getModule()].get(lesson.getId(),set()) | set([lesson.getId() for lesson in time]);
    
    conflictcount = []
    for mod in conflictlist:
        conflictcount.append((modSet.getModule(mod).getNumChoices(),modSet.getModule(mod)));
    ## arrange them in ascending order
    conflictcount = sorted(conflictcount,reverse=True);
    
    for count,mod in conflictcount:
        print(mod.getCode(),count);
    
##    for mod in conflictlist:
##        print(mod)
##        print()
##        for Lid in conflictlist[mod]:
##            print(Lid," ",conflictlist[mod][Lid])
##        print()
##        print()
        
##    count = 1;
##    for c,mod in conflictcount:
##        print(mod.getNumChoices())
##        count*=mod.getNumChoices()
    
##    print(count)
        clock()
    print(CountPossible(conflictlist,conflictcount,len(modList)));
    print(clock())

def CountPossible(conflist,confs,modcount,setc = set()):
##    print(setc);
##    print();
    count = 0;
    curconflict = conflist[confs[modcount-1][1].getCode()]
    if modcount == 1:
        for choice in confs[modcount-1][1].getChoices(setc):
            count += 1;
    else:
        for choice in confs[modcount-1][1].getChoices(setc):
            count += CountPossible(conflist,confs,modcount-1,(setc|set.union(*[curconflict.get(i,set()) for i in choice])))
    return count;
