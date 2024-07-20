#!/usr/bin/env python3
"""Write a Python function that lists all documents in a collection"""
import pymongo


def list_all(mongo_collection):
    """Lists all documents in a collection"""
    if not mongo_collection:
        return []
    docs = mongo_collection.find()
    return [post for post in docs]
