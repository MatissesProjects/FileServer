import sqlite3
from flask import Flask, request, Response, send_from_directory
import os

app = Flask(__name__)

basePath="/home/matisse/outputfiles/"
conn = sqlite3.connect('userFileData.db', check_same_thread=False)
cursor = conn.cursor()
# @app.get("/output/<str:workflow>/<int:fileNumber>/<str:extension>")
# async def outputFile(workflow, fileNumber, extension):
#     filename = f'{fileNumber}.{extension}' # need a way to know the file type
#     return send_from_directory(basePath + f"{workflow}/", filename)

@app.get("/output/createImage/<int:fileNumber>")
async def outputImage(fileNumber):
    filename = f'{fileNumber}.png'
    return send_from_directory(basePath + "images/", filename)

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

    print("success")
    filePath = f'{basePath}{formData["discordId"]}/{formData["workflowName"]}/{file.filename}'
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
    conn.close()
    return Response(response=f'success', status=200)

app.run("127.0.0.1", "5113")

appKey = "makeUniqueForOurApp"