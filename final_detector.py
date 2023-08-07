debug = 1
import cv2
import numpy as np
import time
#add
from picamera2 import MappedArray, Picamera2, Preview

normalSize = (640, 480)
lowresSize = (320, 240)

rectangles = []

def DrawRectangles(request):
    with MappedArray(request, "main") as m:
        for rect in rectangles:
            rect_start = (int(rect[0] * 2) - 5, int(rect[1] * 2) - 5)
            rect_end = (int(rect[2] * 2) + 5, int(rect[3] * 2) + 5)
            cv2.rectangle(m.array, rect_start, rect_end, (0, 255, 0, 0))

#end

def convertFrame (frame):
  r = 750.0 / frame.shape[1]
  dim = (750, int(frame.shape[0] * r))
  frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  if useGaussian:
    gray = cv2.GaussianBlur(gray, (gaussianPixels, gaussianPixels), 0)
  return frame, gray



def InferenceTensorFlow(image):
    global rectangles

    labels = None

    # interpreter = tflite.Interpreter(model_path=model, num_threads=4)
    # interpreter.allocate_tensors()

    # input_details = interpreter.get_input_details()
    # output_details = interpreter.get_output_details()
    print(image)
    image
    height = len(image)
    width = len(image[0])
    # height = input_details[0]['shape'][1]
    # width = input_details[0]['shape'][2]
    # floating_model = False
    
    rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    initial_h, initial_w, channels = rgb.shape

    picture = cv2.resize(rgb, (width, height))

    input_data = np.expand_dims(picture, axis=0)
   
    rectangles = []
    # for i in range(int(num_boxes)):
    #     top, left, bottom, right = detected_boxes[0][i]
    #     classId = int(detected_classes[0][i])
    #     score = detected_scores[0][i]
    #     if score > 0.5:
    #         xmin = left * initial_w
    #         ymin = bottom * initial_h
    #         xmax = right * initial_w
    #         ymax = top * initial_h
    #         if labels:
    #             print(labels[classId], 'score = ', score)
    #         else:
    #             print('score = ', score)
    #         box = [xmin, ymin, xmax, ymax]
    #         rectangles.append(box)


def main():
    picam2 = Picamera2()
    picam2.start_preview(Preview.QTGL)
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                                 lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)

    stride = picam2.stream_configuration("lores")["stride"]
    picam2.post_callback = DrawRectangles

    picam2.start()

    while True:
        buffer = picam2.capture_buffer("lores")
        grey = buffer[:stride * lowresSize[1]].reshape((lowresSize[1], stride))
        _ = InferenceTensorFlow(grey)


if __name__ == '__main__':
    main()



