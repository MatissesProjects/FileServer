from flask import Flask
import flask
from os import listdir
app = Flask(__name__)

basePath="/home/matisse/outputfiles/"

@app.get("/")
async def getFiles():
    return listdir(basePath+ "images/")

@app.get("/output/createImage/<int:fileNumber>")
async def outputImage(fileNumber):
    filename = f'{fileNumber}.png'
    return flask.send_from_directory(basePath + "images/", filename)

app.run("127.0.0.1", "5113")