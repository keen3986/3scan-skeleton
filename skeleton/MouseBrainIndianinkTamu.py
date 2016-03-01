from scipy.misc import imread, imsave
import numpy as np
import time
from time import localtime, strftime
from scipy import ndimage
import os

from skeleton.radiusOfNodes import _getBouondariesOfimage
from skeleton.convOptimize import getSkeletonize3D
from skeleton.unitwidthcurveskeleton import getShortestPathskeleton

"""
    takes in 2D image slices from the root directory
    converts them to binary and returns the thinnned 3d volume
    as a boolean array, image slices as pngs in the root directory
    under name twodkskeletonslices
"""

from skimage.filters import threshold_otsu


def convertToBinary(image, convert):
    """
       threshod an image and display, a global threshold image is in binary_global
       if convert is True,
       object is in brighter contrast and viceversa
    """
    global_thresh = threshold_otsu(image)
    if convert:
        binary_global = image > global_thresh
    else:
        binary_global = image < global_thresh
    return np.uint8(binary_global), global_thresh


def getDiceSimilarityCOefficient(inputIm, thresholdedIm):
    """
        Takes an original image and its segmentation result
        gives the efficiency of a segmentation with dice similariy statistic
        defined as 2(A & B)/ A + B where A, B are the original and segmentation
        result, & intersection ("non zero voxels in common"), A + B indicates sum of non
        zero voxels in A and B
    """
    numerator = np.sum(np.logical_and(thresholdedIm, inputIm))
    denominator = len(np.transpose(np.nonzero(inputIm))) + len(np.transpose(np.nonzero(thresholdedIm)))
    dsc = numerator / denominator
    return dsc


def skeletonizeAndSave(contrast=False, aspectRatio=[1, 1, 1], zoom=True, findMip=False):
    startt = time.time()
    count = 0
    root = input("please enter a root directory where your 2D slices are----")
    formatOfFiles = input("please enter the format of 2D files---")
    # list and sort all the files in the given greyscale
    # input root directory
    # which is to be skeletonized
    listOffiles = os.listdir(root)
    if sorted(listOffiles) == listOffiles:
        listOffiles = listOffiles
    else:
        listOffiles.sort()
    # carefully select all the files with the extension of
    # the two dimensional slice images needed and count the
    # number of slices to allocate memory for the three
    # dimensional volume
    listOfJpgs = []
    for file in listOffiles:
        if file.endswith(formatOfFiles):
            listOfJpgs.append(file)
            count = count + 1
    # i = imread((os.path.join(root, listOffiles[0])))
    # m, n = np.shape(i)
    inputIm = np.zeros((298, 512, 512), dtype=np.uint8)
    count1 = 0
    if findMip:
        mip = np.ones((512, 512), dtype=int) * 255
    # print("x, y, z dimensions are %i %i %i  " % (m, n, 514))
    for fileName in listOfJpgs[:298]:
        # imageExtract = np.zeros((512, 512), dtype=np.uint8)
        image = imread((os.path.join(root, fileName)))
        # imageExtract = image[0:512, 0:512]
        imageExtract = ndimage.filters.gaussian_filter(image, sigma=1.4)
        inputIm[count1][:][:] = imageExtract
        count1 += 1
    # stackSmoothedReplicated = ndimage.interpolation.zoom(stackSmoothed, zoom=aspectRatio, order=0)
    # stackSmoothedLinearInterpolated = ndimage.interpolation.zoom(stackSmoothed, zoom=aspectRatio, order=1)
    # stackSmoothedQuadratic = ndimage.interpolation.zoom(stackSmoothed, zoom=aspectRatio, order=2)
    # stackUnSmoothedQuadratic = ndimage.interpolation.zoom(stackUnsmoothed, zoom=aspectRatio, order=2)
    # stackSmoothedCubic = ndimage.interpolation.zoom(stackSmoothed, zoom=aspectRatio, order=3, prefilter=False)
    # stackUnSmoothedReplicated = ndimage.interpolation.zoom(stackUnsmoothed, zoom=aspectRatio, order=0)
    # stackUnSmoothedLinearInterpolated = ndimage.interpolation.zoom(stackUnsmoothed, zoom=aspectRatio, order=1)
    # stackUnSmoothedCubic = ndimage.interpolation.zoom(stackUnsmoothed, zoom=aspectRatio, order=3, prefilter=False)
        if findMip == 1:
            if contrast is False:
                inds = image < mip  # find where image intensity < min intensity
            else:
                inds = image > mip
                mip[inds] = image[inds]  # update the minimum value at each pixel
    if zoom is True:
        thresholdedIm, globalThreshold = convertToBinary(inputIm, contrast)
    else:
        inputIm = ndimage.filters.gaussian_filter(inputIm, sigma=1)
        thresholdedIm, globalThreshold = convertToBinary(inputIm, contrast)
    boundaryIm = _getBouondariesOfimage(thresholdedIm)
    print("skeletonizing started at")
    print(strftime("%a, %d %b %Y %H:%M:%S ", localtime()))
    if os.path.isdir(root + 'twodbinaryslices/') == 0 and os.path.isdir(root + 'twodkskeletonslices/') == 0:
        print("directory doesnt exist")
        print("threshold of the 3d volume is", globalThreshold)
        os.mkdir(root + 'twodbinaryslices')
        for i in range(thresholdedIm.shape[0]):
            imsave(root + 'twodbinaryslices/' + 'binaryIm%i.png' % i, thresholdedIm[i] * 255)
        os.mkdir(root + 'twodkskeletonslices')
        np.save(root + 'twodkskeletonslices/' + 'Boundaries.npy', boundaryIm)
        if findMip:
            np.save(root + 'twodkskeletonslices/' + 'mip.npy', mip)
        np.save(root + 'twodkskeletonslices/' + 'Greyscale.npy', inputIm)
        np.save(root + 'twodkskeletonslices/' + 'Binary.npy', thresholdedIm)
        skeletonIm = getSkeletonize3D(thresholdedIm)
        np.save(root + 'twodkskeletonslices/' + 'Skeleton.npy', skeletonIm)
        shortestPathSkel = getShortestPathskeleton(skeletonIm)
        for i in range(skeletonIm.shape[0]):
            imsave(root + 'twodkskeletonslices/' + 'skeletonIm%i.png' % i, skeletonIm[i] * 255)
        np.save(root + 'twodkskeletonslices/' + 'ShortestPathskeleton.npy', shortestPathSkel)
    else:
        print("already skeletonized and saved directory existsexists")
        shortestPathSkel = np.load(root + 'twodkskeletonslices/' + 'ShortestPathskeleton.npy')
        boundaryIm = np.load(root + 'twodkskeletonslices/' + 'Boundaries.npy')
        skeletonIm = np.load(root + 'twodkskeletonslices/' + 'Skeleton.npy')
    print("skeletonizing ended at")
    print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    print("\ttime taken to obtain skeleton and save all the outputs is %0.3f seconds" % (time.time() - startt))
    label_img1, countObjects = ndimage.measurements.label(thresholdedIm, structure=np.ones((3, 3, 3), dtype=np.uint8))
    label_img2, countObjectsSkel = ndimage.measurements.label(skeletonIm, structure=np.ones((3, 3, 3), dtype=np.uint8))
    label_img2, countObjectsShkel = ndimage.measurements.label(shortestPathSkel, structure=np.ones((3, 3, 3), dtype=np.uint8))
    assert countObjects == countObjectsSkel
    print("disjoint objects in the input image", countObjects)
    print("disjoint objects in the skeletonized image", countObjectsSkel)
    print("disjoint objects in the ShortestPathskeleton image", countObjectsShkel)
    return shortestPathSkel, boundaryIm


