import sqlite3
from flask import Flask, request, Response, send_from_directory, jsonify
from flask_cors import cross_origin
import os
import json

app = Flask(__name__)

basePath="/home/matisse/outputfiles/"
conn = sqlite3.connect('userFileData.db', check_same_thread=False)
cursor = conn.cursor()

def print_query(sql):
    print(sql)

conn.set_trace_callback(print_query)

@app.route("/output/<workflowName>/<int:userid>/<int:jobId>/<fileName>/<fileExtension>", methods=["GET"])
@cross_origin()
def getFile(workflowName,userid,jobId,fileName,fileExtension):
    filename = f'{fileName}.{fileExtension}'
    return send_from_directory(f"{basePath}{userid}/{workflowName}/{jobId}", filename)

@app.route("/output/<workflowName>/<int:userid>/<int:jobId>", methods=["GET"])
@cross_origin()
def getText(workflowName,userid,jobId):
    return Response(response=cursor.execute('SELECT fileName from Outputs where jobId = ?', (jobId,)).fetchall()[0][0], status=200)


# user twitch Id (username?)
@app.post("/createUser")
def createUser():
    formData = request.form
    outputs_data = (formData['discordId'], formData['discordName'], 100)
    cursor.execute('INSERT OR IGNORE INTO User (discordId, discordName, tokens) VALUES (?, ?, ?)', outputs_data)
    print(outputs_data)
    conn.commit()
    cursor.execute('SELECT tokens FROM User where discordId = ?', (formData['discordId'],))
    return Response(response=f'{cursor.fetchall()[0][0]}', status=200)

@app.post("/tokens")
def tokens():
    formData = request.json
    data = (int(formData['discordId']),)
    print(data)
    cursor.execute('SELECT tokens FROM User where discordId = ?', data)
    return Response(response=f'{cursor.fetchall()[0][0]}', status=200)


'''
@app.post("/setUserTokens")
def setUserTokens():
    formData = request.form
    cursor.execute('update user set tokens = ? where discordId = ?', (formData['tokensLeft'], formData['discordId'],))
    conn.commit()
    return Response(response=f'updated', status=200)
'''

@app.get("/removeImage/<discordId>/<jobId>")
def removeImage(discordId, jobId):
    print(jobId)
    cursor.execute('SELECT discordID, workflowName, j.jobId, fileName FROM Outputs as o JOIN Jobs as j on o.jobId = j.jobId WHERE j.jobId = ?',(jobId,))
    results = cursor.fetchall()
    for row in results:
        os.remove(f"{basePath}{row[0]}/{row[1]}/{row[2]}/{row[3].split('.')[0]}.{row[3].split('.')[1]}")
    cursor.execute(f"DELETE from outputs where jobId = '{int(jobId)}'", ())
    conn.commit()
    cursor.execute(f"DELETE FROM PublicFeed WHERE jobId = '{int(jobId)}'", ())
    conn.commit()
    return Response(response="removed", status=200)

@app.get("/unpublishItem/<discordId>/<jobId>")
def unpublishImage(discordId, jobId):
    cursor.execute('DELETE FROM PublicFeed WHERE discordId = ? AND jobId = ?', (discordId, jobId,))
    conn.commit()
    return Response(response="removed", status=200)

@app.post("/addUserTokens")
def addUserTokens():
    formData = request.json
    id = formData['discordId']
    cursor.execute("update user set tokens = (select tokens from User where discordId = ?) + ? where discordId = ?", (id, float(formData['newTokens']), id,))
    conn.commit()
    return Response(response='updated', status=200)

# workflows is a comma separated list
@app.get("/getUserResults/<userId>")
def getUserImages(userId):
    print("in user images")
    #queryParams = '"createImage","similarImages"'
    queryParams = request.args.get('filter')
    workflows = queryParams.replace('"','').replace(',', "','")
    #[print(request.args.keys(d)) for d in request.args.keys()]

    workflowQuery = f'''SELECT DISTINCT workflowName, u.discordId, j.jobId,
                              substr(o.fileName, 0,instr(o.fileName, '.')) as filename,
                              substr(o.fileName, instr(o.fileName, '.')+1) as extension
                     FROM (SELECT * FROM User WHERE discordId = ?) AS u
                     JOIN Jobs AS j ON u.discordId = j.discordId
                     JOIN Outputs AS o ON j.jobId = o.jobId
                     WHERE workflowName in ('{workflows}')
                         AND filename not like '%space%';'''
    cursor.execute(workflowQuery, (userId,)) #, queryParams.replace('"','').replace(',', "','")))

    # Fetch all results
    results = cursor.fetchall()
    # Print the results
    base = "https://fileserver.matissetec.dev/output/"
    data = []
    for row in results:
        data.append(f"{base}{row[0]}/{row[1]}/{row[2]}/{row[3]}/{row[4]}")
    print(data)

    return data[::-1]

@app.get("/getPublicResults")
def getPublicResults():
    print("get public results")
    queryParams = request.args.get('filter')
    workflows = queryParams.replace('"','').replace(',', "','")
    workflowQuery = f'''SELECT DISTINCT workflowName, discordId, jobId,
                               substr(fileName, 0, instr(fileName, '.')) as filename,
                               substr(fileName, instr(fileName, '.') + 1) as extension
                        FROM PublicFeed
                        WHERE workflowName in ('{workflows}')
                        ORDER BY rowid DESC'''
    cursor.execute(workflowQuery) #, queryParams.replace('"','').replace(',', "','")))

    # Fetch all results
    results = cursor.fetchall()
    # Print the results
    base = "https://fileserver.matissetec.dev/output/"
    data = []
    for row in results:
        data.append(f"{base}{row[0]}/{row[1]}/{row[2]}/{row[3]}/{row[4]}")
    print(data)

    return data #[::-1]

@app.post("/myPublicResults")
def myPublicResults():
    # TODO security update to using discordToken to derive id
    discordId = request.json['discordId']
    cursor.execute('SELECT * FROM PublicFeed WHERE discordId = ? ORDER BY rowid DESC;', (discordId,))
    results = cursor.fetchall()
    # Print the results
    base = "https://fileserver.matissetec.dev/output/"
    data = []
    for row in results:
        data.append(f"{base}{row[3]}/{row[2]}/{row[0]}/{row[1].split('.')[0]}/{row[1].split('.')[1]}")
    print(data)

    return data

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

@app.post("/uploadText")
async def uploadText():
    data = request.json
    print(f"saving text: {data['text']}")

    jobs_data = (data['workflowName'], data['jobId'], data['discordId'])
    print(jobs_data)
    cursor.execute('INSERT INTO Jobs (workflowName, jobId, discordID) VALUES (?, ?, ?)', jobs_data)

    # # Insert data into Outputs table
    outputs_data = (data['jobId'], data['text'])
    cursor.execute('INSERT INTO Outputs (jobId, fileName) VALUES (?, ?)', outputs_data)

    # # Commit changes and close the connection
    conn.commit()
    return Response(response=f'success', status=200)

@app.post("/setItemPublic")
async def setItemPublic():
    data = request.json
    print(f"setting item: {data} to public")
    publicData = (data['jobId'], data['fileName'], data['discordId'], data['workflowName'])
    print(publicData)
    cursor.execute('INSERT INTO PublicFeed (jobId, fileName, discordId, workflowName) VALUES (?, ?, ?, ?)', publicData)
    conn.commit()
    return Response(response='success', status=200)


app.run("127.0.0.1", "5113", debug=True, passthrough_errors=True, use_debugger=False, use_reloader=False)
