from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

from middleware.dataValidator import validateNonEmptyString, isValidLoginToken
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
