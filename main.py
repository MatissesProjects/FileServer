import sqlite3
from flask import Flask, request, Response, send_from_directory, jsonify
from flask_cors import cross_origin
import os
import json

app = Flask(__name__)

basePath="/home/matisse/outputfiles/"
conn = sqlite3.connect('userFileData.db', check_same_thread=False)
cursor = conn.cursor()

@app.route("/output/createImage/<int:userid>/<int:jobId>/<int:fileNumber>", methods=["GET"])
@cross_origin()
def outputImage(userid,jobId,fileNumber):
    filename = f'{fileNumber}.png'
    return send_from_directory(f"{basePath}{userid}/createImage/{jobId}", filename)

@app.route("/output/rethemeImage/<int:userid>/<int:jobId>/<int:fileNumber>", methods=["GET"])
@cross_origin()
def rethemeImage(userid,jobId,fileNumber):
    filename = f'{fileNumber}.png'
    return send_from_directory(f"{basePath}{userid}/rethemeImage/{jobId}", filename)

@app.route("/output/<workflowName>/<int:userid>/<int:jobId>/<int:fileNumber>/<fileExtension>", methods=["GET"])
@cross_origin()
def getFile(workflowName,userid,jobId,fileNumber,fileExtension):
    filename = f'{fileNumber}.{fileExtension}'
    return send_from_directory(f"{basePath}{userid}/{workflowName}/{jobId}", filename)

# user twitch Id (username?)
@app.post("/createUser")
def createUser():
    formData = request.form
    outputs_data = (formData['discordId'], formData['discordName'], 100)
    cursor.execute('INSERT OR IGNORE INTO User (discordId, discordName, tokens) VALUES (?, ?, ?)', outputs_data)
    conn.commit()
    cursor.execute('SELECT tokens FROM User where discordId = ?', (formData['discordId'],))
    return Response(response=f'{cursor.fetchall()}', status=200)

@app.get("/getUser/<userId>")
def getUser(userId):
    cursor.execute('''SELECT  workflowName, u.discordId, j.jobId,
                              substr(o.fileName, 0,instr(o.fileName, '.')) as filename,
                              substr(o.fileName, instr(o.fileName, '.')+1) as extension
                      FROM (SELECT * FROM User WHERE discordId = ?) AS u
                      JOIN Jobs AS j ON u.discordId = j.discordId
                      JOIN Outputs AS o ON j.jobId = o.jobId;''', (userId,))
    # Fetch all results
    results = cursor.fetchall()
    # Print the results
    base = "https://fileserver.matissetec.dev/output/"
    data = []
    for row in results:
        data.append(f"{base}{row[0]}/{row[1]}/{row[2]}/{row[3]}/{row[4]}")
    return Response(response={'data':data}, status=200)

@app.post("/uploadImage")
async def uploadImage():
    files = request.files
    formData = request.form
    # request.form in the form data check the api key
    print(files)
    if 'imageFile' not in files:
        return Response(response='failed to get image', status=501)
    
    file = files['imageFile']
    if file.filename == '':
        print("no image file")
        return Response(response=f'need to supply a file name', status=502)

    filePath = f'{basePath}{formData["discordId"]}/{formData["workflowName"]}/{formData["jobId"]}/{file.filename}'
    print(filePath, "using the file path")
    directory = os.path.dirname(filePath)

    # Create the directory if it doesn't exist (do nothing if it exists)
    os.makedirs(directory, exist_ok=True)
    print(f"saving to {filePath}")
    file.save(filePath)

    # TODO add to database that we have our new file for the user
    # # Insert data into Jobs table
    jobs_data = (formData['workflowName'], formData['jobId'], formData['discordId'])
    cursor.execute('INSERT INTO Jobs (workflowName, jobId, discordID) VALUES (?, ?, ?)', jobs_data)

    # # Insert data into Outputs table
    outputs_data = (formData['jobId'], file.filename)
    cursor.execute('INSERT INTO Outputs (jobId, fileName) VALUES (?, ?)', outputs_data)

    # # Commit changes and close the connection
    conn.commit()
    return Response(response=f'success', status=200)

app.run("127.0.0.1", "5113")

appKey = "makeUniqueForOurApp"