import cv2
print "starting grab"
cap = cv2.VideoCapture('http://localhost:443/stream.mjpg')

ret, frame = cap.read()
print "found frame"
#cv2.imshow('Video', frame)
cv2.imwrite("test.jpg",frame)
print "done"
cap.release()
print "after release"
