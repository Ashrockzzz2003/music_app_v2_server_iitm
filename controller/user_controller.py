from flask import Blueprint, jsonify, make_response, request
from datetime import datetime

from middleware.tokenValidator import validateToken
from middleware.dataValidator import isValidLoginToken
import sqlite3

user = Blueprint("user", __name__)

@user.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "User API is up and running."}), 200)

# Get profile
@user.route("/profile", methods=["GET"])
def getProfile():
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
        
        if decryptedToken["userRoleId"] not in range(1, 4):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        # Validate Token
        if not isValidLoginToken(decryptedToken):
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        userId = decryptedToken["userId"]

        # check if user exists
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userId = ?",
            (userId,),
        )
        user_data = db_cursor.fetchone()
        db_connection.close()

        if user_data == None:
            return make_response(jsonify({"message": "User not found."}), 404)
        
        user_data = dict(zip([key[0] for key in db_cursor.description], user_data))

        if user_data["userAccountStatus"] != '1':
            return make_response(jsonify({"message": "Your account is blocked."}), 401)

        return make_response(jsonify(user_data), 200)


    except Exception as e:
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | getProfile | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)