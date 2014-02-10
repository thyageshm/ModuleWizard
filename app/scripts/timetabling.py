import json, copy,re
from time import clock
import abc

##Start of class hierarchy

currentSem = 'Sem2'
timeToDeepCopy = 0

class TimeSlot(object):
    """
        This class represents each half an hour slot in the timetable in a week
        It holds values of the day and the start time of the slot
        @author: Thyagesh Manikandan
    """

    def __init__(self, day, time):
        self.day = day
        self.time = time

    def getDay(self):
        return self.day

    def getTime(self):
        return self.time

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

    def __eq__(self, otherTimeslot):
        assert isinstance(otherTimeslot, TimeSlot)

        return self.day == otherTimeslot.day and self.time == otherTimeslot.time

    def __lt__(self, otherTimeslot):
        assert isinstance(otherTimeslot, TimeSlot)

        if self.getDay() > otherTimeslot.getDay():
            return False
        elif self.getDay() == otherTimeslot.getDay():
            if self.getTime() >= otherTimeslot.getTime():
                return False
        return True

    def __le__(self, otherTimeslot):
        assert isinstance(otherTimeslot, TimeSlot)

        return self == otherTimeslot or self < otherTimeslot

    def __gt__(self, otherTimeslot):
        assert isinstance(otherTimeslot, TimeSlot)

        return not (self == otherTimeslot or self < otherTimeslot)

    def __ge__(self, otherTimeslot):
        assert isinstance(otherTimeslot, TimeSlot)

        return not (self < otherTimeslot)

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------


class Period(object):
    """
        This class holds a list of continuous timeslots to make a "period"
        This forms the time aspect of a lecture/tutorial/laboratory
        @author: Thyagesh Manikandan
    """
    DEFAULT_DAY_OR_TIME_VALUE = 0
    STRING_EVERY_WEEK = "EVERY WEEK"
    STRING_ODD_WEEK = "ODD WEEKS"
    STRING_EVEN_WEEK = "EVEN WEEKS"

    def __init__(self, weeks, day=DEFAULT_DAY_OR_TIME_VALUE, stime=DEFAULT_DAY_OR_TIME_VALUE,
                 etime=DEFAULT_DAY_OR_TIME_VALUE, timeslots=[]):
        """
        @param weeks: specifies the recurrence of the lesson ("ALL WEEKS", "ODD WEEKS", "EVEN WEEKS")
        @param day: An integer to represent the day of the week starting with 1 for Monday
        @param stime: An int representation for the start time in the 24 hr time (eg 800 for 0800 and 2300 for 2300)
        @param etime: An int representation for the end time in the 24 hr time (eg 800 for 0800 and 2300 for 2300)
        @param timeslots: A list of TimeSlot objects that forms this period
        @return: creates a period object
        """

        ## Type checking
        if not all(type(timeslot) == TimeSlot for timeslot in timeslots):
            raise TypeError("One or more of the given parameters is not of type TimeSlot")

        if not (type(day) == int and type(stime) == int and type(etime) == int):
            raise TypeError("One of the parameters given is not an integer")

        ## Initialise member variables
        self.timeslots = []
        self.weeks = weeks

        ## populate the timeslots based on start time and end time  
        if day is not self.DEFAULT_DAY_OR_TIME_VALUE:
            if etime == 0:
                etime = 2400

            while stime < etime:
                self.timeslots.append(TimeSlot(day, stime))
                stime += 30 if stime % 100 == 0 else 70
                ## populate the timeslots based on list of timeslots given
        if len(timeslots) > 0:
            self.timeslots += timeslots

    def addTimeSlot(self, timeslot):
        """
        @param timeslot:
        @return: None
        """
        assert isinstance(timeslot, TimeSlot)

        self.timeslots.append(timeslot)

    def addTimeslots(self, timeslots):
        """
        @param timeslots: An iterable container of TimeSlot objects to be added to current Period
        @return: None
        """
        assert all(isinstance(timeslot, TimeSlot) for timeslot in timeslots)

        for timeslot in timeslots:
            self.addTimeSlot(timeslot)

    def addPeriods(self, periods):
        """
        @param periods: An iterable container of Period objects whose TimeSlots are to be added to current period
        @return: None
        """

        assert all(isinstance(period, Period) for period in periods)
        for period in periods:
            self.addPeriod(period)

    def addPeriod(self, period):
        """
        @param period: A Period object whose TimeSlots are to be added to this period object
        @return:
        """

        assert isinstance(period, Period)

        for timeslot in period:
            self.addTimeSlot(timeslot)

    def hasSlot(self, needleTimeslot):
        """
        @param needleTimeslot: The TimeSlot object to search for in this period
        @return: Boolean value to signify if the TimeSlot was found or not
        """

        assert isinstance(needleTimeslot, TimeSlot)

        return any(timeslot == needleTimeslot for timeslot in self.timeslots)

    def doesClash(self, anotherPeriod):
        """
        @param anotherPeriod: The period to check for overlap
        @return:
        """

        assert isinstance(anotherPeriod, Period)

        #compare the days and the odd/even week setting
        hasSameDay = self.timeslots[0].getDay() == anotherPeriod.timeslots[0].getDay()

        hasOverlapingWeekSetting = (self.weeks == self.STRING_EVERY_WEEK) or (anotherPeriod.weeks == \
            self.STRING_EVERY_WEEK) or (self.weeks == anotherPeriod.weeks)

        if not (hasSameDay and hasOverlapingWeekSetting):
            return False

        else:
            isStartOfThisPeriodInPeriod = anotherPeriod.getStart().getTime() <= self.getStart().getTime()\
                <= anotherPeriod.getEnd().getTime()
            isEndOfThisPeriodInPeriod = anotherPeriod.getStart().getTime() <= self.getEnd().getTime() \
                <= anotherPeriod.getEnd().getTime()

            return isStartOfThisPeriodInPeriod or isEndOfThisPeriodInPeriod

    def getStart(self):
        """
        @return: Starting TimeSlot object of self
        """
        return self.timeslots[0]

    def getEnd(self):
        """
        @return: Ending TimeSlot object of self
        """
        return self.timeslots[-1]

    def __str__(self):
        message = ""
        for t in self:
            # message+="Day: "+str(t[0])+", Time: "+str(t[1])+"\n"
            message += str(t)

        return message

    def __eq__(self, otherPeriod):
        assert isinstance(otherPeriod, Period)

        return self.getStart() == otherPeriod.getStart() and self.getEnd() == otherPeriod.getEnd()

    def __lt__(self, otherPeriod):
        assert isinstance(otherPeriod, Period)

        if self.getStart() > otherPeriod.getStart():
            return False
        elif self.getStart() == otherPeriod.getStart():
            if self.getEnd() >= otherPeriod.getEnd():
                return False

        return True

    def __le__(self, otherPeriod):
        assert isinstance(otherPeriod, Period)

        return self == otherPeriod or self < otherPeriod

    def __gt__(self, otherPeriod):
        assert isinstance(otherPeriod, Period)

        return not (self < otherPeriod or self == otherPeriod)

    def __ge__(self, otherPeriod):
        assert isinstance(otherPeriod, Period)

        return not (self < otherPeriod)

    def __iter__(self):
        """
        @return: yields all the TimeSlot objects in this Period
        """

        for timeslot in self.timeslots:
            yield timeslot

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------


