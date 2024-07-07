import cv2
import numpy as np


def kmeans_run(img1, img2, distance=0.7, algorithms_name="SIFT"):
    algorithms_all = {
        "SIFT": cv2.SIFT_create(),
        "BRISK": cv2.BRISK_create(),
        "ORB": cv2.ORB_create()
    }
    algorithms = algorithms_all[algorithms_name]

    # 检测关键点并计算描述符
    kp1, des1 = algorithms.detectAndCompute(img1, None)
    kp2, des2 = algorithms.detectAndCompute(img2, None)

    if algorithms_name == "BRISK" or algorithms_name == "ORB":
        BFMatcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = BFMatcher.knnMatch(des1, des2, k=2)

    else:
        # FLANN parameters
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)  # or pass empty dictionary

        # 使用基于FLANN的匹配器, 筛选符合条件的坐标
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

    result = []
    good = []
    for i, (m, n) in enumerate(matches):
        # distance越小匹配度越高
        if m.distance < distance * n.distance:
            good.append(m)
            result.append(kp1[m.queryIdx].pt)
    if len(good) > 5:
        # Gets the coordinates of the key points
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # Compute the transformation matrix and MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            return None, None
        h, w, _ = img1.shape

        # Use the transformation matrix to obtain the coordinates of the four corners of the original image after
        # transformation
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        dst = cv2.perspectiveTransform(pts, M)

        x = [np.int32(dst)][0][0][0][0]
        y = [np.int32(dst)][0][0][0][1]

        w = [np.int32(dst)][0][2][0][0]
        h = [np.int32(dst)][0][2][0][1]

        return x, y, w, h
    else:
        return None, None, None, None
