import cv2
import numpy as np
import sys
import math
import os

def show(img):
    cv2.imshow("titulo", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def draw_contours(img, points, color, size):
    cv2.drawContours(img, points, -1, color, size)
    show(img)

def get_distances(file):
    print(0.1)
    src = cv2.imread(file, 1) # read input image
    print(0.2)
    show(src)

    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) # convert to grayscale
    print(0.3)

    blur = cv2.blur(gray, (3,3)) # blur the image
    print(0.4)

    ret, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
    print(0.5)
    show(thresh)

    mask = cv2.Canny(thresh, 0, 255)
    print(0.6)
    show(mask)

    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(0.7)

    cnt=[]
    for i in range(len(contours)):
        cnt.extend(contours[i])
    cnt= np.asarray(cnt)


    hull =cv2.convexHull(cnt, False)

    #......................
    # divide and conquer  + tree k-d
    #......................

    #---sort and copy------
    def sort_x():
        return sorted(hull, key=lambda e: e[0][0])

    def sort_y():
        return sorted(hull, key=lambda e: e[0][1])

    def get_medium_x(points):
        points= sort_x(points)
        return int(len(points))

    def distance(p1, p2):
        x=abs(p1[0]-p2[0])
        y=abs(p1[1]-p2[1])
        return math.sqrt(x*x+y*y)

    def closest(points):
        r=points.copy()
        l=len(points)
        d=distance(points[0][0], points[1][0])
        if(l>=3):
            r=points[:2]
            for alfa in range(l):
                d2 = distance(points[alfa][0], points[(alfa+1)%l][0])
                if(d2<d):
                    d=d2
                    r=[points[alfa], points[(alfa+1)%l]]
        return (r, d)

    def divide(points):
        if(len(points)<=3):
            return closest(points)
        l=points[:int(len(points)/2)]
        r=points[int(len(points)/2):]
        l, dl=divide(l)
        r, dr=divide(r)
        if(dl<dr):
            return (l, dl)
        else:
            return (r, dr)

    def fusion(array, pop):
        l=[]
        for e in array:
            if((e[0][0]!=pop[0][0][0] and e[0][1]!=pop[0][0][1])
            and (e[0][0]!=pop[1][0][0] and e[0][1]!=pop[1][0][1])):
                l.append(e)
        l.append([[int((pop[0][0][0]+pop[1][0][0])/2), int((pop[0][0][1]+pop[1][0][1])/2)]])
        return l

    y, x =mask.shape
    xs = sort_x()
    ys = sort_y()
    last_index=len(hull)-1


    ##hay que mejorar esta parte.....muuucho
    a=[0,0,0,0]
    a[0] = xs[0][0][0]+xs[1][0][0]
    a[1] = ys[0][0][1]+ys[1][0][1]
    a[2] = (x-xs[last_index][0][0])+(x-xs[last_index-1][0][0])
    a[3] = (y-ys[last_index][0][1])+(y-ys[last_index-1][0][1])

    min = np.amin(np.asarray(a))
    if a[0]==min:
        corner=[xs[0],xs[1]]
    elif a[1]==min:
        corner=[ys[0],ys[1]]
    elif a[2]==min:
        corner=[xs[last_index], xs[last_index-1]]
    elif a[3]==min:
        corner=[ys[last_index], ys[last_index-1]]

    c=0
    for e in hull:
        if((e[0][0]==corner[0][0][0] and e[0][1]==corner[0][0][1])
        or (e[0][0]==corner[1][0][0] and e[0][1]==corner[1][0][1])):
            hull=np.concatenate((hull[:c], hull[(c+1):]))
        else:
            c=c+1


    #............................................................
    #............................................................


    while len(hull) >= 5:
        points=sort_x()
        p, d =divide(points)
        hull =fusion(points, p)

    hull= np.asarray(points)
    hull= np.concatenate((corner, hull))

    base=distance(hull[0][0], hull[1][0])
    dis=[]
    for alfa in range(7):
        for beta in range(alfa+1, 7):
            if(alfa!=0 or beta != 1):
                dis.append(distance(hull[alfa][0], hull[beta][0])/base)

    #.....................................................
    #Drawing
    #.....................................................
    # create an empty black image
    if(len(sys.argv)>1 and sys.argv[1]=="show"):
        drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)

        draw_contours(drawing, cnt, (0, 255, 0), 1)
        draw_contours(drawing, hull, (255, 0, 0), 5)


    return dis

#.....................................................
#create csv
#.....................................................
# import csv
#
#
# hands="/media/valencia/notPrograms/handAlphabet/asl-alphabet/asl_alphabet_train/"
# b=0
# error=0
# with open('datos.csv', 'w') as csvarchivo:
#     csv_app=csv.writer(csvarchivo)
#     for letra in os.listdir(hands):
#         for imagen in os.listdir(hands+letra):
#             path=hands+letra+"/"+imagen
#             try:
#                 print(0)
#                 row=get_distances(path)
#                 print("1")
#                 row.insert(0, letra)
#
#                 csv_app.writerow(row)
#                 #print(row)
#                 #print(b)
#             except:
#                 error=error+1
#                 print(path)
#                 print("error #", error)
#
# print(b)

get_distances("ok-hand.jpg")
