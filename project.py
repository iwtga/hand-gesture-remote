'''
  _____ ____  ____   ___  ____    ____   ___   ___  
 | ____|  _ \|  _ \ / _ \|  _ \  | ___| / _ \ / _ \ 
 |  _| | |_) | |_) | | | | |_) | |___ \| | | | (_) |IRFAN
 | |___|  _ <|  _ <| |_| |  _ <   ___) | |_| |\__, |ALAN
 |_____|_| \_\_| \_\\___/|_| \_\ |____/ \___/   /_/ LANCE
 '''

# TODO list
# Importing Libraries and Capturing the video from webcam - Done
# Adding Trackbar to change hsv values - Done
#Step - 2  -Convert frames Into hsv
#Step - 3  -Track hand on color basis 
#Step - 4  -Create mask on the basis of color and filter actual color 
#Step - 5  -Invert pixel value and then enchance the result for better output
#Step - 6  -Find Contours for specific colored object
#Step - 7  -Find Max area contour and draw it on live feed
#Step - 8  -Find Convexity detect  for counting Values and Apply Cosin method
#Step - 9  -Bind hand gestures with keyboard keys.
#Step -10  -Enjoy your output

# Importing Necessary Libraries
import cv2
import numpy as np 
import math
import pyautogui as p

# Creating the capture instance for taking frames from webcam
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

# nothing function will be called continuously when the trackerbar is not used
def nothing(x):
    pass

# Giving window-name for the trackbar
cv2.namedWindow("Color Adjustments",cv2.WINDOW_NORMAL)

# Resizing the size of trackbar window
cv2.resizeWindow("Color Adjustments", (300, 300))

# Creating threshold trackbar for number of 
cv2.createTrackbar("Thresh", "Color Adjustments", 0, 255, nothing)

# Adding Trackbars for color detection
cv2.createTrackbar("Lower_H", "Color Adjustments", 0, 255, nothing)
cv2.createTrackbar("Lower_S", "Color Adjustments", 0, 255, nothing)
cv2.createTrackbar("Lower_V", "Color Adjustments", 0, 255, nothing)
cv2.createTrackbar("Upper_H", "Color Adjustments", 255, 255, nothing)
cv2.createTrackbar("Upper_S", "Color Adjustments", 255, 255, nothing)
cv2.createTrackbar("Upper_V", "Color Adjustments", 255, 255, nothing)

# This loop will run continuously until the user doesn't press the escape key
while True:
    iscamworking, frame = cap.read()        # Reads frame from webcam
    frame = cv2.flip(frame,2)               # Flip the frame along y axis
    frame = cv2.resize(frame,(600,500))     # To resize the fraze
    # Creating a sub window for hand, the border will be blue
    cv2.rectangle(frame, (0,1), (300,500),(0, 255, 0), 0)
    cropped_image = frame[1:500, 0:300]     # Creating a cropped image of hand
    
    #Step -2
    hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    #detecting hand
    l_h = cv2.getTrackbarPos("Lower_H", "Color Adjustments")
    l_s = cv2.getTrackbarPos("Lower_S", "Color Adjustments")
    l_v = cv2.getTrackbarPos("Lower_V", "Color Adjustments")

    u_h = cv2.getTrackbarPos("Upper_H", "Color Adjustments")
    u_s = cv2.getTrackbarPos("Upper_S", "Color Adjustments")
    u_v = cv2.getTrackbarPos("Upper_V", "Color Adjustments")
    #Step -3
    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])
    
    #Step - 4
    #Creating Mask
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    #filter mask with image
    filtr = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
    
    #Step - 5
    mask1  = cv2.bitwise_not(mask)
    m_g = cv2.getTrackbarPos("Thresh", "Color Adjustments") #getting track bar value
    ret,thresh = cv2.threshold(mask1,m_g,255,cv2.THRESH_BINARY)
    dilata = cv2.dilate(thresh,(3,3),iterations = 6)
    
    #Step -6
    #findcontour(img,contour_retrival_mode,method)
    cnts,hier = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    
    try:
        #print("try")
         #Step -7
         # Find contour with maximum area
        cm = max(cnts, key=lambda x: cv2.contourArea(x))
        #print("C==",cnts)
        epsilon = 0.0005*cv2.arcLength(cm,True)
        data= cv2.approxPolyDP(cm,epsilon,True)
    
        hull = cv2.convexHull(cm)
        
        cv2.drawContours(cropped_image, [cm], -1, (50, 50, 150), 2)
        cv2.drawContours(cropped_image, [hull], -1, (0, 255, 0), 2)
        
        #Step - 8
        # Find convexity defects
        hull = cv2.convexHull(cm, returnPoints=False)
        defects = cv2.convexityDefects(cm, hull)
        count_defects = 0
        #print("Area==",cv2.contourArea(hull) - cv2.contourArea(cm))
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
           
            start = tuple(cm[s][0])
            end = tuple(cm[e][0])
            far = tuple(cm[f][0])
            #Cosin Rule
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14
            #print(angle)
            # if angle <= 50 draw a circle at the far point
            if angle <= 50:
                count_defects += 1
                cv2.circle(cropped_image,far,5,[255,255,255],-1)
        
        print("count==",count_defects)
        
        #Step - 9 
        # Print number of fingers
        if count_defects == 0:
            
            cv2.putText(frame, " ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255),2)
        elif count_defects == 1:
            
            p.press("space")
            cv2.putText(frame, "Play/Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
        elif count_defects == 2:
            p.press("up")
            
            cv2.putText(frame, "Volume UP", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
        elif count_defects == 3:
            p.press("down")
            
            cv2.putText(frame, "Volume Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
        elif count_defects == 4:
            p.press("right")
            
            cv2.putText(frame, "Forward", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
        else:
            pass
           
    except:
        pass
    #step -10    
    cv2.imshow("Thresh", thresh)
    #cv2.imshow("mask==",mask)
    cv2.imshow("filter==",filtr)
    cv2.imshow("Result", frame)

    key = cv2.waitKey(25) &0xFF    
    if key == 27: 
        break
cap.release()
cv2.destroyAllWindows()
    
    
  