from scipy.spatial import ConvexHull
import itertools

import networkx as nx
import numpy as np
import random

from skeleton.networkxGraphFromarray import getNetworkxGraphFromarray as skeletonGraph
from skeleton.cliqueRemoving import removeCliqueEdges

"""
   graph obtained using nx.from_dict_of_lists()
   by supplying 26 nonzero adjacent vertices
   2D skeletonization using inbuilt python as in the below link
   http://scikit-image.org/docs/dev/api/skimage.morphology.html#skimage.morphology.skeletonize
   3D Thinning using parallel 12 subiteration curve thinning by Palagyi
   folowd by unit width curve skeleton implementation
   http://web.inf.u-szeged.hu/ipcg/publications/papers/PalagyiKuba_GMIP1999.pdf
"""


def embed2in3(arr):
    """Embed a 2d shape in a 3d array,
    along all possible testing directions."""

    assert arr.dtype == np.uint8
    assert arr.ndim == 2

    m, n = arr.shape
    embeddedInX = np.zeros((3, m, n), dtype=np.uint8)
    embeddedInX[1, :, :] = arr

    embeddedInY = np.zeros((m, 3, n), dtype=np.uint8)
    embeddedInY[:, 1, :] = arr

    embeddedInZ = np.zeros((m, n, 3), dtype=np.uint8)
    embeddedInZ[:, :, 1] = arr

    return embeddedInX, embeddedInY, embeddedInZ


def reorders(arr):
    for xf, yf, zf in itertools.combinations_with_replacement([1, -1], 3):
        yield arr[::xf, ::yf, ::zf]


def doEmbeddedTest(arr, expectedResult=None):
    assert arr.ndim == 2
    twoResult = getGraphProperties(removeCliqueEdges(skeletonGraph(arr, False)))

    if expectedResult is not None:
        assert twoResult == expectedResult
    else:
        expectedResult = twoResult

    for embedding in embed2in3(arr):
        allOrientationsTest(embedding, expectedResult)

    return twoResult


def allOrientationsTest(arr, expectedResult=None):
    assert arr.ndim == 3
    print(expectedResult)
    i = 0
    for reoriented in reorders(arr):
        i += 1
        print("ith reordering", i)
        np.save("reoriented.npy", reoriented)
        result = getGraphProperties(removeCliqueEdges(skeletonGraph(reoriented, False)))
        print(expectedResult, result)
        assert result[1] == expectedResult[1]


def getGraphProperties(g):
    """Return a count of the nodes, edges, and
    simple cycles in a graph"""
    cycleCount = len(nx.cycle_basis(g))
    # http://stackoverflow.com/questions/21739569/finding-separate-graphs-within-a-graph-object-in-networkx
    # make an undirected copy of the digraph
    UG = g.to_undirected()
    # extract subgraphs
    disjointGraphs = len(list(nx.connected_component_subgraphs(UG)))
    return cycleCount, disjointGraphs

# One single tiny loop
tinyLoop = np.array([[1, 1, 1],
                     [1, 0, 1],
                     [1, 1, 1]], dtype=np.uint8)


# This is a simple suite of test cases for the
# Algo which takes in skeletonized images, and emits
# networkx graphs
# Some quick and dumb tests against the core algorithim
def test_simpleLoopEmbedded():
    doEmbeddedTest(tinyLoop, (1, 1))


# Three independant loops
multiLoop = np.zeros((25, 25))
multiLoop[2:5, 2:5] = tinyLoop
multiLoop[7:10, 7:10] = tinyLoop
multiLoop = np.uint8(multiLoop)


def test_multiLoopEmbedded():
    doEmbeddedTest(multiLoop, (2, 2))

cros = np.zeros((25, 25, 25), dtype=np.uint8)
cros[:, 12, :] = 1
cros[12, :, :] = 1


def test_crossEmbedded():
    allOrientationsTest(cros, (0, 1))

hillbert = np.array([[[1, 1, 1],
                      [1, 0, 1],
                      [1, 0, 1]],
                     [[0, 0, 0],
                      [0, 0, 0],
                      [1, 0, 1]],
                     [[1, 1, 1],
                      [1, 0, 1],
                      [1, 0, 1]]], dtype=np.uint8)


