import pickle
class Face:
    """
        Class to represent a face object, provides utility functiions for the same.
        It enables conversion between pickle and numpy array
    """

    def __init__(self, faceEncoding, isPickle = False):
        self.__faceEncoding = faceEncoding # face encoding array
        if(isPickle):
            self.__faceEncoding = pickle.loads(faceEncoding)

            
    def getEncoding(self):
        # returns the pickle encoding of the image
        return pickle.dumps(self.__faceEncoding)

    def getArrayEncoding(self):
        # get array representation of face object
        return self.__faceEncoding

    def __str__(self):
        return str(self.__faceEncoding)