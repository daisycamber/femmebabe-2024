import numpy as np
from .contours import get_image_contours

MIN_SCORE = 0.70

MIN_R1 = 0.9
MAX_R2 = 0.2
MAX_C = 1.2
MAX_T = 1

NUM_CONTOURS = 128

def kabsch_umeyama(A, B):
    assert A.shape == B.shape
    n, m = A.shape

    EA = np.mean(A, axis=0)
    EB = np.mean(B, axis=0)
    VarA = np.mean(np.linalg.norm(A - EA, axis=1) ** 2)

    H = ((A - EA).T @ (B - EB)) / n
    U, D, VT = np.linalg.svd(H)
    d = np.sign(np.linalg.det(U) * np.linalg.det(VT))
    S = np.diag([1] * (m - 1) + [d])

    R = U @ S @ VT
    c = VarA / np.trace(np.diag(D) @ S)
    t = EA - c * R @ EB
    print('{}-{}-{}'.format(R, c, t))
    return R, c, t

def validate_contours(R, c, t):
    if R[0] < MIN_R1: return False
    if R[1] > MAX_R2: return False
    if c > MAX_C: return False
    if abs(t[0]) > MAX_T or abs(t[1]) > MAX_T: return False
    return True

def compare_contours(imagea, imageb):
    pointsa = get_image_contours(imagea)[:NUM_CONTOURS]
    pointsb = get_image_contours(imageb)[:NUM_CONTOURS]
    score = 0
    count = 0
    for length in range(len(3, pointsa)):
        for a in range(0, len(pointsa)-length):
            for b in range(0, len(pointsa)-length):
                if a >= b-3: continue
                pointsaa = pointsa[a:a+length]
                pointsbb = pointsb[b:b+length]
                if compare_points(pointsaa, pointsbb): score = score + 1
                count = count + 1.0
    return score / count > MIN_SCORE

def compare_points(pointsa, pointsb):
    if len(pointsa) > len(pointsb):
        pointsa = pointsa[:len(pointsb)]
    else:
        pointsb = pointsb[:len(pointsa)]
    R, c, t = kabsch_umeyama(pointsa, pointsb)
    pointsb = np.array([t + c * R @ b for b in pointsb])
    return kabsch_umeyama(pointsa, pointsb)

def validate_melanin_images(imagea, imageb):
    return validate_contours(compare_contours(imagea, imageb))
