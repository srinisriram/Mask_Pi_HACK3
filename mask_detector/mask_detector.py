#Import necessary packages
from vars import use_email, use_motors, MOTOR1_FORWARD_GPIO, ON, OFF
if use_motors:
	import RPi.GPIO as gpio
	from setup_gpio import setup_gpio
import time
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from detect import detect
from gamma import gamma
from send_email import send_email



if use_motors: 
	setup_gpio()
	print("[INFO]: Setting up GPIO...")


#Load all the models, and start the camera stream
faceModel = cv2.dnn.readNet("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel")
faceModel.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
maskModel = load_model("models/mask_detector.h5")

stream = cv2.VideoCapture(0)

label=""

fail_safe = []

while True:
	#Read frame from the stream
	ret, frame = stream.read()

	cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX)
	frame = gamma(frame, gamma=3)


	#Run the detect function on the frame
	(locations, predictions) = detect(frame, faceModel, maskModel)

	#Go through each face detection.
	for (box, pred) in zip(locations, predictions):
		#Extract the prediction and bounding box coords
		(startX, startY, endX, endY) = box
		(mask, withoutMask) = pred

		#Determine the class label and make actions accordingly
		if mask > withoutMask:
			label = 'Mask'
			fail_safe.append(label)
			color = (0,255,0)
			print("You're good to go!")
			if use_motors:
				print("[INFO]: Opening Door...")
				gpio.output(MOTOR1_FORWARD_GPIO, ON)
				time.sleep(3)
				print("[INFO]: Stopping Motor...")
				gpio.output(MOTOR1_FORWARD_GPIO, OFF)
		else:
			label = 'No Mask'
			fail_safe.append(label)
			color = (0,0,255)
			print("Please wear a mask in order to enter")
			if use_email:
				cv2.imwrite('No_mask.jpg',frame)

                #Place label and Bounding Box
		cv2.putText(frame, label, (startX, startY - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
		cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)


		if len(fail_safe) == 10:
			if 'No Mask' in fail_safe:
				if use_email:
					cv2.imwrite('No_mask.jpg',frame)
					send_email("No_mask.jpg")

			fail_safe.clear()

	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# break from loop if key pressed is q
	if key == ord("q"):
		break

#Cleanup
stream.release()
cv2.destroyAllWindows()
