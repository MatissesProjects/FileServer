from flask import Flask, request, Response, send_from_directory
from utils.db_manager import getDB
from dotenv import load_dotenv
from waitress import serve
from flask_cors import cross_origin
from flask_compress import Compress
import os, secure

load_dotenv()
app = Flask(__name__)
production = eval(os.getenv("PRODUCTION"))
basePath = os.getenv("BASE_PATH")
conn, cursor = getDB()

app.config.update(
    SECRET_KEY = os.urandom(64).hex()
)

Compress(app)
secure_headers = secure.Secure()

def send_file_from_directory(workflow_name, user_id, job_id, file_number, file_extension):
    filename = f'{file_number}.{file_extension}'
    return send_from_directory(f"{basePath}{user_id}/{workflow_name}/{job_id}", filename)

@app.route("/output/createImage/<int:userid>/<int:jobId>/<int:fileNumber>", methods=["GET"])
@cross_origin()
def outputImage(userid, jobId, fileNumber):
    return send_file_from_directory('createImage', userid, jobId, fileNumber, 'png')

@app.route("/output/rethemeImage/<int:userid>/<int:jobId>/<int:fileNumber>", methods=["GET"])
@cross_origin()
def rethemeImage(userid, jobId, fileNumber):
    return send_file_from_directory('rethemeImage', userid, jobId, fileNumber, 'png')

@app.route("/output/<workflowName>/<int:userid>/<int:jobId>/<int:fileNumber>/<fileExtension>", methods=["GET"])
@cross_origin()
def getFile(workflowName, userid, jobId, fileNumber, fileExtension):
    return send_file_from_directory(workflowName, userid, jobId, fileNumber, fileExtension)


# user twitch Id (username?)
@app.post("/createUser")
def createUser():
    try:
        formData = request.form
        if 'discordId' not in formData or 'discordName' not in formData:
            return Response(response='Bad request: discordId and discordName are required', status=400)
        outputs_data = (formData['discordId'], formData['discordName'], 100)
        cursor.execute('INSERT OR IGNORE INTO User (discordId, discordName, tokens) VALUES (?, ?, ?)', outputs_data)
        conn.commit()
        cursor.execute('SELECT tokens FROM User where discordId = ?', (formData['discordId'],))
        return Response(response=f'{cursor.fetchall()}', status=200)
    except Exception as e:
        return Response(response=f'Error: {str(e)}', status=500)

@app.get("/getUser/<userId>")
def getUser(userId):
    try:
        query = '''SELECT  workflowName, u.discordId, j.jobId,
                          substr(o.fileName, 0,instr(o.fileName, '.')) as filename,
                          substr(o.fileName, instr(o.fileName, '.')+1) as extension
                  FROM (SELECT * FROM User WHERE discordId = ?) AS u
                  JOIN Jobs AS j ON u.discordId = j.discordId
                  JOIN Outputs AS o ON j.jobId = o.jobId;'''
        cursor.execute(query, (userId,))
        results = cursor.fetchall()
        base = "https://fileserver.matissetec.dev/output/"
        data = [f"{base}{row[0]}/{row[1]}/{row[2]}/{row[3]}/{row[4]}" for row in results]
        return data
    except Exception as e:
        return Response(response=f'Error: {str(e)}', status=500)

@app.post("/uploadImage")
async def uploadImage():
    try:
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

        # # Commit changes to database
        conn.commit()
        return Response(response=f'success', status=200)
    except Exception as e:
        return Response(response=f'Error: {str(e)}', status=500)

@app.errorhandler(404)
def page_not_found(e):
    return Response(response='404', status=404)

@app.after_request
def add_headers(response):
    secure_headers.framework.flask(response)
    return response

if __name__ == "__main__":
    appKey = 'makeUniqueForOurApp'
    #appKey = os.getenv("APP_KEY")
    if production:
        print('Starting production server on port 5113. At http://127.0.0.1:5113/')
        serve(app, host='127.0.0.1', port=5113)
    else:
        app.config['SERVER_NAME'] = '127.0.0.1:5113'
        app.run(port=5113)