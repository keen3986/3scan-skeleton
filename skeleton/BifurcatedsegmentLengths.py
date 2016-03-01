import itertools
import time

import numpy as np
import networkx as nx

from skeleton.networkxGraphFromarray import getNetworkxGraphFromarray
<<<<<<< HEAD
=======
from skeleton.cliqueRemovig import removeCliqueEdges
>>>>>>> dabc0f3b6bcb1524a4adaa5d6dd20d93dc5e79be
from skeleton.segmentLengths import _removeEdgesInVisitedPath, _getDistanceBetweenPointsInpath


def getBifurcatedSegmentsAndLengths(imArray, skelOrNot=True, arrayOrNot=True):
    """
        algorithm - 1) go through each of the disjoint graphs
                    2) decide if it is one of the following a) line
                    b) cycle c) acyclic tree like structure d) cyclic tree like structure
                    e) single node
                    3) Find all the paths in a given disjoint graph from a point whose degree is greater
                    than or equal to 2 to a point whose degree equal to one
                    4) calculate distance between edges in each path and displacement to find curve length and
                    curve displacement to find tortuosity
                    5) Remove all the edges in this path once they are traced
    """
    if arrayOrNot is False:
        networkxGraph = imArray
    else:
        networkxGraph = getNetworkxGraphFromarray(imArray, skelOrNot)
    assert networkxGraph.number_of_selfloops() == 0
    # intitialize all the common variables
    startt = time.time()
    segmentCountdict = {}
    segmentLengthdict = {}
    segmentTortuositydict = {}
    totalSegments = 0
    # list of disjointgraphs
    disjointGraphs = list(nx.connected_component_subgraphs(networkxGraph))
    for ithDisjointgraph, subGraphskeleton in enumerate(disjointGraphs):
        nodes = subGraphskeleton.nodes()
        if len(nodes) == 1:
            " if it is a single node"
        else:
            """ if there are more than one nodes decide what kind of subgraph it is
                if it has cycles alone, or it's a cyclic/acyclic graph"""
            nodes.sort()
            nodeDegreedict = nx.degree(subGraphskeleton)
            degreeList = list(nodeDegreedict.values())
            cycleList = nx.cycle_basis(subGraphskeleton)
<<<<<<< HEAD
            cycleList = [item for item in cycleList if len(item) != 3]
