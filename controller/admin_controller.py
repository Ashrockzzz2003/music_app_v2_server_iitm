from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

from middleware.dataValidator import validateNonEmptyString, isValidLoginToken, validateInteger, validateUserDob, validateSongDuration
from middleware.tokenValidator import validateToken

import sqlite3

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
            """SELECT s.songName, s.songDescription, s.songDuration, s.songReleaseDate, s.songLyrics, s.songAudioFileExt, s.songImageFileExt, g.genreId, g.genreName, l.languageName, l.languageId, s.createdBy, u.userFullName, s.isActive, s.createdAt, s.lastUpdatedAt, s.likesCount, s.dislikesCount, s.songAlbumId
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