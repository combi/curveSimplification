import math
import random

from PYTHON.core import mathLib as mathLib

'''
https://bost.ocks.org/mike/simplify/
https://en.wikipedia.org/wiki/Binary_heap
'''


def visvalinganTuples(pointsTuples, epsilon=0.01):
    points = [mathLib.Vector(pnt) for pnt in pointsTuples]

    result = visvalingan(points, epsilon=epsilon)

    return result

def visvalingan(points, epsilon=0.01):
    """
    https://bost.ocks.org/mike/simplify/
    https://hull-repository.worktribe.com/output/459275
    """
    def computePointArea(points, i):
        return mathLib.triangleAreaFrom3Points(points[i-1], points[i], points[i+1])

    def sortPointsByArea(points, reverse=True):
        return sorted(points, key=lambda x: x[1], reverse=reverse)

    def sortPointsById(points):
        return sorted(points, key=lambda x: x[2])

    # print 'epsilon=', epsilon
    numPoints = len(points)
    print 'numPoints=', numPoints

    if numPoints <=3:
        newPoints = list(points)
    else:
        if not epsilon:
            newPoints = list(points)
        else:
            # rejectedPointsIds = set()
            print 'points:'
            for i, p in enumerate(points):
                print i, p

            workPoints = [[points[i], computePointArea(points, i), i-1] for i in range(len(points))[1:-1]]
            # workPoints.insert(0, [[None, None], None, 0])
            print 'workPoints:'
            for x in workPoints:
                print x

            pointsByArea = sortPointsByArea(workPoints[1::], reverse=False)

            print 'pointsByArea:'
            separationIndex = None
            for i, (point, currentArea, wIndex) in enumerate(pointsByArea):
                print '\t %d: point: %s' %(i, [point, currentArea, wIndex])


            biggestArea = pointsByArea[-1][1]
            print 'biggestArea=', biggestArea
            areaThreshold = epsilon * biggestArea
            print 'areaThreshold=', areaThreshold

            currentArea= pointsByArea[-1][1]
            print 'currentArea=', currentArea


            numPointsByArea = len(pointsByArea)
            print 'numPointsByArea=', numPointsByArea

            print 'looking for points of area less:'
            separationIndex = None
            for i, (point, currentArea, wIndex) in enumerate(pointsByArea):
                print '\t %d: point: %s' %(i, [point, currentArea, wIndex])
                separationIndex = i
                if currentArea > areaThreshold:
                    break
            print 'separationIndex=', separationIndex



            # iteration = 0
            # while pointsByArea and currentArea < areaThreshold:
            #     print
            #     print 'iteration:', iteration
            #     print '\t pointsByArea=', pointsByArea
            #     point, currentArea, wIndex = pointsByArea.pop()
            #     # print 'popped point:', point
            #     # print 'popped point, currentArea, wIndex=', point, currentArea, wIndex
            #     print
            #     print '\t popped:', [point, currentArea, wIndex]
            #     # print 'wIndex:', wIndex
            #     # prevPnt = workPoints[wIndex-1]
            #     # print '\t prevPnt=', prevPnt
            #     # nextPnt = workPoints[wIndex+1]
            #     # print '\t nextPnt=', nextPnt
            #     # prevArea =
            #     iteration += 1
            newPoints = [x[0] for x in sortPointsById(pointsByArea)]

    result = [points[0]] + newPoints + [points[-1]]

    return result

def douglasPeuckerTuples(pointsTuples, epsilon=0.01):
    """
    https://fr.wikipedia.org/wiki/Algorithme_de_Douglas-Peucker
    """
    points = [mathLib.Vector(pnt) for pnt in pointsTuples]

    result = douglasPeucker(points, epsilon=epsilon)

    return result

