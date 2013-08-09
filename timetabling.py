class Timeslot(object):
    def __init__(self,day,time):
        self.day = day
        self.time = time

    def __str__(self):
        message = "Day: "+str(self.day)+","
        message += "Time: "+str(self.time)
        return message
    def __getitem__(self,key):
        if type(key) != int:
            raise TypeError("Index is not of type Integer")
        elif not 0 <= key <=1:
            raise IndexError("Key is not found!")

        return (self.day if key == 0 else self.time)

    def getDay(self):
        return self.day

    def getTime(self):
        return self.time
    
    def __eq__(self,timeslot):
        return self.day == timeslot.day and self.time == timeslot.time

class Period(object):
    def __init__(self,weeks,*timeslots):
        if not all(type(timeslot) == Timeslot for timeslot in timeslots):
            raise TypeError("One or more of the given parameters is not of type Timeslot")

        self.timeslots = list(timeslots)
        self.weeks = weeks

    def addTimeslot(timeslot):
        if type(timeslot) != Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")

        self.timeslots.append(timeslot)

    def __str__(self):
        message = ""
        for t in self:
            #message+="Day: "+str(t[0])+", Time: "+str(t[1])+"\n"
            message+=str(t)

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
            return (anotherSlot.timeslots[0][1] <= self.timeslots[0][1] <= anotherSlot.timeslots[-1][1]) or (anotherSlot.timeslots[0][1] <= self.timeslots[-1][1] <= anotherSlot.timeslots[-1][1])

    def hasSlot(self,timeslot):
        if type(timeslot) != Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")

        return any(t == timeslot for t in self.timeslots)

class PeriodGroup(object):
    def __init__(self,*periods):
        if not all(type(period) == Period for period in periods):
            raise TypeError("One or more of the parameters given is not of type Period")
        self.periods = list(periods)

    def addPeriod(self, period):
        if not type(period) == Period:
            raise TypeError("Given parameter is not of type Period")

    def DoClash(self,anotherGroup):
        return any(selftime.DoClash(anothertime) for selftime,anothertime in zip(self.periods,another.periods))

    def __iter__(self):
        for period in self.periods:
            yield period

    def hasSlot(self,timeslot):
        if type(timeslot) != Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")

        return any(period.hasSlot(timeslot) for period in self.periods)

class Lesson(object):

    def __init__(self,group,*periodgroups):
        if not all(type(t) == PeriodGroup for t in periodgroups):
            raise TypeError("One or more of the parameters is not of type Period");

        self.periodgroups = list(periodgroups)

        self.group = group
        self.module = None
        self.alternatives = len(periodgroups)

    def addPeriodGroup(self,periodgroup):
        if not type(periodgroup) == PeriodGroup:
            raise TypeError("Given parameter was not of type PeriodGroup")

        self.periodgroups.append(periodgroup)

    def __iter__(self):
        for pg in self.periodgroups:
            yield pg

    def __eq__(self,anotherLesson):
        return self.getId() == anotherLesson.getId()

    def hasSlot(self,timeslot):
        if type(timeslot) != Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")
        return any(periodgroup.hasSlot(timeslot) for periodgroup in self.periodgroups)

    def setModule(newModule):
        self.module = newModule

    def getModule():
        return self.module

    def getId():
        return self.module+self.group

    def getAlternatives(self,timeslot):
        for pg in self:
            if not pg.hasSlot(timeslot):
                yield pg

    def getAlternativeCount(self):
        return self.alternatives

class Lecture(Lesson):
    def __init__(self,id,*periodgroups):
        Lesson.__init__(id,periodgroups)

class Tutorial(Lesson):
    def __init__(self,id,*periodgroups):
        Lesson.__init__(id,periodgroups)


class Module(object):
    def __init__(self,code,*lessons):
        if all(issubclass(type(lesson),Lesson) for lesson in lessons):
            raise TypeError("One or more of the given lessons are not lectures/tutorials")

        self.lessons = list(lessons)
        self.code = code

    def getOccupingLessonID(self,timeslot):
        if type(timeslot) != Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")

        for lesson in self:
            if lesson.hasSlot(timeslot):
                yield lesson.getID()
    
    def getLesson(self,id):
        for lesson in self:
            if lesson.getID() == id:
                return lesson

    def getCode(self):
        return self.code

    def addLesson(self,lesson):
        if not issubclass(type(lesson),Lesson):
            raise TypeError("Given parameter is not a lesson")

        lesson.setModule(self.code)
        self.lessons.append(lesson)

    def __eq__(self,anotherModule):
        return (self.getCode() == anotherModule.getCode())

    def __iter__(self,FilterType=object):
        for lesson in self.lessons:
            if issubclass(lesson,FilterType):
                yield lesson

