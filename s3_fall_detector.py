import os
import cv2 as cv
import time
from datetime import datetime
import statistics as st

class FallDetector:
    def __init__(self, func = 0, scale = 1):
        """FallDetector(func = 0(default) or path of video source, scale = 1 or resolution scale)"""

        self.scale = scale            
        #background subtraction model
        self.backSub = cv.createBackgroundSubtractorMOG2()
        
        #collect movement history data 
        self.largestContour = []    
        self.height = []
        self.width = []
        self.xPoint = []    
        self.yPoint = []
        self.xlPoint = []
        self.ylPoint = []
        self.xcenter =[]
        self.ycenter = []
        self.status = "Starting..."

        #time parameter 
        self.counter = 0
        self.start = time.time()

        #Flags
        self.toBeChecked = False
        self.isFall = False
        self.stationary = False
        self.alertMsgFlag = False
        self.OutofFrame = False
        


        # self.capture = cv.VideoCapture("http://203.252.161.105:8000/stream.mjpg")
        # self.capture = cv.VideoCapture("http://localhost:8000/stream.mjpg")
        self.capture = cv.VideoCapture("/home/woo4826/Desktop/proj_makers/output.mp4")

    
    def rescaleFrame(self): 

        """Reduce resolution of the source to increase the processing speed
        (for img,video & live video)"""

        width = int(self.frame.shape[1] * self.scale)
        height = int(self.frame.shape[0] * self.scale)
        dimensions = (width,height)
        self.frame = cv.resize(self.frame, dimensions, interpolation= cv.INTER_AREA)

    def __analyzePosition(self):

        """Get position of the moving object by bounding it with a rectangle"""

        x,y,w,h = cv.boundingRect(self.largestContour)
        parameter = [self.width, self.height, self.xPoint, self.yPoint,self.xlPoint,self.ylPoint, self.xcenter,self.ycenter]
        p = [w,h,x,y,int(x+w),int(y+h),int(x+(w/2)),int(y+(h/2))]
        
        for i,j in zip(parameter,p):
            i.append(j)
        
        if st.mean(self.width) > st.mean(self.height): #check horizontal position
            self.toBeChecked = True
        
        if len(self.width) > 10:
            for i in parameter:
                i.pop(0)

    def __checkStationary(self):

        """Check the standard deviation of 10 consecutives coordinates
        the person is stationary if the standard deviation is very small"""

        parameter = [self.xcenter, self.ycenter]
        stddevVal = [st.pstdev(i) for i in parameter]
        #cv.putText(self.frame, 'xPointSD: '+str(stddevVal[0]), (10,35), cv.FONT_ITALIC, 0.5, (255,255,255),2,8)    #to observe changes in coordinates
        #cv.putText(self.frame, 'yPointSD: '+str(stddevVal[1]), (10,50), cv.FONT_ITALIC, 0.5, (255,255,255),2,8)
        
        if stddevVal[0] < 2 and stddevVal[1] < 2:   #standard deviation threshold can be varied
            self.stationary  = True
    
    def __checkOutofFrame(self):

        """When the detected person walk out of frame (left and right), 
        defined there was no one in the scene"""

        fw = self.frame.shape[1]            #frame width
        meanLX = st.mean(self.xlPoint)      #left boundary
        meanUX = st.mean(self.xPoint)       #right boundary

        if meanUX == 0 or meanLX == fw:     #if L/R box boundaries touches frame boundaries
            self.OutofFrame = True
        else:
            self.OutofFrame = False
            
    def __checkAction(self):

        """Check Position/Action"""

        #getting the current position parameters
        x = self.xPoint[-1]
        y = self.yPoint[-1]
        rw = self.width[-1]
        rh = self.height[-1]
        fw = self.frame.shape[1]
        fh = self.frame.shape[0]
        rectArea = rw*rh
        frameArea = fw*fh
        #colors code
        green = (0,255,0)
        red = (0,0,255)
        orange = (0,140,255)
        
        if rectArea < 0.7*frameArea: # avoid detected moving object too close to camera
            self.__checkStationary()
            
            #Action checker
            if self.toBeChecked and not self.stationary:
                self.status = "Warning!"
                #fall detected
                color = orange
                    
            elif not self.toBeChecked and self.stationary:
                self.__checkOutofFrame()
                self.status = 'Standing'
                color = green
                
            elif not self.toBeChecked and not self.stationary:
                self.__checkOutofFrame()
                self.status = "Moving"
                color = green
                if self.alertMsgFlag:
                    self.alertMsgFlag = False
                
            elif self.toBeChecked and self.stationary:
                self.isFall = True
                self.counter += 1
                color = red
                self.status = 'FALL!'
                if self.counter == 5:
                    self.__sendAlert()
                    self.counter = 0
            
            if not self.OutofFrame:
                cv.rectangle(self.frame, (x,y), (x+rw,y+rh), color,2)
                cv.circle(self.frame, (self.xcenter[-1],self.ycenter[-1]),2,red,2)
                cv.putText(self.frame, "status: {}".format(self.status), (x, y+15), cv.FONT_ITALIC, 0.5, color, 1)
    
            else: 
                self.status = "No people is in the detection area"
                cv.putText(self.frame, "status: {}".format(self.status), (10, 20), cv.FONT_ITALIC, 0.5, (255,255,255), 1)

    def __sendAlert(self):

        """Send alert messages, save screenshot of the scene when fall detected"""

        if self.alertMsgFlag == False: 
            print('Fall is detected')
            #dt = self.datetime.strftime("%d%m%Y%H%M%S")
            dt = "11082023174922"
            name = dt +'.jpg'
            p = os.path.sep.join(['shots', "Fallshot_{}.png".format(str(dt))])
            cv.imwrite(p,self.frame)
            print(name + ' saved in '+ str(p))
            
            self.alertMsgFlag = True
            self.isFall = False
            self.toBeChecked = False
            url = "http://localhost:3000/fall-detection"  # API 엔드포인트 주소
            payload = {
                "deviceId": "your_device_id",
                "imageCapture": True
            }
            
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Fall detection check completed.")
            else:
                print("Error:", response.text)
            
    def __getDateTime(self):

        """Get date and time"""

        now = datetime.now()
        self.datetime = now.strftime("%Y/%m/%d %H:%M:%S")


    def getFrame(self, history = 20, NMixtures = 10, detectShadows = False, learningRate = 0.01):
        
        """
        Start fall detector.
        Get frame from FallDetector.
        Analyse moving object appear and its position.
        """

        if not self.capture.isOpened():
            print("Error opening video file or stream")
    
        if self.capture.isOpened():
            isTrue, self.frame = self.capture.read()
            self.toBeChecked = False
            self.isFall = False
            self.stationary = False
            if isTrue == True and  self.frame is not None:
                #self.__rescaleFrame()
                #self.__getDateTime()
                self.backSub.setHistory(history)
                self.backSub.setNMixtures(NMixtures)
                self.backSub.setDetectShadows(detectShadows)
                self.fgmask = self.backSub.apply(self.frame,learningRate = learningRate)
                self.backgroundImg = self.backSub.getBackgroundImage()
                
                contours, _ = cv.findContours(self.fgmask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE, offset=(0,0))
                
                maxArea = 0
                
                for i,contour in enumerate(contours):
                    area = cv.contourArea(contours[i])
                    if (area > maxArea and area > 600):
                        maxArea = area
                        self.largestContour = contours[i]
                        
                if len(self.largestContour) > 0:
                    self.__analyzePosition()
                    self.__checkAction()
                
                else:
                    self.status = "No people is in the detection area"

    def showFrame(self):
        "Display frame"
        
        w = self.frame.shape[1]
        end = time.time()
        seconds = end - self.start
        fps  = round((1 / seconds), 1)
        self.start = time.time()

        cv.putText(self.frame, "FPS: {}".format(fps), (int(w/2), 20), cv.FONT_ITALIC, 0.5, (255, 255, 255), 1)
        cv.putText(self.frame, "status: {}".format(self.status), (10, 20), cv.FONT_ITALIC, 0.5, (255,255,255), 1)
        #cv.putText(self.frame, self.datetime, (self.frame.shape[1]-160, 20), cv.FONT_HERSHEY_DUPLEX, 0.4, (0, 0, 0), 1)
        cv.imshow('Streaming',self.frame)

    def showFGMask(self):
        "Display FG mask"

        cv.imshow('FG mask', self.fgmask)

    def showBackground(self):
        "Display Background Img"

        cv.imshow('Background', self.backgroundImg)
        
        
        
if __name__ == "__main__":

    fd = FallDetector()
    time.sleep(1) #to initialize camera for autofocus ad start up (optional)
    
    while True:
        fd.getFrame()
        fd.showFrame()

        if cv.waitKey(20) & 0xFF==ord('d'):
            break
        
    fd.capture.release()
    cv.destroyAllWindows()
    
    
