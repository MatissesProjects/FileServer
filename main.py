import sqlite3
from flask import Flask, request, Response, send_from_directory
app = Flask(__name__)

basePath="/home/matisse/outputfiles/"
conn = sqlite3.connect('userFileData.db')
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
    print(request.form)
    # request.form in the form data check the api key
    print(files)
    if 'imageFile' not in files:
        return Response(response='failed to get image', status=501)
    
    file = files['imageFile']
    if file.filename == '':
        print("no image file")
        return Response(response=f'need to supply a file name', status=502)

    print("success")
    filePath = f'{basePath}images/{file.filename}'
    print(f"saving to {filePath}")
    file.save(filePath)

    # TODO add to database that we have our new file for the user
    # # Insert data into User table
    # users_data = [('123456789', 'UserOne', 100), ('987654321', 'UserTwo', 150)]
    # cursor.executemany('INSERT INTO User (discordId, discordName, tokens) VALUES (?, ?, ?)', users_data)

    # # Insert data into Jobs table
    # jobs_data = [('WorkflowA', 1, '123456789'), ('WorkflowB', 2, '987654321'), ('WorkflowC', 3, '123456789')]
    # cursor.executemany('INSERT INTO Jobs (workflowName, jobId, discordID) VALUES (?, ?, ?)', jobs_data)

    # # Insert data into Outputs table
    # outputs_data = [(1, '6878808662.png'), (2, '7392628832.png'), (2, '8071648859.png'), (2, '6029311345.png')]
    # cursor.executemany('INSERT INTO Outputs (jobId, fileName) VALUES (?, ?)', outputs_data)

    # # Commit changes and close the connection
    # conn.commit()
    # conn.close()
    return Response(response=f'success', status=200)

app.run("127.0.0.1", "5113")

appKey = "makeUniqueForOurApp"