class Lesson(object):
    """
        This class represents a single lesson in any module (eg Lecture, Tutorial, Laboratory)
        It is represented as a list of periods that define when the lesson takes place
        Additional info such as the module that the lesson belongs to and group number are saved as well
        For the sake of the algorithm in this file, alternatives is a list of lessons of the same type (eg lecture) that
            contain the same set of periods to define them
        @author: Thyagesh Manikandan
    """

    def __init__(self, moduleCode, group, periods=[]):
        """
        @param moduleCode: The Module Code of the module that the lesson belongs to
        @param group: The specific group number of the lesson
        @param periods: The list of periods that define the lesson
        @return: None
        """

        assert all(isinstance(period, Period) for period in periods)
        assert isinstance(moduleCode, str)
        assert isinstance(group, str)

        self.periods = periods
        self.group = str(group)
        self.moduleCode = moduleCode
        self.alternatives = []

    def addPeriod(self, period):
        """
        @param period: The Period object to add to the Lesson
        @return:
        """

        assert isinstance(period, Period)

        self.periods.append(period)

    def addPeriods(self, periods):
        """
        @param periods: An iterable container  of periods to add to the lesson
        @return:
        """

        assert all(type(period) == Period for period in periods)

        for period in periods:
            self.addPeriod(period)

    def mergeWithLesson(self, lesson):
        """
        @param lesson: A Lesson object to merge with
        @return:
        """

        assert issubclass(type(lesson), Lesson)

        for period in lesson:
            self.addPeriod(period)

    def mergeWithLessons(self, lessons):
        """
        @param lessons: An iterable container of Lesson objects to merge with
        @return:
        """

        assert all(issubclass(type(lesson), Lesson) for lesson in lessons)

        for lesson in lessons:
            self.mergeWithLesson(lesson)

    def addAlternative(self, lesson):
        """
        @param lesson: A Lesson object of same type as this Lesson object to add as an alternative
        @return: None
        """

        assert isinstance(lesson, Lesson)

        if lesson not in self.alternatives:
            self.alternatives.append(lesson)

    def addAlternatives(self, lessons):
        """
        @param lessons: An iterable container of lessons that are of the same type of this Lesson to add as alternatives
        @return: None
        """

        assert all(type(lesson) == type(self) for lesson in lessons)

        for lesson in lessons:
            self.addAlternative(lesson)

    def hasSlot(self, timeslot):
        """
        @param timeslot: The TimeSlot object that is tested for existence in this Lesson object
        @return: Boolean to represent existence or otherwise
        """

        assert isinstance(timeslot, TimeSlot)

        return any(period.hasSlot(timeslot) for period in self.periods)

    def getModuleCode(self):
        return self.moduleCode

    @abc.abstractmethod
    def getLessonType(self):
        """ Return string form of the lesson type """
        return

    def getGroup(self):
        return self.group

    def getId(self):
        """
        @return: A unique Id to identify this lesson. Made of moduleCode, group and lesson type
        """
        return self.moduleCode + "_" + type(self).__name__ + "_" + self.group

    def getAlternatives(self):
        """
        @return: yields all lessons that are alternatives to self
        """

        for lesson in self.alternatives:
            yield lesson

    def getAlternativeCount(self):
        return len(self.alternatives)

    def isAlternative(self, lesson):
        """
        @param lesson: The Lesson object that is tested to be an alternative to self Lesson object
        @return: Boolean to represent whethe or not the given lesson is an alternative to self
        """

        # Both lessons need to have the same number of periods and same periods
        if len(self.periods) == len(lesson.periods):
            return all(selfp == lessonp for selfp, lessonp in zip(lesson, self))
        else:
            return False

    def clashesWith(self, otherLesson):
        return any(otherLesson.hasSlot(timeslot) for period in self for timeslot in period)

    def __str__(self):
        return "ID: " + self.getId()

    def __iter__(self):
        for period in sorted(self.periods):
            yield period

    def __eq__(self, other):
        return self.getId() == other.getId()

