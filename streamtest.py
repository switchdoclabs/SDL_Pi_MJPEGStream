import io
import picamera
import logging
import SocketServer
from threading import Condition
from PIL import ImageFont, ImageDraw, Image
import cv2
import traceback
import StringIO

import numpy as np

import datetime as dt

#import SimpleHTTPServer

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

PAGE="""\
<html>
<head>
<title>SkyWeather MJPEG streaming demo</title>
</head>
<body>
<h1>SkyWeather MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="1296" height="730" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                        # now add timestamp to jpeg
                        # Convert to PIL Image
                        cv2.CV_LOAD_IMAGE_COLOR = 1 # set flag to 1 to give colour image
                        npframe = np.fromstring(frame, dtype=np.uint8)
                        pil_frame = cv2.imdecode(npframe,cv2.CV_LOAD_IMAGE_COLOR)
                        #pil_frame = cv2.imdecode(frame,-1)
                        cv2_im_rgb = cv2.cvtColor(pil_frame, cv2.COLOR_BGR2RGB)
                        pil_im = Image.fromarray(cv2_im_rgb)

                        draw = ImageDraw.Draw(pil_im)

                        # Choose a font
                        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 25)
                        myText = "SkyWeather "+dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        # Draw the text
                        color = 'rgb(255,255,255)'
                        #draw.text((0, 0), myText,fill = color, font=font)

                        # get text size
                        text_size = font.getsize(myText)

                        # set button size + 10px margins
                        button_size = (text_size[0]+20, text_size[1]+10)

                        # create image with correct size and black background
                        button_img = Image.new('RGBA', button_size, "black")
                        
                        #button_img.putalpha(128)
                        # put text on button with 10px margins
                        button_draw = ImageDraw.Draw(button_img)
                        button_draw.text((10, 5), myText, fill = color, font=font)

                        # put button on source image in position (0, 0)

                        pil_im.paste(button_img, (0, 0))
                        bg_w, bg_h = pil_im.size 
                        # WeatherSTEM logo in lower left
                        size = 64
                        WSLimg = Image.open("WeatherSTEMLogoSkyBackground.png")
                        WSLimg.thumbnail((size,size),Image.ANTIALIAS)
                        pil_im.paste(WSLimg, (0, bg_h-size))

                        # SkyWeather log in lower right
                        SWLimg = Image.open("SkyWeatherLogoSymbol.png")
                        SWLimg.thumbnail((size,size),Image.ANTIALIAS)
                        pil_im.paste(SWLimg, (bg_w-size, bg_h-size))

                        # Save the image
                        buf= StringIO.StringIO()
                        pil_im.save(buf, format= 'JPEG')
                        frame = buf.getvalue()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                traceback.print_exc()
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(SocketServer.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
#with picamera.PiCamera(resolution='1920x1080', framerate=24) as camera:
with picamera.PiCamera(resolution='1296x730', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    camera.annotate_foreground = picamera.Color(y=0.2,u=0, v=0)
    camera.annotate_background = picamera.Color(y=0.8, u=0, v=0)
    try:
        address = ('', 443)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
