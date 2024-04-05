# No Auth needed.

from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

import sqlite3

public = Blueprint("public", __name__)

@public.route("/language", methods=["GET"])
def getAllLanguages():
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT languageId, languageCode, languageName from languageData WHERE isActive='1'"
        )
        languageData = db_cursor.fetchall()
        db_connection.close()

        languageData = [dict(zip([key[0] for key in db_cursor.description], language)) for language in languageData]

        return make_response(jsonify({"data": languageData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getAllLanguages | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    

@public.route("/language/<int:language_id>", methods=["GET"])
def getLanguageById(language_id):
    try:
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT languageId, languageCode, languageName from languageData WHERE languageId = ? AND isActive='1'", (language_id,)
        )
        languageData = db_cursor.fetchall()
        db_connection.close()

        languageData = [dict(zip([key[0] for key in db_cursor.description], language)) for language in languageData]

        if languageData == []:
            return make_response(jsonify({"message": "Language not found."}), 404)

        return make_response(jsonify({"data": languageData, "message": "Success"}), 200)


    except Exception as e:
        fs = open("logs/public.log", "a")
        fs.write(f"{datetime.now()} | getLanguageById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)