def main():
    ShortestPathskeleton, boundaryIm = skeletonizeAndSave(zoom=True, aspectRatio=[7, 1, 1])


if __name__ == '__main__':
    main()


# maxip = np.amin(stackUnSmoothedQuadratic, 0)
# maxipS = np.amin(stackSmoothedQuadratic, 0)
# maxip1 = np.amax(stackUnSmoothedQuadratic < tu, 0)
# maxip1S = np.amax(stackSmoothedQuadratic < ts, 0)
# plt.subplot(2, 1, 1)
# plt.imshow(maxip, cmap='gray')
# # plt.title('grey scale mip of unsmoothed quadratic interpolated volume pf = True')
# plt.subplot(2, 1, 2)
# plt.imshow(maxip1, cmap='gray')
# plt.title('thresholded mip of unsmoothed quadratic interpolated volume (no clipping) pf = True')
# plt.subplot(2, 1, 3)
# plt.imshow(maxipS, cmap='gray')
# plt.title('grey scale mip of smoothed quadratic interpolated volume')
# plt.subplot(2, 2, 4)
# plt.imshow(1 - maxip1S, cmap='gray')
# plt.title('thresholded mip of smoothed quadratic interpolated volume (no clipping)')

# stackSmoothedQuadratic = ndimage.interpolation.zoom(stackSmoothed, zoom=aspectRatio, order=2, prefilter=False)
# stackUnSmoothedQuadratic = ndimage.interpolation.zoom(stackUnsmoothed, zoom=aspectRatio, order=2, prefilter=False)

# plt.subplot(1, 3, 1)
# plt.imshow(unSmoothedQuad[0], cmap='gray')
# plt.subplot(1, 3, 2)
# plt.imshow(unSc[0], cmap='gray')
# plt.subplot(1, 3, 3)
# plt.imshow(unSc2[0], cmap='gray')

# plt.subplot(2, 1, 1)
# plt.hist(z,256,[0,256]),plt.show()
# plt.subplot(2, 1, 2)
# A = z[labels==0]
# B = z[labels==1]
# plt.hist(A,256,[0,256],color = 'r')
# plt.hist(B,256,[0,256],color = 'b')
# plt.hist(centers,32,[0,256],color = 'y')
# plt.show()

# for I in range(0, skeletonER.shape[0]):
#     plt.subplot(1, 3, 1)
#     # maxip = np.amax(interpolatedIm[I:I + 7], 0)
#     plt.imshow(grey[I], cmap='gray')
#     plt.subplot(1, 3, 2)
#     plt.imshow(threshold[I], cmap='gray')
#     plt.subplot(1, 3, 3)
#     plt.imshow(skeletonER[I], cmap='gray')
#     plt.savefig('Mosaic%i.png' % I, bbox_inches='tight')


# #     plt.subplot(1, 3, 1)
# #     plt.imshow(maxip, cmap='gray')
# #     plt.subplot(1, 3, 2)
# #     plt.imshow(maxip2, cmap='gray')


# plt.subplot(1, 2, 1)
# plt.imshow(subSubvolume[0], cmap='gray')
# plt.subplot(1, 2, 2)
# plt.imshow(255-subSubvolume[0], cmap='gray')


# for i in range(threshold.shape[0]):
#     imsave(root + 'twodThresholdslicesgoodRegionOT/' + 'thresholdot%i.png' % i, threshold[i] * 255)

# for i in range(subSubvolume.shape[0]):
#     imsave(root + 'twodGreyslicesgoodRegion/' + 'GreyGR%i.png' % i, subSubvolume[i])
