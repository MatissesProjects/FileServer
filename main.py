from flask import Flask, request, Response, send_from_directory
app = Flask(__name__)

basePath="/home/matisse/outputfiles/"


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
    return Response(response=f'success', status=200)

app.run("127.0.0.1", "5113")

appKey = "makeUniqueForOurApp"