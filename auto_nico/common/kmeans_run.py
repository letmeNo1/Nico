import cv2
import numpy as np
from sklearn.cluster import MeanShift


def kmeans_run(img1, img2, distance=0.7, algorithms_name="SIFT", Scale=1):
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    if algorithms_name == "template_match":
        x, y, w, h = template_matching(img1_gray, img2_gray)
        if x is None:
            return None, None, None, None
        else:
            return int(x / Scale), int(y / Scale), 10, 10
    else:
        algorithms_all = {
            "SIFT": cv2.SIFT_create(),
            "BRISK": cv2.BRISK_create(),
            "ORB": cv2.ORB_create()
        }
        algorithms = algorithms_all[algorithms_name]

        kp1, des1 = algorithms.detectAndCompute(img1_gray, None)
        kp2, des2 = algorithms.detectAndCompute(img2_gray, None)
        if algorithms_name in ["BRISK", "ORB"]:
            BFMatcher = cv2.BFMatcher(cv2.NORM_HAMMING)
            matches = BFMatcher.knnMatch(des1, des2, k=2)
        else:
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(des1, des2, k=2)

        good = [m for m, n in matches if m.distance < distance * n.distance]

        if len(good) >= 5:
            points = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 2)

            ms = MeanShift(bandwidth=50)
            ms.fit(points)
            labels = ms.labels_

            core_samples_mask = (labels == np.argmax(np.bincount(labels)))
            filtered_points = points[core_samples_mask]

            x_mean, y_mean = np.mean(filtered_points, axis=0)

            x = int(x_mean)
            y = int(y_mean)

            return int(x / Scale), int(y / Scale), 10, 10
        else:
            return None, None, None, None


def template_matching(img1, img2, method=cv2.TM_CCOEFF_NORMED):
    result = cv2.matchTemplate(img2, img1, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    h, w = img1.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img2, top_left, bottom_right, (0, 255, 0), 2)
    if max_val < 0.8:
        return None, None, None, None
    else:
        return top_left[0], top_left[1], bottom_right[0], bottom_right[1]
