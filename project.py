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
# Converting frame to HSV - Done
# Tracking hand on the basis of color provided by the user - Done
# Creating a mask to filter the values given by user and filter the frame - Done
# Inverting the pixel value for better enhanced results - Done
# Find Contours - Done
# Drawing the contour with max contour - Done
#Step - 8  -Find Convexity detect  for counting Values and Apply Cosin method
#Step - 9  -Bind hand gestures with keyboard keys.
#Step -10  -Enjoy your output

# Importing Necessary Libraries
import cv2
import pyautogui as p
import numpy as np 
import math

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
    

    hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)    # Creating hsv of cropped image


    # Hand Detection values; it will take values from tracj
    l_hue = cv2.getTrackbarPos("Lower_H", "Color Adjustments")  # lower hue
    l_sat = cv2.getTrackbarPos("Lower_S", "Color Adjustments")  # lower saturation
    l_val = cv2.getTrackbarPos("Lower_V", "Color Adjustments")  # lower brightness

    u_hue = cv2.getTrackbarPos("Upper_H", "Color Adjustments")  # higher hue
    u_sat = cv2.getTrackbarPos("Upper_S", "Color Adjustments")  # high saturation
    u_val = cv2.getTrackbarPos("Upper_V", "Color Adjustments")  # higher brightness

    # Putting the values obtained from trackbar into arrays
    lower_bound = np.array([l_hue, l_sat, l_val])   # Lower Bound Values
    upper_bound = np.array([u_hue, u_sat, u_val])   # Upper Bound Values
    

    # Creating a mask to filter the values given by user and filter the frame
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Filtering the original image with mask
    filtr = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
    
    #Step - 5
    mask1  = cv2.bitwise_not(mask)      # performing bitwise not to invert black and white
    m_g = cv2.getTrackbarPos("Thresh", "Color Adjustments")     # Getting threshold value from trackbar
    ret,thresh = cv2.threshold(mask1,m_g,255,cv2.THRESH_BINARY) # adding the threshold values into bitmap
    dilated = cv2.dilate(thresh,(3,3),iterations = 6)       # Dialating the frame
    
    # Finding contours
    cnts,hier = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)  # finding cnt, and heirarchy
    
    try:
        # Find contour that has the maximum area
        cm = max(cnts, key=lambda x: cv2.contourArea(x))    # Finding contour with max area
        epsilon = 0.0005*cv2.arcLength(cm,True)
        data= cv2.approxPolyDP(cm,epsilon,True)
    
        hull = cv2.convexHull(cm)       # hull is the red border around the hand this is optional
        
        cv2.drawContours(cropped_image, [cm], -1, (50, 50, 150), 2) # drawing the max contour
        cv2.drawContours(cropped_image, [hull], -1, (0, 255, 0), 2) # this is optional just to see how camera catches the hand
        
        #Step - 8
        # Find convexity defects
        hull = cv2.convexHull(cm, returnPoints=False) # creating a hull
        defects = cv2.convexityDefects(cm, hull)    # finds the conexity defects in a hull
        count_defects = 0           # count convexity defects
        #print("Area==",cv2.contourArea(hull) - cv2.contourArea(cm))
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]      #start, end, far
           
            start = tuple(cm[s][0])
            end = tuple(cm[e][0])
            far = tuple(cm[f][0])
            # Performing cosine rule to find the angle
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14

            #check if it is a valid defect
            if angle <= 50:
                count_defects += 1
                cv2.circle(cropped_image,far,5,[255,255,255],-1)
        
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
    #cv2.imshow("filter==",filtr)
    cv2.imshow("Result", frame)

    key = cv2.waitKey(25) &0xFF    
    if key == 27: 
        break
cap.release()
cv2.destroyAllWindows()
    
    
  