##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------


class Lecture(Lesson):
    """
        This class represents a Lecture as a lesson type
        It inherits from Lesson and is only used for type checking
        @author: Thyagesh Manikandan
    """
    def __init__(self, module, group, *periods):
        if len(periods) > 0:
            Lesson.__init__(self, module, module, list(periods))
        else:
            Lesson.__init__(self, module, group)

    def getLessonType(self):
        return "Lecture"


class Tutorial(Lesson):
    """
        This class represents a Tutorial as a lesson type
        It inherits from Lesson and is only used for type checking
        @author: Thyagesh Manikandan
    """
    def __init__(self, module, group, *periods):
        if len(periods) > 0:
            Lesson.__init__(self, module, group, list(periods))
        else:
            Lesson.__init__(self, module, group)

    def getLessonType(self):
        return "Tutorial"


class Laboratory(Lesson):
    """
        This class represents a Laboratory as a lesson type
        It inherits from Lesson and is only used for type checking
        @author: Thyagesh Manikandan
    """
    def __init__(self, module, group, *periods):
        if len(periods) > 0:
            Lesson.__init__(self, module, group, list(periods))
        else:
            Lesson.__init__(self, module, group)

    def getLessonType(self):
        return "Laboratory"

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
        @author: Thyagesh Manikandan
    """

    LESSON_TYPES = ["Lecture", "Tutorial", "Laboratory"]

    def __init__(self, code, examDate, dept, level):
        """
            @param code: refers to the module code in string
            @param examDate: the examDate in string ("DD/MM/YYYY hh:mm AM/PM")
            @param dept: refers to the department the module belongs to, in string
            @param level: refers to the level of modules (eg 1 for CS1231)
            @return: creates a module object with given params
        """

        # Test if given code is valid
        if not isinstance(code, str):
            raise TypeError("Given code is not of type string!")

        # Create the member variables to hold module's info
        self.lessons = {lessonType: [] for lessonType in self.LESSON_TYPES}  # The dict that holds the lessons
        self.code = code                                                     # The module code
        self.examDate = examDate                                             # The exam date
        self.dept = dept                                                     # The department
        self.level = level                                                   # The module level
        self.actualLectureCount = 0                                          # The num of lectures in the module
        self.actualTutorialCount = 0                                         # The num of tutorials in the module
        self.actualLabCount = 0                                              # The num of laboratories in the module

    def addLesson(self, lesson):
        """
        @param lesson: The lesson to add to current Module
        @return: None
        """

        assert issubclass(type(lesson), Lesson)
        assert self.code == lesson.getModuleCode()

        ## check if this is a second period to an existing lesson
        if self.hasLesson(lesson=lesson):
            internalLesson = self.getLesson(lesson.getId())
            internalLesson.mergeWithLesson(lesson)
            self.hasAlternativeLesson(internalLesson)
        elif not self.hasAlternativeLesson(lesson):
            self.lessons[lesson.getLessonType()].append(lesson)

    def removeLesson(self, lesson):
        """
        @param lesson: Lesson to be removed from this module
        @return:
        """

        assert issubclass(type(lesson), Lesson)
        assert self.code == lesson.getModuleCode()

        self.lessons[lesson.getLessonType()].remove(lesson)

    def removeAllExcept(self, lessonType, group):
        """
        @param lessonType: The lessonType to clear except for given Lesson group
        @param group: The group to keep as the compulsory Lesson
        @return: None
        """

        assert lessonType in self.LESSON_TYPES

        for lesson in self.lessons[lessonType]:
            if group in [lesson.getGroup()] + [tempLesson.getGroup() for tempLesson in lesson.getAlternatives()]:
                self.lessons[lessonType] = [lesson]
                break


    def doesNotClash(self, otherLessons):
        return all(any(not self_lesson.clashesWith(lesson) for lesson in otherLessons for self_lesson in self.__iter__(lessonType)) for lessonType in self.LESSON_TYPES if self.getActualLessonCount(lessonType) > 0)

    def hasAlternativeLesson(self, lesson):
        """
        @param lesson: Checks if a given lesson is an alternative to existing lesson. If so, adds it as an alternative
        @return: Boolean value that tells if given lesson is an alternative or not
        """

        for self_lesson in self.__iter__(lesson.getLessonType()):
            if self_lesson != lesson and self_lesson.isAlternative(lesson):
                self_lesson.addAlternative(lesson)
                return True
        return False

    def isValidLessonId(lessonId):
        """
        @param lessonId: Lesson Id to validate
        @return: Boolean value to represent success of validation
        """

        assert isinstance(lessonId, str)

        idSegments = lessonId.split('_')
        return len(idSegments) == 3 and all(segment != "" for segment in idSegments)

    def getLessonTypeFromId(self, lessonId):
        return lessonId.split("_")[1]

    def hasLesson(self, lesson):
        assert issubclass(type(lesson), Lesson)

        return any(lesson == self_lesson for self_lesson in self.lessons[lesson.getId().split("_")[1]])

    def hasLessonWithId(self, lessonId):
        assert self.isValidLessonId(lessonId)

        return any(lessonId == self_lesson.getId() for self_lesson in self.getLessonsOfType(self.getLessonTypeFromId(lessonId)))

    def getLessonsOccupyingTimeSlot(self, timeslot):
        """
        @param timeslot: The TimeSlot object used to get lessons that contain it
        @return: yields the lessons that contain the TimeSlot given
        """

        assert isinstance(timeslot, TimeSlot)

        for lesson in self:
            if lesson.hasSlot(timeslot):
                yield lesson



    def getClashingLessons(self, otherLesson):
        """
        @param conflictLesson: The Lesson object to be check for overlap
        @return:
        """

        assert issubclass(type(otherLesson), Lesson)

        conflictSet = set()
        for period in otherLesson:
            for timeslot in period:
                for conflictLesson in self.getLessonsOccupyingTimeSlot(timeslot):
                    conflictSet.add(conflictLesson)

        ## A separate for loop to avoid repetitions in lessons
        if conflictLesson in conflictSet:
            yield conflictLesson

    def getLesson(self, lessonId):
        ## only check in the list of lessons that are of the same type (Lec/Tut/Lab)
        for lesson in self.lessons[self.getLessonTypeFromId(lessonId)]:
            if lesson.getId() == lessonId:
                return lesson

        raise AssertionError("Unable to find Lesson of given Id")

    def getDepartment(self):
        return self.dept

    def getLevel(self):
        return self.level

    def getPossibleLessonsChoiceCount(self):
        """
        'Possible Lessons Choice' refers a choice of one lecture, tutorial and lab where applicable
        @return: number of such choices
        """

        lectureCount = 1 if 0 == self.getActualLectureCount() else self.getCurrentLectureCount()
        tutorialCount = 1 if 0 == self.getActualTutorialCount() else self.getCurrentTutorialCount()
        labCount = 1 if 0 == self.getActualLabCount() else self.getCurrentLabCount()

        return lectureCount * tutorialCount * labCount

    def getCode(self):
        return self.code

    def getExamDate(self):
        return self.examDate

    def setBaseparams(self):
        """
        This method is used to set the count of lessons in the actual module as,
        to optimise we would be removing some of the lessons prematurely

        @return: None
        """

        # * delete for loop later *
        lessonsToRemove = []
        for lesson in self:
            if self.hasAlternativeLesson(lesson):
                lessonsToRemove.append(lesson)
        for lesson in lessonsToRemove:
            self.removeLesson(lesson)

        self.actualLectureCount = self.getCurrentLectureCount()
        self.actualTutorialCount = self.getCurrentTutorialCount()
        self.actualLabCount = self.getCurrentLabCount()

    def getActualLectureCount(self):
        return self.actualLectureCount

    def getActualTutorialCount(self):
        return self.actualTutorialCount

    def getActualLabCount(self):
        return self.actualLabCount

    def getLectures(self):
        return self.lessons["Lecture"]

    def getTutorials(self):
        return self.lessons["Tutorial"]

    def getLaboratories(self):
        return self.lessons["Laboratory"]

    def getCurrentTutorialCount(self):
        return len(self.lessons["Tutorial"])

    def getCurrentLectureCount(self):
        return len(self.lessons["Lecture"])

    def getCurrentLabCount(self):
        return len(self.lessons["Laboratory"])

    def getActualLessonCount(self, lessonType):
        return len(self.lessons[lessonType])

    def getLessonsOfType(self, lessonType):
        assert lessonType in self.LESSON_TYPES

        return self.lessons[lessonType]

    def getCompulsoryLessons(self):
        """
        Yields all the compulsory lessons in the module, determined by a lack of other lessons in the respective lists
        @return: yields the lessons
        """
        if self.getActualLectureCount() is -1:
            self.setBaseparams()

        if (self.getActualLectureCount() == 1 and self.getCurrentLectureCount() > 0) or self.getCurrentLectureCount() == 1:
            yield self.getLectures()[0]
        if (self.getActualTutorialCount() == 1 and self.getCurrentTutorialCount() > 0) or self.getCurrentTutorialCount() == 1:
            yield self.getTutorials()[0]
        if (self.getActualTutorialCount() == 1 and self.getCurrentLabCount() > 0) or self.getCurrentLabCount() == 1:
            yield self.getLaboratories()[0]

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

    def __iter__(self, lessonTypeFilter = "", excludeList=set()):

        if lessonTypeFilter != "":
            assert lessonTypeFilter in self.LESSON_TYPES
            for lesson in self.lessons[lessonTypeFilter]:
                if lesson.getId() not in excludeList:
                    yield lesson
        else:
            for ltype in self.lessons.keys():
                for lesson in self.lessons[ltype]:
                    if lesson.getId() not in excludeList:
                        yield lesson


##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------


class ModuleSet(object):
    """
        This class is used a convenient container for a group of Module objects
        @author: Thyagesh Manikandan
    """
    def __init__(self):
        self.modules = {}
        self.moduleCount = 0

    def addModule(self, module, hasSetParams = False):
        assert isinstance(module, Module)

        if not hasSetParams:
            module.setBaseparams()

        self.modules[module.getCode()] = module
        self.moduleCount += 1

    def mergeWithModSet(self, anotherModSet):
        for mod in anotherModSet:
            if not isinstance(mod, Module):
                print mod
            self.addModule(mod, True)

    def removeModule(self, code):
        assert isinstance(code, str)

        del self.modules[code]
        self.moduleCount -= 1

    def getModuleCount(self):
        return self.moduleCount

    def getModule(self, code):
        for module in self:
            if module.getCode() == code:
                return module

    def __iter__(self):
        for module in self.modules.values():
            yield module

##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------------------------------------------

##Constants or hardcoded variables
dayToInt = {"MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3, "THURSDAY": 4, "FRIDAY": 5, "SATURDAY": 6, "SUNDAY": 7}
facChoices = ['ENGINEERING']
modCodeList = {'ST2334': {"Lecture": "SL1", "Tutorial": "T1"}, 'SSA2209': {"Tutorial": "D3"},
               'EE2024': {"Tutorial": "T9", 'Laboratory': 'B1'}, 'EE2023': {}, "EE2031": {'Laboratory': 'B2'}}
prevModCodeList = ['MA1505', 'MA1506', 'PC1432', 'CS1231', 'DSC2006', 'CG1101', 'CG1103', 'GEK1001', 'CS2103', 'CG1108', 'CG1413', 'DSC3202', 'EE2011', 'CS2104', 'CG2271', 'EE2020', 'EE2021']


def getJsonDataFromFile():
    fileMods = open('../data/modInfo.json')
    fileLessonTypes = open('../data/lessonTypesReference.json')
    fileDeptToFac = open('../data/departmentToFacultyConversion.json')

    modsJson = json.load(fileMods)
    lessonTypesJson = json.load(fileLessonTypes)
    deptToFac = json.load(fileDeptToFac)

    fileMods.close()
    fileLessonTypes.close()
    fileDeptToFac.close()

    return modsJson, lessonTypesJson, deptToFac

def isNotValidModDataSet(modData):

    isNotDict = not isinstance(modData, dict)
    if isNotDict:
        return True

    hasInvalidExamDate = modData['ExamDate'] == "Not Applicable."
    hasInvalidTimeTable = modData['Timetable'] == "Not Applicable."

    if not hasInvalidExamDate:
        hasNoExamDateThisSemester = not modData['ExamDate'].get(currentSem, '')
    else:
        return True

    if not hasInvalidTimeTable:
        isNotOfferedThisSemester = not modData['Timetable'].get(currentSem, [])
    else:
        return True

    return hasNoExamDateThisSemester or isNotOfferedThisSemester

def hasLessons(modData):
    isList = isinstance(modData["Timetable"][currentSem], list)
    hasLessonInDictFormat = all(isinstance(lesson, dict) for lesson in modData["Timetable"][currentSem])
    return isList and hasLessonInDictFormat

def loadAllModData():
    """
    Load all the json into local variables for manipulation
    Data include module information such as module code, Timetable, Exam Dates, Pre-Requisites, etc
        and conversion data from department to faculty and vice versa
        and a reference to a list of available lesson types
    @return:
    """

    modsJson, lessonTypesJson, deptToFac = getJsonDataFromFile()

    modSet = ModuleSet()
    preReqData = {}
    preclusionData = {}

    for modcode, modData in modsJson.items():
        modcode = str(modcode)

        if isNotValidModDataSet(modData):
            #get preclusion data as long as it is available
            if isinstance(modData, dict):
                preclusionData[modcode] = modData['Preclusion'] if isinstance(modData['Preclusion'], list) else ["None"]
            continue    # skip this iteration

        ## Gather preRequisite Data for the module
        preReqData[modcode] = modData['Tree']['children']
        preclusionData[modcode] = modData['Preclusion'] if isinstance(modData['Preclusion'], list) else ["None"]

        ## Get Module Information
        examDate = modData['ExamDate'][currentSem]
        modDept = modData['Department']
        level = modData["Level"];
        newMod = Module(modcode, examDate, modDept, level)

        # try:
        if hasLessons(modData):
            currentSemesterTimetable = modData['Timetable'][currentSem]
            for lesson in [lessons for lessons in currentSemesterTimetable]:
                lessonPeriod = Period(0, stime=int(lesson['StartTime']), etime=int(lesson['EndTime']), day=dayToInt[lesson['DayText']])
                newLesson = eval(lessonTypesJson[lesson['LessonType']])(modcode, str(lesson['ClassNo']), lessonPeriod)
                newMod.addLesson(newLesson)
        modSet.addModule(newMod)
    return modSet, deptToFac, preReqData, preclusionData


def generatePossibleModules(modInfoDict, masterModset, prevModCodeList):
    masterModset = filterByAllCriteria(masterModset, 3, ["All"], modInfoDict, prevModCodeList)
    print "Master Count: ", masterModset.getModuleCount()
    modList, masterModset = getPreallocatedModuleList(masterModset, modInfoDict)
#    print masterModset.getModuleCount()
    masterModset = removeConflicts(modInfoDict.keys(), masterModset)

    compulsoryLessons = []
    for mod in modList:
        for lesson in mod.getCompulsoryLessons():
            compulsoryLessons.append(lesson)


    startModListCollection = clock()
    possibleMods = []
    for mod in masterModset:
        if mod not in modList and mod.doesNotClash(compulsoryLessons):
            possibleMods.append(mod.getCode())

    print "Done Collecting Mod List: ", str(clock() - startModListCollection)
    return possibleMods, modList


def getPreallocatedModuleList(masterModset, modInfoDict):
    modList = []
    preallocStartTime = clock()
    for mod in masterModset:
        if mod.getCode() in modInfoDict.keys():
            for lessonType, group in modInfoDict[mod.getCode()].items():
                mod.removeAllExcept(lessonType, group)
            modList.append(mod)
    print "Time Taken for Prereq Calc: ", str(clock() - preallocStartTime)
    return modList, masterModset


def filterByAllCriteria(masterModset, maxLevel, modTypes, modInfoDict, prevModCodeList):
    startLevelFilterTime = clock()
    masterModset = filterByLevel(masterModset, maxLevel, modInfoDict.keys())
    startModuleTypeFilterTime = clock()
    print "Level Filter Time: ", str(startModuleTypeFilterTime - startLevelFilterTime)
    print "Master Count1: ", masterModset.getModuleCount()
    masterModset = filterByModuleType(masterModset, modTypes, modInfoDict.keys())
    startPrereqFilterTime = clock()
    print "Module Type Filter Time: ", str(startPrereqFilterTime - startModuleTypeFilterTime)
    print "Master Count2: ", masterModset.getModuleCount()
    masterModset = filterByPrereq(prevModCodeList, masterModset)
    print "Prereq Filter Time: ", str(clock() - startPrereqFilterTime)
    print "Master Count3: ", masterModset.getModuleCount()
    return masterModset


def filterByLevel(modset, maxlevel, modulesToKeep):
    modulesToDelete = []
    for mod in modset:
        firstNumInModCode = int(mod.getLevel())
        if firstNumInModCode > maxlevel and mod.getCode() not in modulesToKeep:
            modulesToDelete.append(mod.getCode())

    for modcode in modulesToDelete:
        modset.removeModule(modcode)
    return modset


def filterByModuleType(modset, moduleTypes, modulesToKeep):
    moduleTypeFilters = {"GE": isGeModule, "SS": isSingaporeStudiesModule, "Exposure": isExposureModule, "Technology": isTechnologyModule, "All": (lambda modcode: True)}
    moduleFilterFunction = lambda modcode: any(filterFunction(modcode) for filterType, filterFunction in moduleTypeFilters.items() if filterType in moduleTypes)
    modulesToDelete = []

    for mod in modset:
        modCode = mod.getCode()
        if not moduleFilterFunction(modCode) and (modCode not in modulesToKeep):
            modulesToDelete.append(modCode)

    for modCode in modulesToDelete:
        modset.removeModule(modCode)

    return modset


def isExposureModule(modcode):
    return modcode[-1] == "E"


def isTechnologyModule(modcode):
    return modcode[-1] == "T"


def isGeModule(modcode):
    return isGemModule(modcode) or isGekModule(modcode)


def isGemModule(modcode):
    return modcode[:3] == "GEM"


def isGekModule(modcode):
    return modcode[:3] == "GEK"


def isSingaporeStudiesModule(modcode):
    return modcode[:2] == "SS"


def filterByPrereq(modCodeList, masterModSet):
    modsToRemove = []
    for mod in masterModSet:
        modCode = mod.getCode()
        if modCode in modCodeList or not isEligibleByPrereq(modCode, modCodeList):
            modsToRemove.append(modCode)

    for modCode in modsToRemove:
        masterModSet.removeModule(modCode)

    return masterModSet


def isEligibleByPrereq(modCodeToTake, modCodesAlreadyTaken):
    preReqDict = preReqData[modCodeToTake]
    if not preReqDict:
        return True
    else:
        return satisfiesPrereq(preReqDict[0], modCodesAlreadyTaken)


def satisfiesPrereq(child, modList):
    if not child:
        return True
    if child['name'] == "and":
        return all(satisfiesPrereq(c1, modList) for c1 in child['children'])
    elif child['name'] == "or":
        return any(satisfiesPrereq(c1, modList) for c1 in child['children'])
    else:
        return child['name'] in modList


def removeConflicts(mainModCodeList, masterModSet):
#   print [modCode for modCode in mainModCodeList if not masterModSet.getModule(modCode)]
    examSlotsTime = clock()

    examSlots = [masterModSet.getModule(modCode).getExamDate() for modCode in mainModCodeList]
    modListToDelete = []

    examTimeConflictStartTime = clock()

    print "Examslots time: ", str(examTimeConflictStartTime - examSlotsTime)

    for mod in masterModSet:
        if mod.getCode() not in mainModCodeList:
            if hasNoExamConflict(mod, examSlots) and isOfRightFaculty(mod):
                pass
            else:
                modListToDelete.append(mod.getCode())

    for modCode in modListToDelete:
        masterModSet.removeModule(modCode)

    print "Exam and Faculty Conflict Time: ", str(clock() - examTimeConflictStartTime)

    return masterModSet


def hasNoExamConflict(mod, examSlots):
    return mod.getExamDate() == "Not Available." or mod.getExamDate() not in examSlots


def isOfRightFaculty(mod):
    return deptToFac[mod.getDepartment()] in facChoices


def createTimeBasedModules(timeRestraints):
    i = 1
    modset = ModuleSet()
    for restraint in timeRestraints:
        mod = Module("TimeRestrainModule " + str(i), "Not Available.", "COMPUTING & ENGINEERING",1)
        stime = restraint["StartTime"]
        while (stime + restraint["TimeNeeded"]) <= restraint["EndTime"]:
            tempPeriod = Period("EVERY WEEK", day=dayToInt[restraint["Day"]], stime=stime,
                                etime=(stime + restraint["TimeNeeded"]))
            tempLesson = Lecture("TimeRestrainModule " + str(i), stime, tempPeriod)
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
                for _ in mod.getClashingLessons(clashingLesson):
                    clashingModuleCount[clashingMod.getCode()] += 1
                    break

    return clashingModuleCount


def saveGeneratedListToFile(modList):
    fileN = open("test.txt", 'w')
    for mod in modList:
        fileN.write(mod + '\n')
    fileN.close()


def generationSequencer(data, modCodeList, prevModCodeList, timeRestrictions = {}):
    clock()
    print "copying..."
    modData = ModuleSet()
    modData.mergeWithModSet(data)
    timeToDeepCopy = clock()
    print "time to copy...", str(timeToDeepCopy)
    if not timeRestrictions:
        timeRestrictionsFile = open("../data/timeRestrictionsTestData.json")
        timeRestrictions = json.load(timeRestrictionsFile)
    testModSet = createTimeBasedModules(timeRestrictions)
    startOfMergeTime = clock()
    print "loading and adding time based modules: ", str(startOfMergeTime - timeToDeepCopy)
    modData.mergeWithModSet(testModSet)
    for mod in testModSet:
        modCodeList[mod.getCode()] = {}
        preReqData[mod.getCode()] = []
    print "merging time based mods and general mods: ", str(clock() - startOfMergeTime)
    prevModCodeList = addPreclusionToPrevMods(prevModCodeList, preclusionData)
    print "Generating Modules..."
    modList, testMods = generatePossibleModules(modCodeList, modData, prevModCodeList)
    print "Number of possible mods: " + str(len(modList)), str(clock() - timeToDeepCopy)
    for modcode in modList:
        print modcode
    return modList, testMods


def addPreclusionToPrevMods (prevModCodeList, preclusionData):
    newPrevModList = []
    for modcode in prevModCodeList:
        newPrevModList += [modcode] + preclusionData[modcode]

    return newPrevModList


print "loading data..."
loadedData, deptToFac, preReqData, preclusionData = loadAllModData()
print "Num of mods: " + str(loadedData.getModuleCount())
modList, testMods = generationSequencer(loadedData, modCodeList, prevModCodeList)
print "Num of mods: " + str(loadedData.getModuleCount())
modList, testMods = generationSequencer(loadedData, modCodeList, prevModCodeList)
# saveGeneratedListToFile(modList)

# mod = checkModuleAdding("YLS1201", 0)
# mod.setBaseparams()

## timeRestrictions = [{"Day": "MONDAY", "StartTime": 1200, "EndTime": 1400, "TimeNeeded": 30}]

# testModSet = createTimeBasedModules(timeRestrictions)
# clashingDict = getClashingModuleCount(loadedData, testModSet)
# print clashingDict
# for mod in testModSet:
# for lesson in mod:
#     for p in lesson:
# print p

####################
### Testing code ###
####################


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
                    newlesson = Laboratory(modcode, str(lesson['ClassNo']),
                                           Period(0, stime=int(lesson['StartTime']), etime=int(lesson['EndTime']),
                                                  day=dayToInt[lesson['DayText']]))
                else:
                    print(lesson['LessonType'])
                    newlesson = eval(LtypesJson[lesson['LessonType']])(modcode, str(lesson['ClassNo']),
                                                                       Period(0, stime=int(lesson['StartTime']),
                                                                              etime=int(lesson['EndTime']),
                                                                              day=dayToInt[lesson['DayText']]))
                newmod.addLesson(newlesson)
        except KeyError:
            noTimetableModCount += 1

    return newmod