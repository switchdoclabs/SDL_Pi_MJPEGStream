# mjpeg streaming in pure Python

# SwitchDoc Labs 2019
# open source license

This software gives an example of how to stream MJPEG video on the Raspberry Pi using the PiCamera library using overlays.  This is the same software that is being used in the SwitchDoc Labs SkyWeather product in conjunction with WeatherSTEM.

We are publishing this because we could not find anything on the web to do what we needed to do (Python streaming in thread on SkyWeather - single picture capability - abiltiy to add overlays and information on the fly)


SkyWeather:

https://shop.switchdoc.com/products/skyweather-raspberry-pi-based-weather-station-kit-for-the-cloud

WeatherSTEM:

https://www.weatherstem.com/dashboard-sales


Requires a Rapsberry Pi 3B+ or greater.

#Contents

streamtest.py

Python program to stream video using the PiCamera library.  Each frame is intercepted and various overlays and information is placed on the frame then sent to the stream.

Defaults to streaming on:

http://localhost:443/

cvgrab.py

Grabs a single frame from the MJPEG video stream using openCV.  Writes to a file "test.jpg"




