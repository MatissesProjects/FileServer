from flask import Flask
import flask 
app = Flask(__name__)

basePath="~/outputfiles/"

@app.get("/output/createImage/<int:fileNumber>")
async def outputImage(fileNumber):
    filename = f'{fileNumber}.png'
    return flask.send_from_directory(basePath + "images/", filename)

app.run("127.0.0.1", "5113")