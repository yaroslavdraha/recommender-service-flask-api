from bson import ObjectId
from pymongo.cursor import Cursor


class Response:

    __data = []
    __success = False
    __error = ""
    __code = None

    def __init__(self):
        self.__data = []

    def setData(self, data):
        self.__data = data

    def clearData(self):
        self.__data = []

    def setSuccess(self, success):
        self.__success = success

    def setError(self, error):
        self.__success = False
        self.__error = error

    def setCode(self, code):
        self.__code = code
        if code == 200:
            self.__success = True

    def get(self):
        # Transform from cursor to list
        data = []
        if type(self.__data) is Cursor:
            for item in self.__data:
                data.append(item)
            self.__data = data

        # Map to array and convert ObjectId to string
        data = []
        if self.__data is not None and len(self.__data) and type(self.__data) is list:
            data = [Response.convert_mongo_item(item) for item in self.__data]
        elif type(self.__data) is dict:
            data.append(Response.convert_mongo_item(self.__data))

        return {
            "data": data,
            "success": self.__success,
            "error": self.__error
        }

    # Convert ObjectId object to string
    @staticmethod
    def convert_mongo_item(item):
        if '_id' in item and type(item['_id']) == ObjectId:
            item['_id'] = str(item['_id'])
        return item