def test_hillbert():
    allOrientationsTest(hillbert, expectedResult=(1, 1))

loopPair = np.array([[1, 1, 1],
                     [1, 0, 1],
                     [1, 1, 1],
                     [1, 0, 1],
                     [1, 1, 1]], dtype=np.uint8)

parallelepiped = np.zeros((13, 17, 19), dtype=np.uint8)
parallelepiped[2:-2, 2:-2, 2:-2] = 1


def test_parallelepiped():
    allOrientationsTest(parallelepiped, expectedResult=(0, 1))


squae = np.zeros((20, 20), dtype=np.uint8)
squae[2:-2, 2:-2] = 1


def test_square():
    doEmbeddedTest(squae, expectedResult=(0, 1))


frame = np.zeros((10, 10), dtype=np.uint8)

frame[2:-2, 2:-2] = 1
frame[4:-4, 4:-4] = 0


def test_frame():
    c, d = doEmbeddedTest(frame, (1, 1))
    assert c == 1

framedSquare = frame.copy()
framedSquare[6:-6, 6:-6] = 1


def test_framedSquare():
    c, d = doEmbeddedTest(framedSquare)


hevi = np.zeros((20, 20), dtype=np.uint8)
hevi[10:, :] = 1


def test_circle():
    i = np.zeros((25, 25), dtype=np.uint8)
    xs, ys = np.mgrid[-1:1:25j, -1:1:25j]

    for trial in range(5):
        i[:] = 0
        r = np.random.uniform(3, 10)
        xc, yc = np.random.uniform(-1, 1, size=2)
        mask = ((xs ** 2) + (ys ** 2)) < r ** 2
        i[mask] = 1

        # 2d blob should congeal down to a point
        # pv: congealing down to a 3 point skeleton/line 25 by 25 image
        # hence considering only the equivalence of the cycles and independent graphs
        c, d = doEmbeddedTest(i)
        assert c == 0 and d == 1


def test_Heaviside():
    doEmbeddedTest(hevi, (0, 1))


def getRing(ri, ro, size=(25, 25)):
    """
    Make a annular ring in 2d.
    The inner and outer radius are given as a
    percentage of the overall size.
    """
    n, m = size
    xs, ys = np.mgrid[-1:1:n * 1j, -1:1:m * 1j]
    r = np.sqrt(xs ** 2 + ys ** 2)

    torus = np.zeros(size, dtype=np.uint8)
    torus[(r < ro) & (r > ri)] = 1
    return torus

concentricCircles = getRing(0.1, 0.2) + getRing(0.4, 0.5) + getRing(0.7, 0.9)


def test_ellipse():
    i = np.zeros((25, 25), dtype=np.uint8)
    xs, ys = np.mgrid[-1:1:25j, -1:1:25j]

    aspect = random.randint(1, 2) / 10
    for trial in range(5):
        i[:] = 0
        r = np.random.uniform(3, 10)
        # xc, yc = np.random.uniform(-1, 1, size=2)
        mask = (aspect * ((xs ** 2) + (ys ** 2))) < r ** 2
        i[mask] = 1

        # 2d blob should congeal down to a point
        # pv congealing to a line
        c, d = doEmbeddedTest(i)
        assert c == 0 and d == 1


def test_convex3DBlob():
    xs = np.random.uniform(-1, 1, size=5)
    ys = np.random.uniform(-1, 1, size=5)
    zs = np.random.uniform(-1, 1, size=5)

    xyzs = list(zip(xs, ys, zs))

    hullz = ConvexHull(xyzs)

    xf, yf, zf = np.mgrid[-1:1:50j, -1:1:50j, -1:1:50j]
    i = np.zeros(xf.shape, dtype=np.uint8)
    for x, y, z, c in hullz.equations:
        mask = (xf * x) + (yf * y) + (zf * z) - c < 0
        i[mask] = 1
    allOrientationsTest(i, (0, 1))
