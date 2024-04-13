from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

from middleware.dataValidator import validateNonEmptyString, isValidLoginToken, validateInteger, validateUserDob, validateSongDuration
from middleware.tokenValidator import validateToken

import sqlite3, os

admin = Blueprint("admin", __name__)

@admin.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "Admin API is up and running."}), 200)

# Genre API
@admin.route("/genre/create", methods=["POST"])
def createGenre():
    """
    {
        "genreName": "string",
        "genreDescription": "string"
    }
    """
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if required fields are present

        if "genreName" not in data or "genreDescription" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["genreName"]) or not validateNonEmptyString(data["genreDescription"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        genreName = str(data["genreName"])
        genreDescription = str(data["genreDescription"])

        # Check if genre already exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT genreId FROM genreData WHERE genreName = ?",
            (genreName,),
        )

        language_data = db_cursor.fetchone()
        db_connection.close()

        if language_data != None:
            return make_response(jsonify({"message": "Genre already exists."}), 400)

        # Create Genre

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO genreData (genreName, genreDescription, isActive, createdBy, lastUpdatedBy) VALUES (?, ?, '1', ?, ?)",
            (genreName, genreDescription, userId, userId),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Genre created successfully."}), 200)

        
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | createGenre | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/genre/<int:genre_id>/update", methods=["POST"])
def updateGenre(genre_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        

        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        # Check if required fields are present

        if "genreName" not in data or "genreDescription" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["genreName"]) or not validateNonEmptyString(data["genreDescription"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        genreName = str(data["genreName"])
        genreDescription = str(data["genreDescription"])

        # Check if genre_id exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM genreData WHERE genreId = ?",
            (genre_id,),
        )

        genre_data = db_cursor.fetchone()
        db_connection.close()

        if genre_data == None:
            return make_response(jsonify({"message": "Genre not found."}), 404)
        
        # Check if genre already exists with the same name

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT genreId FROM genreData WHERE genreName = ? AND genreId != ?",
            (genreName, genre_id),
        )

        genre_data = db_cursor.fetchone()
        db_connection.close()

        if genre_data != None:
            return make_response(jsonify({"message": "Genre already exists."}), 400)
        
        # Update Genre

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE genreData SET genreName = ?, genreDescription = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE genreId = ?",
            
            (genreName, genreDescription, userId, genre_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Genre updated successfully."}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | updateGenre | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/genre/<int:genre_id>/toggle-status", methods=["POST"])
def toggleGenreStatus(genre_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        # Check if genre_id exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT isActive FROM genreData WHERE genreId = ?",
            (genre_id,),
        )

        genre_data = db_cursor.fetchone()
        db_connection.close()

        if genre_data == None:
            return make_response(jsonify({"message": "Genre not found."}), 404)
        
        isActive = genre_data[0]

        if isActive == "1":
            isActive = "0"
        else:
            isActive = "1"

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE genreData SET isActive = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE genreId = ?",
            (isActive, userId, genre_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Genre Status Updated.", "newStatus": isActive}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | toggleGenreStatus | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/genre", methods=["GET"])
def getAllGenre():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT DISTINCT genreData.genreId, genreData.genreName, genreData.genreDescription, genreData.isActive, genreData.createdAt, genreData.lastUpdatedAt, userData.userFullName, userData.userId, userData.userEmail, userData.userGender, userData.userRoleId FROM genreData JOIN userData ON genreData.createdBy = userData.userId",
        )

        genreData = db_cursor.fetchall()
        db_connection.close()

        if genreData == None:
            return make_response(jsonify({"message": "No genres found.", "data": []}), 404)
        
        genreData = [dict(zip([key[0] for key in db_cursor.description], genre)) for genre in genreData]

        return make_response(jsonify({"message": "Success", "data": genreData}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getAllGenre | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/genre/<int:genre_id>", methods=["GET"])
def getGenreById(genre_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT DISTINCT genreData.genreId, genreData.genreName, genreData.genreDescription, genreData.isActive, genreData.createdAt, genreData.lastUpdatedAt, userData.userFullName, userData.userId, userData.userEmail, userData.userGender, userData.userRoleId FROM genreData JOIN userData ON genreData.createdBy = userData.userId WHERE genreData.genreId = ?", (genre_id,)
        )

        genreData = db_cursor.fetchall()
        db_connection.close()

        if genreData == None:
            return make_response(jsonify({"message": "No matching genre found.", "data": []}), 404)
        
        genreData = [dict(zip([key[0] for key in db_cursor.description], genre)) for genre in genreData]

        return make_response(jsonify({"message": "Success", "data": genreData}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getGenreById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Language API
@admin.route("/language/create", methods=["POST"])
def createLanguage():
    """
    {
        "languageCode": "string",
        "languageName": "string"
    }
    """
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if required fields are present

        if "languageCode" not in data or "languageName" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["languageCode"]) or not validateNonEmptyString(data["languageName"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        languageCode = str(data["languageCode"]).lower()
        languageName = str(data["languageName"])

        # Check if language already exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT languageId FROM languageData WHERE languageCode = ?",
            (languageCode,),
        )

        language_data = db_cursor.fetchone()
        db_connection.close()

        if language_data != None:
            return make_response(jsonify({"message": "Language already exists."}), 400)

        # Create language

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO languageData (languageCode, languageName, isActive, createdBy, lastUpdatedBy) VALUES (?, ?, '1', ?, ?)",
            (languageCode, languageName, userId, userId),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Language created successfully."}), 200)

        
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | createLanguage | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/language/<int:language_id>/update", methods=["POST"])
def updateLanguage(language_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        

        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        # Check if required fields are present

        if "languageCode" not in data or "languageName" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["languageCode"]) or not validateNonEmptyString(data["languageName"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)
        
        languageCode = str(data["languageCode"]).lower().strip()
        languageName = str(data["languageName"]).strip()
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM languageData WHERE languageId = ?",
            (language_id,),
        )

        language_data = db_cursor.fetchone()
        db_connection.close()

        if language_data == None:
            return make_response(jsonify({"message": "Language not found."}), 404)
        
        # Check if language already exists with the same code

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT languageId FROM languageData WHERE languageCode = ? AND languageId != ?",
            (languageCode, language_id),
        )

        language_data = db_cursor.fetchone()
        db_connection.close()


        if language_data != None:
            return make_response(jsonify({"message": "Language already exists."}), 400)
        
        # Update language

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE languageData SET languageCode = ?, languageName = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE languageId = ?",
            (languageCode, languageName, userId, language_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Language updated successfully."}), 200)
        
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | updateLanguage | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    
@admin.route("/language/<int:language_id>/toggle-status", methods=["POST"])
def toggleLanguageStatus(language_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT isActive FROM languageData WHERE languageId = ?",
            (language_id,),
        )

        language_data = db_cursor.fetchone()
        db_connection.close()

        if language_data == None:
            return make_response(jsonify({"message": "Language not found."}), 404)
        
        isActive = language_data[0]

        if isActive == "1":
            isActive = "0"
        else:
            isActive = "1"

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE languageData SET isActive = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE languageId = ?",
            (isActive, userId, language_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Language Status Updated.", "newStatus": isActive}), 200)
        
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | toggleLanguageStatus | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/language", methods=["GET"])
def getAllLanguage():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        

        # Get all languages

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT DISTINCT languageData.languageId, languageData.languageCode, languageData.languageName, languageData.isActive, languageData.createdAt, languageData.lastUpdatedAt, userData.userFullName, userData.userId, userData.userEmail, userData.userGender, userData.userRoleId FROM languageData JOIN userData ON languageData.createdBy = userData.userId",
        )

        languageData = db_cursor.fetchall()
        db_connection.close()

        if languageData == None:
            return make_response(jsonify({"message": "No languages found.", "data": []}), 200)

        languageData = [dict(zip([key[0] for key in db_cursor.description], language)) for language in languageData]

        return make_response(jsonify({"message": "Success", "data": languageData}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getLanguage | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/language/<int:language_id>", methods=["GET"])
def getLanguage(language_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        

        # Get language

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT DISTINCT languageData.languageId, languageData.languageCode, languageData.languageName, languageData.isActive, languageData.createdAt, languageData.lastUpdatedAt, userData.userFullName, userData.userId, userData.userEmail, userData.userGender, userData.userRoleId FROM languageData JOIN userData ON languageData.createdBy = userData.userId WHERE languageData.languageId = ?", (language_id,)
        )

        languageData = db_cursor.fetchall()
        db_connection.close()

        languageData = [dict(zip([key[0] for key in db_cursor.description], language)) for language in languageData]

        if languageData == []:
            return make_response(jsonify({"message": "No languages found."}), 404)

        return make_response(jsonify({"message": "Success", "data": languageData}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getLanguage | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Song API
@admin.route("/song/create", methods=["POST"])
def createNewSong():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        data = request.form.to_dict()
        # print(data)

        # Check if required fields are present
        # songName, songDescription (can be empty), songDuration, songReleaseDate, songLyrics (can be empty), songAudioFileExt, songImageFileExt, songGenreId, songLanguageId

        if "songName" not in data or "songDuration" not in data or "songReleaseDate" not in data or "songAudioFileExt" not in data or "songImageFileExt" not in data or "songGenreId" not in data or "songLanguageId" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["songName"]) or not validateNonEmptyString(data["songAudioFileExt"]) or not validateNonEmptyString(data["songImageFileExt"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if not validateInteger(data["songGenreId"]) or not validateInteger(data["songLanguageId"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if not validateUserDob(data["songReleaseDate"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if not validateSongDuration(data["songDuration"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if "songAudio" not in request.files or "songImage" not in request.files:
            return make_response(jsonify({"message": "Missing files."}), 400)

        songAudio = request.files["songAudio"]
        songImage = request.files["songImage"]

        if songAudio.filename == "" or songImage.filename == "":
            return make_response(jsonify({"message": "Missing files."}), 400)
        
        if songAudio.filename.split(".")[-1] != data["songAudioFileExt"] or songImage.filename.split(".")[-1] != data["songImageFileExt"]:
            return make_response(jsonify({"message": "Invalid file extension."}), 400)
        
        # Accept only png images. only mp3 audio files.
        # TODO: Accept more

        if songAudio.filename.split(".")[-1] != "mp3" or songImage.filename.split(".")[-1] != "png":
            return make_response(jsonify({"message": "Only mp3, png files supported"}), 400)
        
        songName = str(data["songName"]).strip()
        if "songDescription" in data:
            songDescription = str(data["songDescription"]).strip()
        else:
            songDescription = None

        songDuration = str(data["songDuration"])
        songReleaseDate = str(data["songReleaseDate"]).strip()
        if "songLyrics" in data:
            songLyrics = str(data["songLyrics"]).strip()
        else:
            songLyrics = None
        
        songAudioFileExt = str(data["songAudioFileExt"]).strip()
        songImageFileExt = str(data["songImageFileExt"]).strip()
        songGenreId = int(data["songGenreId"])
        songLanguageId = int(data["songLanguageId"])

        # Check if release date is valid. That is it should not be less than current date
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT CURRENT_TIMESTAMP"
        )
        current_date = db_cursor.fetchone()
        db_connection.close()

        if current_date == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)
        
        if songReleaseDate < current_date[0]:
            return make_response(jsonify({"message": "Invalid release date."}), 400)

        # Check if genre exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT isActive FROM genreData WHERE genreId = ?",
            (songGenreId,),
        )
        genre_data = db_cursor.fetchone()
        if genre_data == None:
            return make_response(jsonify({"message": "Genre not found."}), 404)
        if genre_data[0] != "1":
            return make_response(jsonify({"message": "Genre blocked now."}), 400)
        db_connection.close()


        # Check if language exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT isActive FROM languageData WHERE languageId = ?",
            (songLanguageId,),
        )
        language_data = db_cursor.fetchone()
        if language_data == None:
            return make_response(jsonify({"message": "Language not found."}), 404)
        if language_data[0] != "1":
            return make_response(jsonify({"message": "Language blocked now."}), 400)
        db_connection.close()

        # Check if song name already exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT songId FROM songData WHERE songName = ?",
            (songName,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data != None:
            return make_response(jsonify({"message": "Song already exists."}), 400)
        

        # Save data if successful save files

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "INSERT INTO songData (songName, songDescription, songDuration, songReleaseDate, songLyrics, songAudioFileExt, songImageFileExt, songGenreId, songLanguageId, isActive, createdBy, lastUpdatedBy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '1', ?, ?)",
            (songName, songDescription, songDuration, songReleaseDate, songLyrics, songAudioFileExt, songImageFileExt, songGenreId, songLanguageId, userId, userId),
        )

        db_connection.commit()
        db_connection.close()

        # Get song id

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT songId FROM songData WHERE songName = ?",
            (songName,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)
        
        songId = song_data[0]

        # Save files

        songAudio.save(f"static/song/audio/{songId}.{songAudioFileExt}")
        songImage.save(f"static/song/poster/{songId}.{songImageFileExt}")

        return make_response(jsonify({"message": "Song created successfully."}), 200)    
        

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | createNewSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/song/<int:song_id>/update", methods=["POST"])
def updateSong(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ?",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        songDescription = song_data["songDescription"]
        songLyrics = song_data["songLyrics"]
        
        data = request.form.to_dict()

        # Check if required fields are present
        # songName, songDescription (can be empty), songDuration, songReleaseDate, songLyrics (can be empty), songAudioFileExt, songImageFileExt, songGenreId, songLanguageId

        if "songName" not in data or "songDuration" not in data or "songReleaseDate" not in data or "songAudioFileExt" not in data or "songImageFileExt" not in data or "songGenreId" not in data or "songLanguageId" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["songName"]) or not validateNonEmptyString(data["songAudioFileExt"]) or not validateNonEmptyString(data["songImageFileExt"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if not validateInteger(data["songGenreId"]) or not validateInteger(data["songLanguageId"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if not validateUserDob(data["songReleaseDate"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if not validateSongDuration(data["songDuration"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)

        if "songAudio" not in request.files or "songImage" not in request.files:
            return make_response(jsonify({"message": "Missing files."}), 400)

        songAudio = request.files["songAudio"]
        songImage = request.files["songImage"]

        if songAudio.filename == "" or songImage.filename == "":
            return make_response(jsonify({"message": "Missing files."}), 400)
        
        if songAudio.filename.split(".")[-1] != data["songAudioFileExt"] or songImage.filename.split(".")[-1] != data["songImageFileExt"]:
            return make_response(jsonify({"message": "Invalid file extension."}), 400)
        
        # Accept only png images. only mp3 audio files.
        # TODO: Accept more

        if songAudio.filename.split(".")[-1] != "mp3" or songImage.filename.split(".")[-1] != "png":
            return make_response(jsonify({"message": "Only mp3, png files supported"}), 400)
        
        songName = str(data["songName"]).strip()
        if "songDescription" in data:
            songDescription = str(data["songDescription"]).strip()

        songDuration = str(data["songDuration"])
        songReleaseDate = str(data["songReleaseDate"]).strip()
        if "songLyrics" in data:
            songLyrics = str(data["songLyrics"]).strip()
        
        songAudioFileExt = str(data["songAudioFileExt"]).strip()
        songImageFileExt = str(data["songImageFileExt"]).strip()
        songGenreId = int(data["songGenreId"])
        songLanguageId = int(data["songLanguageId"])

        # Check if release date is valid. That is it should not be less than current date
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT CURRENT_TIMESTAMP"
        )
        current_date = db_cursor.fetchone()
        db_connection.close()

        if current_date == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)
        
        if songReleaseDate < current_date[0]:
            return make_response(jsonify({"message": "Invalid release date."}), 400)

        # Check if genre exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT isActive FROM genreData WHERE genreId = ?",
            (songGenreId,),
        )
        genre_data = db_cursor.fetchone()
        if genre_data == None:
            return make_response(jsonify({"message": "Genre not found."}), 404)
        if genre_data[0] != "1":
            return make_response(jsonify({"message": "Genre blocked now."}), 400)
        db_connection.close()


        # Check if language exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT isActive FROM languageData WHERE languageId = ?",
            (songLanguageId,),
        )
        language_data = db_cursor.fetchone()
        if language_data == None:
            return make_response(jsonify({"message": "Language not found."}), 404)
        if language_data[0] != "1":
            return make_response(jsonify({"message": "Language blocked now."}), 400)
        db_connection.close()

        # Check if another song exists with the same name

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT songId FROM songData WHERE songName = ? AND songId != ?",
            (songName, song_id),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data != None:
            return make_response(jsonify({"message": "Song already exists."}), 400)
        
        # Update song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE songData SET songName = ?, songDescription = ?, songDuration = ?, songReleaseDate = ?, songLyrics = ?, songAudioFileExt = ?, songImageFileExt = ?, songGenreId = ?, songLanguageId = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE songId = ?",
            (songName, songDescription, songDuration, songReleaseDate, songLyrics, songAudioFileExt, songImageFileExt, songGenreId, songLanguageId, userId, song_id),
        )

        db_connection.commit()
        db_connection.close()

        # Save files

        songAudio.save(f"static/song/audio/{song_id}.{songAudioFileExt}")
        songImage.save(f"static/song/poster/{song_id}.{songImageFileExt}")

        return make_response(jsonify({"message": "Song updated successfully."}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | updateSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/song/<int:song_id>/toggle-status", methods=["POST"])
def toggleSongStatus(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ?",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        isActive = song_data["isActive"]

        if isActive == "1":
            isActive = "0"
        else:
            isActive = "1"

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE songData SET isActive = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE songId = ?",
            (isActive, userId, song_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Song Status Updated.", "newStatus": isActive}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | toggleSongStatus | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/song/<int:song_id>", methods=["GET"])
def getSongById(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            """SELECT s.songName, s.songPlaysCount, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.songAudioFileExt, s.songImageFileExt, g.genreId, g.genreName, l.languageName, l.languageId, s.createdBy, u.userFullName, s.isActive, s.createdAt, s.lastUpdatedAt, s.likesCount, s.dislikesCount, s.songAlbumId
                        FROM songData AS s
                        JOIN genreData AS g ON s.songGenreId = g.genreId 
                        JOIN languageData AS l ON s.songLanguageId = l.languageId
                        JOIN userData AS u ON s.createdBy = u.userId
                        WHERE s.songId = ?""",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # Check if song is of creator

        if song_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        return make_response(jsonify({"message": "Success", "data": song_data}), 200)
        
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getSongById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/song/my-songs", methods=["GET"])
def getMySongs():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            """SELECT s.songName, s.songPlaysCount, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.songAudioFileExt, s.songImageFileExt, g.genreId, g.genreName, l.languageName, l.languageId, s.createdBy, u.userFullName, s.isActive, s.createdAt, s.lastUpdatedAt, s.likesCount, s.dislikesCount, s.songAlbumId
                        FROM songData AS s
                        JOIN genreData AS g ON s.songGenreId = g.genreId 
                        JOIN languageData AS l ON s.songLanguageId = l.languageId
                        JOIN userData AS u ON s.createdBy = u.userId
                        WHERE s.createdBy = ?""",
            (userId,),
        )

        song_data = db_cursor.fetchall()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = [dict(zip([key[0] for key in db_cursor.description], song)) for song in song_data]
        
        return make_response(jsonify({"message": "Success", "data": song_data}), 200)
        
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getSongById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/song/<int:song_id>/delete", methods=["POST"])
def deleteSong(song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ?",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # Check if song is of creator

        if song_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Delete song

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "DELETE FROM playlistSongData WHERE songId = ?",
            (song_id,),
        )

        db_cursor.execute(
            "DELETE FROM userHistory WHERE songId = ?",
            (song_id,),
        )

        db_cursor.execute(
            "DELETE FROM songLikeDislikeData WHERE songId = ?",
            (song_id,),
        )

        db_cursor.execute(
            "DELETE FROM songData WHERE songId = ?",
            (song_id,),
        )

        db_connection.commit()
        db_connection.close()

        # Delete files from /song/audio and /song/poster

        if os.path.exists(f"static/song/audio/{song_id}.mp3"):
            os.remove(f"static/song/audio/{song_id}.mp3")

        if os.path.exists(f"static/song/poster/{song_id}.png"):
            os.remove(f"static/song/poster/{song_id}.png")

        
        return make_response(jsonify({"message": "Song deleted successfully."}), 200)



    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | deleteSong | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

# Albums API
@admin.route("/album/create", methods=["POST"])
def createNewAlbum():
    """
    {
        "albumName": "Album Name",
        "albumDescription": "Album Description",
        "albumReleaseDate": "2022-09-12",
        "albumImage": "Album Image"
    }
    """
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        data = request.form.to_dict()

        # Check if required fields are present
        # albumName, albumDescription, albumReleaseDate, albumImageFileExt

        if "albumName" not in data or "albumReleaseDate" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["albumName"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)
        
        if not validateUserDob(data["albumReleaseDate"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)
        
        if "albumImage" not in request.files:
            return make_response(jsonify({"message": "Missing files."}), 400)
        
        albumImage = request.files["albumImage"]

        if albumImage.filename == "":
            return make_response(jsonify({"message": "Missing files."}), 400)
        
        # Accept only png images.

        if albumImage.filename.split(".")[-1] != "png":
            return make_response(jsonify({"message": "Only png files supported"}), 400)
        
        albumName = str(data["albumName"]).strip()
        if "albumDescription" in data:
            albumDescription = str(data["albumDescription"]).strip()
        else:
            albumDescription = None

        albumReleaseDate = str(data["albumReleaseDate"]).strip()
        albumImageFileExt = "png"

        # Check if release date is valid. That is it should not be less than current date

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT CURRENT_TIMESTAMP"
        )

        current_date = db_cursor.fetchone()
        
        db_connection.close()

        if current_date == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)
        
        if albumReleaseDate < current_date[0]:
            return make_response(jsonify({"message": "Invalid release date."}), 400)
        
        # Check if album name already exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT albumId FROM albumData WHERE albumName = ?",
            (albumName,),
        )

        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data != None:
            return make_response(jsonify({"message": "Album already exists."}), 400)
        
        # Save data if successful save files

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        """CREATE TABLE IF NOT EXISTS "albumData" (
            "albumId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            "albumName" VARCHAR(255) NOT NULL,
            "albumDescription" VARCHAR(255) NULL,
            "albumReleaseDate" TEXT NOT NULL,
            "albumImageFileExt" VARCHAR(10) NOT NULL,
            "albumLikesCount" INTEGER NOT NULL,
            "albumDislikesCount" INTEGER NOT NULL,
            "isActive" CHAR(1) NOT NULL,
            "createdBy" INTEGER NOT NULL,
            "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "lastUpdatedBy" INTEGER NOT NULL,
            "lastUpdatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY ("createdBy") REFERENCES "userData"("userId"),
            FOREIGN KEY ("lastUpdatedBy") REFERENCES "userData"("userId"),
            CHECK ("isActive" IN ('0', '1'))
        );"""

        db_cursor.execute(
            "INSERT INTO albumData (albumName, albumDescription, albumReleaseDate, albumImageFileExt, albumLikesCount, albumDislikesCount, isActive, createdBy, lastUpdatedBy) VALUES (?, ?, ?, ?, 0, 0, '1', ?, ?)",
            (albumName, albumDescription, albumReleaseDate, albumImageFileExt, userId, userId),
        )

        db_connection.commit()

        db_cursor.execute(
            "SELECT albumId FROM albumData WHERE albumName = ?",
            (albumName,),
        )

        album_data = db_cursor.fetchone()

        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)
        
        albumId = album_data[0]

        albumImage.save(f"static/album/{albumId}.{albumImageFileExt}")

        return make_response(jsonify({"message": "Album created successfully."}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | createNewAlbum | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/album/<int:album_id>/update", methods=["POST"])
def updateAlbumData(album_id):
    """
    {
        "albumName": "Album Name",
        "albumDescription": "Album Description",
        "albumReleaseDate": "2022-09-12",
        "albumImage": "Album Image",
        "updateImage": "1",
        "updateReleaseDate": "1"
    }
    """
    if 1 == 1:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if album exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM albumData WHERE albumId = ?",
            (album_id,),
        )
        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

        if album_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        albumDescription = album_data["albumDescription"]
        
        data = request.form.to_dict()

        # Check if required fields are present

        if "albumName" not in data or "updateImage" not in data or "updateReleaseDate" not in data:
            return make_response(jsonify({"message": "Missing required fields."}), 400)
        
        if not validateNonEmptyString(data["albumName"]):
            return make_response(jsonify({"message": "Invalid data."}), 400)
        
        if data["updateImage"] != "0" and data["updateImage"] != "1":
            return make_response(jsonify({"message": "Invalid data."}), 400)
        
        if data["updateReleaseDate"] != "0" and data["updateReleaseDate"] != "1":
            return make_response(jsonify({"message": "Invalid data."}), 400)
        
        if data["updateImage"] == "1" and "albumImage" not in request.files:
            return make_response(jsonify({"message": "Missing files."}), 400)
        
        albumImage = None
        if data["updateImage"] == "1":
            albumImage = request.files["albumImage"]

            if albumImage.filename == "":
                return make_response(jsonify({"message": "Missing files."}), 400)
            
            if albumImage.filename.split(".")[-1] != "png":
                return make_response(jsonify({"message": "Only png files supported"}), 400)
        

        albumName = str(data["albumName"]).strip()
        if "albumDescription" in data:
            albumDescription = str(data["albumDescription"]).strip()
        else:
            albumDescription = album_data["albumDescription"]


        if data["updateReleaseDate"] == "1":
            if "albumReleaseDate" not in data:
                return make_response(jsonify({"message": "Missing required fields."}), 400)
            
            if not validateUserDob(data["albumReleaseDate"]):
                return make_response(jsonify({"message": "Invalid data."}), 400)
            
            albumReleaseDate = str(data["albumReleaseDate"]).strip()

            # Check if release date is valid. That is it should not be less than current date

            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "SELECT CURRENT_TIMESTAMP"
            )

            current_date = db_cursor.fetchone()
            db_connection.close()

            if current_date == None:
                return make_response(jsonify({"message": "Internal server error."}), 500)
            
            if albumReleaseDate < current_date[0]:
                return make_response(jsonify({"message": "Invalid release date."}), 400)
            
        else:
            albumReleaseDate = album_data["albumReleaseDate"]

        # Check if album name already exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT albumId FROM albumData WHERE albumName = ? AND albumId != ?",
            (albumName, album_id),
        )

        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data != None:
            return make_response(jsonify({"message": "Album already exists."}), 400)
        
        # Update album

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE albumData SET albumName = ?, albumDescription = ?, albumReleaseDate = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE albumId = ?",
            (albumName, albumDescription, albumReleaseDate, userId, album_id),
        )

        db_connection.commit()
        db_connection.close()

        if data["updateImage"] == "1":

            albumImage.save(f"static/album/{album_id}.png")

        return make_response(jsonify({"message": "Album updated successfully."}), 200)

    # except Exception as e:
    #     fs = open("logs/admin.log", "a")
    #     fs.write(f"{datetime.now()} | updateAlbumData | {e}\n")
    #     fs.close()
    #     return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/album/<int:album_id>/toggle-status", methods=["POST"])
def toggleAlbumStatus(album_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if album exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM albumData WHERE albumId = ?",
            (album_id,),
        )
        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

        if album_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        isActive = album_data["isActive"]

        if isActive == "1":
            isActive = "0"
        else:
            isActive = "1"


        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE albumData SET isActive = ?, lastUpdatedBy = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE albumId = ?",
            (isActive, userId, album_id),
        )

        db_connection.commit()
        db_connection.close()


        return make_response(jsonify({"message": "Album Status Updated.", "newStatus": isActive}), 200)
    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | toggleAlbumStatus | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    
@admin.route("/album", methods=["GET"])
def getAllAlbums():
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if user_data[2] == 2:
            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "SELECT * FROM albumData WHERE createdBy = ?",
                (userId,),
            )

            album_data = db_cursor.fetchall()
            db_connection.close()

            if album_data == None:
                return make_response(jsonify({"message": "Album not found."}), 404)
            
            album_data = [dict(zip([key[0] for key in db_cursor.description], album)) for album in album_data]
            

            return make_response(jsonify({"message": "Success", "data": album_data}), 200)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT a.albumId, a.albumName, a.albumDescription, a.albumReleaseDate, a.albumImageFileExt, a.albumLikesCount, a.albumDislikesCount, a.isActive, a.createdBy, a.createdAt, a.lastUpdatedBy, a.lastUpdatedAt, u.userFullName, u.userEmail FROM albumData AS a JOIN userData AS u ON a.createdBy = u.userId",
        )

        album_data = db_cursor.fetchall()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        album_data = [dict(zip([key[0] for key in db_cursor.description], album)) for album in album_data]
                      
        return make_response(jsonify({"message": "Success", "data": album_data}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getAllAlbums | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/album/<int:album_id>", methods=["GET"])
def getAlbumById(album_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)

        if user_data[2] == 2:
            db_connection = sqlite3.connect("db/app_data.db")
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "SELECT * FROM albumData WHERE createdBy = ? AND albumId = ?",
                (userId, album_id),
            )

            album_data = db_cursor.fetchone()
            db_connection.close()

            if album_data == None:
                return make_response(jsonify({"message": "Album not found."}), 404)
            
            album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

            return make_response(jsonify({"message": "Success", "data": album_data}), 200)

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT a.albumId, a.albumName, a.albumDescription, a.albumReleaseDate, a.albumImageFileExt, a.albumLikesCount, a.albumDislikesCount, a.isActive, a.createdBy, a.createdAt, a.lastUpdatedBy, a.lastUpdatedAt, u.userFullName, u.userEmail FROM albumData AS a JOIN userData AS u ON a.createdBy = u.userId WHERE a.albumId = ?",
            (album_id,),
        )

        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)

        album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

        # Get Album Songs

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT s.songId, s.songName, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.songAudioFileExt, s.songImageFileExt, g.genreId, g.genreName, l.languageName, l.languageId, s.createdBy, u.userFullName, s.isActive, s.createdAt, s.lastUpdatedAt, s.likesCount, s.dislikesCount, s.songAlbumId FROM songData AS s JOIN genreData AS g ON s.songGenreId = g.genreId JOIN languageData AS l ON s.songLanguageId = l.languageId JOIN userData AS u ON s.createdBy = u.userId WHERE s.songAlbumId = ?",
            (album_id,),
        )

        album_songs = db_cursor.fetchall()
        db_connection.close()

        album_songs = [dict(zip([key[0] for key in db_cursor.description], song)) for song in album_songs]

        return make_response(jsonify({"message": "Success", "data": album_data, "songs": album_songs}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | getAlbumById | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/album/<int:album_id>/addSong/<int:song_id>", methods=["POST"])
def addSongToAlbum(album_id, song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if album exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM albumData WHERE albumId = ?",
            (album_id,),
        )
        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

        if album_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ?",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # Check if song is of creator

        if song_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song is already in album

        if (song_data["songAlbumId"] == album_data["albumId"]):
            return make_response(jsonify({"message": "Song already in album."}), 400)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE songData SET songAlbumId = ? WHERE songId = ?",
            (album_id, song_id),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Song added to album."}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | addSongToAlbum | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)

@admin.route("/album/<int:album_id>/removeSong/<int:song_id>", methods=["POST"])
def removeSongFromAlbum(album_id, song_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if album exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM albumData WHERE albumId = ?",
            (album_id,),
        )
        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

        if album_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if song exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "SELECT * FROM songData WHERE songId = ?",
            (song_id,),
        )

        song_data = db_cursor.fetchone()
        db_connection.close()

        if song_data == None:
            return make_response(jsonify({"message": "Song not found."}), 404)
        
        song_data = dict(zip([key[0] for key in db_cursor.description], song_data))

        # Check if song is of creator

        if song_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if (song_data["songAlbumId"] != album_data["albumId"]):
            return make_response(jsonify({"message": "Song not in album."}), 400)
        
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "UPDATE songData SET songAlbumId = NULL WHERE songId = ?",
            (song_id,),
        )

        db_connection.commit()
        db_connection.close()

        return make_response(jsonify({"message": "Song removed from album."}), 200)

    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | removeSongFromAlbum | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)      

@admin.route("/album/<int:album_id>/delete", methods=["POST"])
def deleteAlbum(album_id):
    try:
        # Authorize
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None or len(tokenData.split(" ")) != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if len(secretToken.split(",")) != 3:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return make_response(jsonify({"message": "Session Expired"}), 401)
        elif decryptedToken == -1:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        if decryptedToken["userRoleId"] != 1 and decryptedToken["userRoleId"] != 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT userId, userAccountStatus, userRoleId FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        # Check if user is admin or creator

        if user_data[2] != 1 and user_data[2] != 2 and user_data[1] != "1":
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Check if album exists

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM albumData WHERE albumId = ?",
            (album_id,),
        )

        album_data = db_cursor.fetchone()
        db_connection.close()

        if album_data == None:
            return make_response(jsonify({"message": "Album not found."}), 404)
        
        album_data = dict(zip([key[0] for key in db_cursor.description], album_data))

        if album_data["createdBy"] != userId and user_data[2] == 2:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Delete Album

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "DELETE FROM albumLikeDislikeData WHERE albumId = ?",
            (album_id,),
        )

        db_cursor.execute(
            "UPDATE songData SET songAlbumId = NULL WHERE songAlbumId = ?",
            (album_id,),
        )

        db_cursor.execute(
            "DELETE FROM albumData WHERE albumId = ?",
            (album_id,),
        )

        db_connection.commit()
        db_connection.close()

        # Delete Album Image

        if os.path.exists(f"static/album/{album_id}.png"):
            os.remove(f"static/album/{album_id}.png")

        return make_response(jsonify({"message": "Album deleted successfully."}), 200)


    except Exception as e:
        fs = open("logs/admin.log", "a")
        fs.write(f"{datetime.now()} | deleteAlbum | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)