class ModuleSet(object):
    
##    Created = False
    def __init__(self):
##        if ModuleSet.Created:
##           raise RuntimeError("A moduleset has already been created")
        self.modules = []

    def __iter__(self):
        for module in self.modules:
            yield module

    def addModule(module):
        if not type(module) == Module:
            raise TypeError("The given parameter is not of type Module")

        self.modules.append(module)

    def removeModule(code):
        for module in self:
            if module.getCode() == code:
                self.modules.remove(module)

class Timetable(object):
    def __init__(self):
        self.field = [[[] for j in range(16)] for i in range(6)]

    def getSlot(self,day,time):
        return self.fields[day][time]

    def __getitem__(self,timeslot):
        if type(timeslot) != Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")

        return self.getSlot(timeslot.getDay(),timeslot.getTime())

    ## combine these functions using polymorphism
    def addModuleSet(self,moduleset):
        if not type(moduleset) == ModuleSet:
            raise TypeError("The given parameter is not of type ModuleSet")
        
        for module in moduleset:
            self.addModule(module)
                        
    def addModule(self,module):
        if not type(module) == Module:
            raise TypeError("The given parameter is not of type Module")
        
        for lesson in module:
            self.addLesson(lesson)

    def addLesson(self,lesson):
        if not issubclass(type(lesson),Lesson):
            raise TypeError("Given parameter is not of type Lesson")
        for periodgroup in lesson:
            addLessonPG(periodgroup,lesson)
            
    def addLessonPG(self,periodgroup,lesson):
        if not type(periodgroup) == PeriodGroup:
            raise TypeError("Given parameter is not of type PeriodGroup")
        for period in periodgroup:
            self.addLessonP(period,lesson)

    def addLessonP(self,period,lesson):
        if not type(period) == Period:
            raise TypeError("Given parameter is not of type Period")
        for timeslot in period:
            self.addLessonT(timeslot,lesson)
    
    def addLessonT(self,timeslot,lesson):
        if not type(timeslot) == Timeslot:
            raise TypeError("Given parameter is not of type Timeslot")

        self[timeslot].append(lesson)

    def removeLessonT(self,timeslot,lessonid):
        Slot = self[timeslot]

        for lesson in Slot:
            if lesson.getId() == lessonid:
                Slot.remove(lesson);

    def removeLessonP(self,period,lessonid):
        for timeslot in period:
            removeLessonT(timeslot,lessonid)

    def removeLessonPG(self,peridgroup,lessonid):
        for period in periodgroup:
            removeLessonP(perion,lessonid)

    def getLessonsCount(self,timeslot):
        return len(self[timeslot])

    def removeAlternatives(self,lesson,timeslot):
        lessonid = lesson.getId()
        for pg in lesson.getAlternatives(timeslot):
            self.removeLessonPG(pg,lessonid)

    def AddAlternatives(self,lesson,timeslot):
        lessionid = lesson.getId()

        for pg in lesson.getAlternatives(timeslot):
            self.addLessonPG(pg,lesson)

class possibleTimetables(object):

    def __init__(self):
        self.timetables = list()

    def generatePossibleTimetables(self,moduleset):
        baseTimetable = Timetable()
        baseTimetable.addModuleSet(moduleset)

        for day in baseTimetable:
            for timeslot in day:
                for lesson in timeslot:
                    if lesson.getAlternativeCount == 1:
                        timeslot = []
                        timeslot.append(lesson)
                        break
        
        










                  
## test classes/functions to learn :P

class test(object):
    a = 0
    def __init__(self):
            self.id = test.a
            test.a += 1

class test1(test):
    def __init__(self,timeslot):
            test.__init__(self)
            self.time = timeslot

    def getID(self):
        return self.id

    def testing(self):
        print(self.time)

def f(a,b):
	for i in range(0,10):
		yield i

## restarts each time!
##for i in f():
##	print(i)
##	if i == 3:
##		break
##
##for i in f():
##	print(i)
##	if i == 3:
##		break




##Test for Period
##lec = list()
##lec.append(Period((1,1),(1,2),(1,3)))
##lec.append(Period((1,2),(1,3),(1,4)))
##lec.append(Period((1,3),(1,4)))
##lec.append(Period((1,4),(1,5),(1,6)))
##lec.append(Period((2,5),(2,6),(2,7)))
##
##for t1 in lec:
##    for t2 in lec:
##        if not t1 == t2:
##            print("Do ("+ str(t1) +") and ("+str(t2)+") clash? "+str(t1.DoClash(t2)))
##
##    print ("\n")