=======
>>>>>>> dabc0f3b6bcb1524a4adaa5d6dd20d93dc5e79be
            cycleCount = len(cycleList)
            if set(degreeList) == set((1, 2)):
                continue
            elif set(degreeList) == {2}:
                """ it is a circle, set tortuosity to infinity (NaN) """
                cycleList = nx.cycle_basis(subGraphskeleton)
                cycle = cycleList[0]
                sourceOnCycle = cycle[0]
                segmentCountdict[sourceOnCycle] = 1
                segmentLengthdict[1, sourceOnCycle, sourceOnCycle] = _getDistanceBetweenPointsInpath(cycle, 1)
                segmentTortuositydict[1, sourceOnCycle, sourceOnCycle] = 0
                _removeEdgesInVisitedPath(subGraphskeleton, cycle, 1)
            elif cycleCount >= 1:
                visitedSources = []
                """go through each of the cycles and find the lengths, set tortuosity to NaN (circle)"""
                for nthCycle, cyclePath in enumerate(cycleList):
                    sourceOnCycle = cyclePath[0]
                    if sourceOnCycle not in visitedSources:
                        "check if the same source has multiple loops/cycle"
                        segmentCountdict[sourceOnCycle] = 1
                    else:
                        segmentCountdict[sourceOnCycle] = segmentCountdict[sourceOnCycle] + 1
                    visitedSources.append(sourceOnCycle)
                    segmentLengthdict[segmentCountdict[sourceOnCycle], sourceOnCycle, sourceOnCycle] = _getDistanceBetweenPointsInpath(cyclePath, 1)
                    segmentTortuositydict[segmentCountdict[sourceOnCycle], sourceOnCycle, sourceOnCycle] = 0
                    _removeEdgesInVisitedPath(subGraphskeleton, cyclePath, 1)
                if subGraphskeleton.number_of_edges() != 0:
                    "all the cycles in the graph are checked now look for the tree characteristics in this subgraph"
                    # collecting all the branch and endpoints
                    branchpoints = [k for (k, v) in nodeDegreedict.items() if v > 2]
                    listOfPerms = list(itertools.permutations(branchpoints, 2))
                    branchpoints.sort()
                    for sourceOnTree, item in listOfPerms:
                        if nx.has_path(subGraphskeleton, sourceOnTree, item) and sourceOnTree != item:
                            simplePaths = list(nx.all_simple_paths(subGraphskeleton, source=sourceOnTree, target=item))
                            for simplePath in simplePaths:
                                if len(list(set(branchpoints) & set(simplePath))) == 2:
                                    if sourceOnTree not in visitedSources:
                                        "check if the same source has multiple segments"
                                        segmentCountdict[sourceOnTree] = 1
                                    else:
                                        segmentCountdict[sourceOnTree] = segmentCountdict[sourceOnTree] + 1
                                    visitedSources.append(sourceOnTree)
                                    curveLength = _getDistanceBetweenPointsInpath(simplePath)
                                    curveDisplacement = np.sqrt(np.sum((np.array(sourceOnTree) - np.array(item)) ** 2))
                                    segmentLengthdict[segmentCountdict[sourceOnTree], sourceOnTree, item] = curveLength
                                    segmentTortuositydict[segmentCountdict[sourceOnTree], sourceOnTree, item] = curveLength / curveDisplacement
                                    _removeEdgesInVisitedPath(subGraphskeleton, simplePath, 0)
            else:
                """ acyclic tree nodes with degrees greater than 2 exist"""
                branchpoints = [k for (k, v) in nodeDegreedict.items() if v > 2]
                listOfPerms = list(itertools.permutations(branchpoints, 2))
                branchpoints.sort()
                visitedSources = [];
                for sourceOnTree, item in listOfPerms:
                    if nx.has_path(subGraphskeleton, sourceOnTree, item) and sourceOnTree != item:
                        simplePaths = list(nx.all_simple_paths(subGraphskeleton, source=sourceOnTree, target=item))
                        for simplePath in simplePaths:
                            if len(list(set(branchpoints) & set(simplePath))) == 2:
                                if sourceOnTree not in visitedSources:
                                    "check if the same source has multiple segments, if it doesn't number of segments is 1"""
                                    segmentCountdict[sourceOnTree] = 1
                                else:
                                    segmentCountdict[sourceOnTree] = segmentCountdict[sourceOnTree] + 1
                                visitedSources.append(sourceOnTree)
                                curveLength = _getDistanceBetweenPointsInpath(simplePath)
                                curveDisplacement = np.sqrt(np.sum((np.array(sourceOnTree) - np.array(item)) ** 2))
                                segmentLengthdict[segmentCountdict[sourceOnTree], sourceOnTree, item] = curveLength
                                segmentTortuositydict[segmentCountdict[sourceOnTree], sourceOnTree, item] = curveLength / curveDisplacement
                                _removeEdgesInVisitedPath(subGraphskeleton, simplePath, 0)
<<<<<<< HEAD
=======
    # print(sum(segmentCountdict.values()), len(segmentTortuositydict), len(segmentLengthdict))
>>>>>>> dabc0f3b6bcb1524a4adaa5d6dd20d93dc5e79be
    totalSegments = len(segmentLengthdict)
    print("time taken to calculate segments and their lengths is %0.3f seconds" % (time.time() - startt))
    return segmentCountdict, segmentLengthdict, segmentTortuositydict, totalSegments


if __name__ == '__main__':
    from skeleton.orientationStatisticsSpline import plotKde
    shskel = np.load("/home/pranathi/Downloads/twodimageslices/twodkskeletonslices/Skeleton.npy")
    segmentCountdict, segmentLengthdict, segmentTortuositydict, totalSegments = getBifurcatedSegmentsAndLengths(shskel)
    plotKde(segmentCountdict)
    plotKde(segmentLengthdict)
    plotKde(segmentTortuositydict)
