from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import MONGODB_CONFIG
import datetime

class MongoDBManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            # Create a new client and connect to the server
            self.client = MongoClient(MONGODB_CONFIG['url'])
            
            # Verify the connection
            self.client.admin.command('ping')
            
            # Get the database
            self.db = self.client[MONGODB_CONFIG['database']]
            
            logging.info("Successfully connected to MongoDB Atlas")
        except ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name):
        """
        Get a specific collection
        """
        return self.db[collection_name]

    def insert_document(self, collection_name, document):
        """
        Insert a single document into a collection
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logging.error(f"Error inserting document: {e}")
            return None
        
    def insert_subjects(self, subjects):
        """
        Insert multiple subjects into the subjects collection.
        
        :param subjects: List of subject names to insert.
        """
        try:
            subject_docs = [{'name': subject, 'code': subject[:3].upper(), 'created_at': datetime.datetime.now()} for subject in subjects]
            collection = self.get_collection('subjects')
            result = collection.insert_many(subject_docs)
            return result.inserted_ids
        except Exception as e:
            logging.error(f"Error inserting subjects: {e}")
            return None

    def find_documents(self, collection_name, query, sort=None):
        """
        Retrieve documents from a collection based on a query.
        Optionally sort the results.
    
        :param collection_name: Name of the collection.
        :param query: Query to filter documents.
        :param sort: Sorting criteria, e.g., [("field_name", 1)] for ascending or [("field_name", -1)] for descending.
        :return: Cursor to the documents.
        """
        collection = self.db[collection_name]
        if sort:
            return collection.find(query).sort(sort)
        return collection.find(query)
    

    def update_document(self, collection_name, query, update):
        """
        Update documents in a collection
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(query, {'$set': update})
            return result.modified_count
        except Exception as e:
            logging.error(f"Error updating document: {e}")
            return 0

    def delete_document(self, collection_name, query):
        """
        Delete documents from a collection
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            return 0

    def get_subject_attendance(self, subject):
        """
        Retrieve attendance records for a specific subject.
        
        :param subject: The subject name to filter attendance records.
        :return: List of attendance records.
        """
        try:
            collection = self.get_collection('attendance')
            pipeline = [
                {"$match": {"subject": subject}},
                {"$group": {
                    "_id": "$student_id",
                    "name": {"$first": "$name"},
                    "total_classes": {"$sum": 1},
                    "attended": {"$sum": 1},
                    "percentage": {"$avg": 100},
                    "time": {"$first": "$time"}
                }}
            ]
            result = list(collection.aggregate(pipeline))
            return [(record["_id"], record["name"], record["total_classes"], record["attended"], record["percentage"], record["time"]) for record in result]
        except Exception as e:
            logging.error(f"Error retrieving subject attendance: {e}")
            return []

    def get_overall_attendance(self, from_date, to_date):
        """
        Retrieve overall attendance records within a date range.
        
        :param from_date: The start date of the range.
        :param to_date: The end date of the range.
        :return: List of overall attendance records.
        """
        try:
            collection = self.get_collection('attendance')
            pipeline = [
                {"$match": {"date": {"$gte": datetime.datetime.strptime(from_date, '%Y-%m-%d'), "$lte": datetime.datetime.strptime(to_date, '%Y-%m-%d')}}},
                {"$group": {
                    "_id": "$date",
                    "total_students": {"$sum": 1},
                    "present": {"$sum": 1},
                    "percentage": {"$avg": 100}
                }},
                {"$sort": {"_id": 1}}
            ]
            result = list(collection.aggregate(pipeline))
            return [(record["_id"].strftime('%Y-%m-%d'), record["total_students"], record["present"], record["percentage"]) for record in result]
        except Exception as e:
            logging.error(f"Error retrieving overall attendance: {e}")
            return []

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()