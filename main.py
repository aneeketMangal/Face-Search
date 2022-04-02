import uvicorn
from src.database.database import Database
from src.utils.modem import Modem
from multiprocessing import Pool
from fastapi import FastAPI, File, UploadFile, Form
import logging
import json


# opening config file to load the required settings for the server
configFile = open('config.json', 'r')
config = json.load(configFile)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# configuring the logger to log the debug/warning messages
logging.basicConfig(
    filename=config['log']['location'],
    filemode='w',
    format = '%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG
)

logging.debug("Main function called")

# instantiating the app
app = FastAPI()
modem = Modem() # creating a modem object
database = Database(
    config['database']
) # creating a database object
logging.info("Server started")

# Defining the endpoints of the API


"""
    - /search_faces/:
        - POST:
            - URL parameters: k, confidence/tolerance
            - File: an image file
            - Sample URL = "localhost:8000/search_faces/?confidence=0.4&k=100 HTTP/1.1"
            - Returns a list of top-k matching faces from the database
            -
"""
@app.post("/search_faces/")
async def search_faces(
    tolerance: float,
    k: int,
    file: UploadFile =
    File(
        ...,
        description="An image file, possible containing multiple human faces."
        )
    ):
    logging.debug("search_faces endpoint called")
    facesObject = await file.read()
    facesEncodingArray = modem.encodeMultipleFaces(facesObject) # converting the image into encoding
    targetObjectArray = database.getFacesWithoutMetaData()  # getting all the faces from the database

    targetEncodingArray = []
    for target in targetObjectArray:
        if(target[1] != None):
            # converting pickle objects back to array
            targetEncodingArray.append([modem.decode(target[1]), target[0], target[2]]) 

    # finding the matches
    matches = {}
    for index, face in enumerate(facesEncodingArray): # iterating over each face in the given image
        currMatches = []
        for idx, target in enumerate(targetEncodingArray): # iterating and checking over each face in the database
            distance = modem.compareImages(face, target[0])
            if(distance < tolerance): # if the distance is less than the tolerance, the face is a match
                currMatches.append([distance, [target[1], target[2]]])
        
        currMatches.sort(key=lambda x: x[0], reverse=True)
        currFace = "Face--"+ str(index+1)
        matches[currFace] = []
        for i in range(min(len(currMatches), k)):
            # storing id and names of matching faces
            matches[currFace].append({
                "id": currMatches[i][1][0],
                "name": currMatches[i][1][1]
            })

    return {
       "status": "OK", 
       "body": {
           "matches": matches
        }
    }

"""
    - /add_face/:
        - POST:
            - File: an image file
            - Sample URL = "localhost:8000/domain/add_face/"
            - Uploads a face in the image file to the database
"""

@app.post("/add_face/")
async def add_face(
    file: UploadFile =
                  File(..., description="An image file having a single human face."
            ) 
        ):

    # reading the contents of the file, since read() is an async operation, await is used
    image = await file.read()
    # using an internal function to get the face encoding of image
    face, metadata = modem.encodeSingleFace([image, file.filename])
    
    # if no face is found
    if(face is None):
        return {
            "status": "ERROR",
            "body": "No face found in the image"
        }
    else:
        # adding the face to the database, if its detected
        database.insertFaceWithMetaData(face, metadata)
        return {
            "status": "OK",
            "body": "Face added successfully"   
        }

"""
    - /add_faces_in_bulk/:
        - POST:
            - File: a zip file
            - Sample URL = "localhost:8000/domain/add_faces_in_bulks/"
            - Uploads faces in the image files inside a zip file to the database
"""

@app.post("/add_faces_in_bulk/")
async def add_faces_in_bulk(
    file: UploadFile = 
        File(
            ..., description="A ZIP file containing multiple face images."
        )
    ):

    
    # reading the file fetched from the http request
    zip = await file.read() 
    fileArray = modem.encodeZip(zip)
    faceDataArray = []

    # Now after receiving the array of file contents
    # we now fetch the face encoding of each image
    # Multiprocessing has been used to speed up the process
    # A pool of 8 processes are created
    try: 
        pool = Pool(processes=8) # creating a pool of 8 processes
        faceDataArray = pool.map(func=modem.encodeSingleFace, iterable=fileArray) # mapping the processes to the function and arguement
    finally: 
        pool.close() # closing the pool once the processes are done
        pool.join()

    
    imagesAdded = 0
    for face in faceDataArray:
        if(face[0] is not None):
            imagesAdded+=1
            database.insertFaceWithMetaData(face[0], face[1])

    return {
        "status": "OK", 
        "body": str(imagesAdded)+ " faces added"
    }


"""
    - /get_face_info/:
        - POST:
            - form data: api_key and face_id
            - Sample URL = "localhost:8000/domain/add_faces_in_bulks/"
            - Uploads faces in the image files inside a zip file to the database
"""



@app.post("/get_face_info/")
async def get_face_info(api_key: str = Form(...), face_id: str = Form(...)):
    faceObject = database.getFaceMetaData(int(face_id))
    if(faceObject is None):
        return {
            "status": "ERROR",
            "body": "Face not found"
        }
    else:
        return {
            "status": "OK",
            "body": {
                "id": faceObject[0],
                "person": faceObject[1],
                "version": faceObject[2],
                "date": faceObject[3],
                "location": faceObject[4],
            }
        }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host = config['server']['host'],
        port = config['server']['port'],
        debug = config['server']['debug']
    )