def douglasPeucker(points, epsilon=0.01, autoAdjustEpsilon=True):
    """
    https://fr.wikipedia.org/wiki/Algorithme_de_Douglas-Peucker
    """
    newPoints = None
    dmax   = -1
    index  = -1


    vFirst = points[0]
    vLast  = points[-1]
    for i in range(1, len(points)-2):
        vI = points[i]
        d  = vI.distToSegment(vFirst, vLast)
        if d > dmax:
            dmax = d
            index = i

    if not epsilon:
        newPoints = list(points)

    else:
        epsilon_ = (epsilon * dmax) + 1 if autoAdjustEpsilon else epsilon

        if dmax > epsilon_:
            recuRes1, _ = douglasPeucker(points[0:index+1], epsilon_, autoAdjustEpsilon=False)
            recuRes2, _ = douglasPeucker(points[index:] , epsilon_, autoAdjustEpsilon=False)
            newPoints   = recuRes1[0:-1]+recuRes2
        else:
            newPoints = [points[0], points[-1]]


    result  = (newPoints, dmax)
    return result



def testSorting():
    lSorted = [
    ('a',1),
    ('b',3),
    ('c',8),
    ('d',15),
    ('e',20),
    # ('f',30),
    # ('g',31),
    # ('h',40),
    ]

    print
    print 'lSorted:'
    for i,x in enumerate(lSorted):
        print i, x

    index = 3

    print
    item = lSorted.pop(index)
    print 'item=', item

    print
    print 'lSorted after pop:'
    for i,x in enumerate(lSorted):
        print i, x

    # changedItem = (item[0], 20)
    # changedItem = (item[0], 31)
    # changedItem = (item[0], 41)
    changedItem = (item[0], 2)
    print 'changedItem=', changedItem

    print 'now at index %d: %s' %(index, lSorted[index])


    listLength = len(lSorted)

    if changedItem[1] == lSorted[index][1]:
        lSorted.insert(index, changedItem)
    else:
        insertionPoint = index
        if changedItem[1] > lSorted[index][1]:
            while lSorted[insertionPoint][1] < changedItem[1]:
                insertionPoint+=1
                if insertionPoint >=listLength:
                    break
        else:
            # while lSorted[insertionPoint][1] > changedItem[1]:
            while insertionPoint > -1:
                insertionPoint-=1
                print 'insertionPoint=%d (%s)' %(insertionPoint, lSorted[insertionPoint][1])
                if lSorted[insertionPoint][1] > changedItem[1]:
                    print '%s > %s breaking' %(lSorted[insertionPoint][1], changedItem[1])
                    break
        print 'insertionPoint should be', insertionPoint
        lSorted.insert(insertionPoint, changedItem)


        # for i, item in enumerate(lSorted[index+1:]):
        #     print i, item
        #     if changedItem[1] >= item[1]:
        #         print 'diiiiing'

    print
    print 'lSorted:'
    for i,x in enumerate(lSorted):
        print i, x


class MinHeap(object):
    def __init__(self, members):
        self.members = list(members)

    def children(self, i):
        result = None
        numMembers = len(self.members)
        i1 = (2*i)+1  # index du premier child
        i2 = (2*i)+2  # index du second child

        # Divers tests pour gerer les cas des nodes qui sont vers la fin du tableau, la ou
        # des nodes sont susceptibles de ne pas avoir d'enfant
        if i2 > numMembers-1:
            result = [None, None]
        elif i2 <= numMembers-1:
            result = [self.members[i1], self.members[i2]]
        elif i1 <= numMembers-1:
            result = [self.members[i1], None]
        return result

    def parent(self, i):
        parent = self.members[int(math.floor(i-1)/2)] if i else None
        return parent

def testMinHeap():
    random.seed(123)
    arrayUnsorted = [random.randint(-50,50) for _ in range(10)]
    print 'arrayUnsorted=', arrayUnsorted
    minHeap = MinHeap(arrayUnsorted)

    print 'minHeap.members=', minHeap.members
    i = 0
    item = minHeap.members[i]
    print 'item at %d is %s' %(i, item)
    print 'children of item %d are %s' %(item, minHeap.children(i))
    print 'parent of item %d is %s' %(item, minHeap.parent(i))


if __name__=="__main__":
    # testSorting()
    testMinHeap()

