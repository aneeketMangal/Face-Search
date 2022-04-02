from src.utils.face import Face
from pathlib import Path
import face_recognition
import io
import zipfile
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import date


class Modem:
    """
        Modem class handle the work of converting
        files into suitable encoding to insert into database
    """
    def __init__(self):
        pass

    def compareImages(self, image1, image2):
        """
            Compares two images and returns the confidence
            of the match
        """

        distance = face_recognition.face_distance(
            [image2.getArrayEncoding()], 
            image1.getArrayEncoding()
        )
        
        return distance    

    
    # function to convert image into encoding
    # returns an array of face encodings (128*n array format)
    def encode(self, imageObject):
        try:
            imageObject = io.BytesIO(imageObject)
            imageLoad = face_recognition.load_image_file(imageObject)
            # returns an array of face encodings (128*n array format)
            imageEncodings = face_recognition.face_encodings(imageLoad)
            return imageEncodings
        except Exception as e:
            # in case image cannot be encoded for some reason, then a empty array is returned
            # indicated that no face was present in the file
            return []     
        
    """
        Converts a image object into 
        required encoding.
        It returns a [face object, metaData] in case a face is present
    """
    def encodeSingleFace(self, fileObject):
        imageEncodings = self.encode(fileObject[0])
        face: Face = None
        if(len(imageEncodings)>0):
            face = Face(imageEncodings[0])
        
        metadata = {
            "person": Path(fileObject[1]).stem, # name of the person is assumed to be same as fileName
            "date": date.today(), # date when the image is added on the server
            "version": "NA", # version of the image
            "location": "NA" # location of the image
        }

        # extracting metadata from the image, if a face is present
        # in the image
        if(face is not None):
            imageObject = io.BytesIO(fileObject[0])
            image = Image.open(imageObject)
            exifdata = image.getexif() # getting exif data from the images
            for tag_id in exifdata:
                tag_name = TAGS.get(tag_id, tag_id)
                value = exifdata.get(tag_id)
                
                # checking if a tag contains the word "version" in it
                # if it does, then it is assumed to be the version of the image
                # similar is the case with location
                if(tag_name == "version"): 
                    metadata["version"] = value

                if(tag_name == "location"):
                    metadata["location"] = value

            return [face, metadata]
        return [face, None]

    # function to fetch multiple face encodings
    # return an array of Face objects
    def encodeMultipleFaces(self, imageObject):
        imageEncodings = self.encode(imageObject)
        imageEncodingsArray = []
        for encoding in imageEncodings:
            imageEncodingsArray.append(Face(encoding))

        return imageEncodingsArray

    
    # returns an array of [file.read(), fileName] objects
    # it will be used to convert the zip file into an array of File objects
    def encodeZip(self, zipObject):
        try:
            zipBinary = io.BytesIO(zipObject)
            zip = zipfile.ZipFile(zipBinary)
            fileArray = []
            for file in zip.namelist():
                # checking if current file is a directory
                if(file.endswith("/")) or (file.endswith("\\")):
                    continue
                fileOpen = zip.open(file)
                fileRead = fileOpen.read()
                fileArray.append([fileRead, file])
            return fileArray
        except Exception as e:
            return []
        

    # converting pickle objects in Face objects
    def decode(self, imageEncoding):
        return Face(imageEncoding, isPickle=True)
