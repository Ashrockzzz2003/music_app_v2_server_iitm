# Auth Controller

from flask import Blueprint, request, jsonify, make_response, session
from middleware.dataValidator import (
    validateEmail,
    validatePassword,
    validateUserFullName,
    validateUserDob,
    validateGender,
    validateOtp,
)
from middleware.tokenGenerator import generateToken
from middleware.tokenValidator import validateToken
from datetime import datetime
from middleware.helper.generateOtp import generate_otp
from middleware.mail.mailer import send_otp_register

import sqlite3


auth = Blueprint("auth", __name__)


@auth.route("/test", methods=["GET"])
def root():
    return make_response(
        jsonify({"message": "Auth API is up and running."}),
        200,
    )


@auth.route("/login", methods=["POST"])
def login():
    """
    {
        "userEmail": "string",
        "userPassword": "string"
    }
    """
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        if not ("userEmail" in data and "userPassword" in data):
            return make_response(jsonify({"message": "Missing parameters."}), 400)

        if not (validateEmail(data["userEmail"])):
            return make_response(jsonify({"message": "Invalid Email."}), 400)

        if not (validatePassword(data["userPassword"])):
            return make_response(jsonify({"message": "Invalid Password."}), 400)

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userEmail = ? AND userPassword = ?",
            (data["userEmail"], data["userPassword"]),
        )
        user_data = db_cursor.fetchone()

        db_connection.close()

        if user_data == None:
            return make_response(
                jsonify({"message": "Invalid Email or Password."}), 404
            )

        if user_data[6] == "0":
            return make_response(jsonify({"message": "Your account is blocked."}), 403)

        token = generateToken(
            {
                "userId": user_data[0],
                "userAccountStatus": user_data[6],
                "userRoleId": user_data[7],
            }
        )

        return make_response(
            jsonify(
                {
                    "message": "Login successful.",
                    "token": token,
                    "userRoleId": user_data[7],
                }
            ),
            200,
        )

    except Exception as e:
        fs = open("logs/auth.log", "a")
        fs.write(f"{datetime.now()} | userLogin | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    

@auth.route("/register", methods=["POST"])
def register():
    """
    {
        "userFullName": "string",
        "userEmail": "string",
        "userPassword": "string",
        "userDob": "string",
        "userGender": "string"
    }
    """
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        if not ("userEmail" in data and "userPassword" in data and "userFullName" in data and "userDob" in data and "userGender" in data):
            return make_response(jsonify({"message": "Missing parameters."}), 400)
        
        if not (validateUserFullName(data["userFullName"])):
            return make_response(jsonify({"message": "Invalid Full Name."}), 400)

        if not (validateEmail(data["userEmail"])):
            return make_response(jsonify({"message": "Invalid Email."}), 400)

        if not (validatePassword(data["userPassword"])):
            return make_response(jsonify({"message": "Invalid Password."}), 400)
        
        if not (validateUserDob(data["userDob"])):
            return make_response(jsonify({"message": "Invalid Date of Birth."}), 400)
        
        if not (validateGender(data["userGender"])):
            return make_response(jsonify({"message": "Invalid Gender."}), 400)
        
        # Check if user already exists. 
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userData WHERE userEmail = ?",
            (data["userEmail"],),
        )
        user_data = db_cursor.fetchone()

        if user_data != None:
            return make_response(jsonify({"message": "Already an account exists with the same email ID."}), 409)
        
        # Generate OTP.
        theOtp = generate_otp()

        # Check if entry already exists in userRegister table.
        db_cursor.execute(
            "SELECT * FROM userRegister WHERE userEmail = ?",
            (data["userEmail"],),
        )

        user_data = db_cursor.fetchone()

        if user_data != None:
            db_cursor.execute(
                "UPDATE userRegister SET userFullName = ?, userPassword = ?, userDob = ?, userGender = ?, userOtp = ?, lastUpdatedAt = CURRENT_TIMESTAMP WHERE userEmail = ?",
                (data["userFullName"], data["userPassword"], data["userDob"], data["userGender"], theOtp, data["userEmail"]),
            )
            db_connection.commit()
            db_connection.close()

            user_data = {
                "registrationId": user_data[0],
                "userEmail": data["userEmail"],
            }

        else:
            db_cursor.execute(
                "INSERT INTO userRegister (userFullName, userEmail, userPassword, userDob, userGender, userRoleId, userOtp) VALUES (?, ?, ?, ?, ?, 2, ?)",
                (data["userFullName"], data["userEmail"], data["userPassword"], data["userDob"], data["userGender"], theOtp),
            )

            user_data = {
                "registrationId": db_cursor.lastrowid,
                "userEmail": data["userEmail"],
            }

            db_connection.commit()
            db_connection.close()

        if user_data["registrationId"] == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)

        # Send to mail.
        if not send_otp_register(data["userEmail"], theOtp):
            return make_response(jsonify({"message": "Internal server error."}), 500)

        otpToken = generateToken({
            "registrationId": user_data["registrationId"],
            "userEmail": data["userEmail"],
        })

        # Return response with OTP Token.
        return make_response(jsonify({"message": "OTP sent to your email.", "otpToken": otpToken}), 200)

    except Exception as e:
        fs = open("logs/auth.log", "a")
        fs.write(f"{datetime.now()} | userRegister | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    
@auth.route("/register/verify", methods=["POST"])
def registerVerify():
    try:
        if not request.is_json:
            return make_response(jsonify({"message": "Missing JSON in request."}), 400)

        data = request.get_json()

        if (not "otp" in data):
            return make_response(jsonify({"message": "Missing parameters."}), 400)
        
        if not (validateOtp(data["otp"])):
            return make_response(jsonify({"message": "Invalid OTP."}), 400)
        
        # Get Request Headers
        tokenData = request.headers.get("Authorization")

        if tokenData == None:
            return make_response(jsonify({"message": "Unauthorized Access"}), 401)
        
        secretToken = tokenData.split(" ")[1]

        # Validate Token
        if len(str(secretToken)) == 0 or secretToken is None:
            return jsonify({"message": "Unauthorized Access"})
        
        if len(secretToken.split(",")) != 3:
            return jsonify({"message": "Unauthorized Access"})
        
        decryptedToken = validateToken(
            secretToken.split(",")[0],
            secretToken.split(",")[1],
            secretToken.split(",")[2],
        )

        if decryptedToken == -2:
            return jsonify({"message": "Session Expired"})
        elif decryptedToken == -1:
            return jsonify({"message": "Unauthorized Access"})

        registrationId = decryptedToken["registrationId"]
        userEmail = decryptedToken["userEmail"]

        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        db_cursor.execute(
            "SELECT * FROM userRegister WHERE registrationId = ? AND userEmail = ? AND userOtp = ?",
            (registrationId, userEmail, data["otp"]),
        )

        registrationData = db_cursor.fetchone()

        if registrationData == None:
            return make_response(jsonify({"message": "Invalid OTP."}), 400)

        # Attempt Delete
        deleteRow = db_cursor.execute(
            "DELETE FROM userRegister WHERE registrationId = ? AND userEmail = ? AND userOtp = ?",
            (registrationId, userEmail, data["otp"]),
        )

        db_connection.commit()
        db_connection.close()

        if deleteRow.rowcount != 1:
            return make_response(jsonify({"message": "Invalid OTP."}), 400)
        
        # Insert into userData
        db_connection = sqlite3.connect("db/app_data.db")
        db_cursor = db_connection.cursor()

        """
        CREATE TABLE IF NOT EXISTS "userData" (
            "userId" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            "userFullName" VARCHAR(255) NOT NULL,
            "userEmail" VARCHAR(255) NOT NULL UNIQUE,
            "userPassword" VARCHAR(255) NOT NULL,
            "userDob" VARCHAR(255) NOT NULL,
            "userGender" CHAR(1) NOT NULL,
            "userAccountStatus" CHAR(1) NOT NULL,
            "userRoleId" INTEGER NOT NULL,
            "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "lastUpdatedAt" TEXT NULL,
            FOREIGN KEY ("userRoleId") REFERENCES "userRole"("roleId"),
            CHECK ("userGender" IN ('M', 'F', 'O')),
            CHECK ("userAccountStatus" IN ('0', '1', '2'))
        );"""

        insertData = db_cursor.execute(
            "INSERT INTO userData (userFullName, userEmail, userPassword, userDob, userGender, userAccountStatus, userRoleId) VALUES (?, ?, ?, ?, ?, '1', 3)",
            (registrationData[1], registrationData[2], registrationData[3], registrationData[4], registrationData[5]),
        )

        db_connection.commit()
        db_connection.close()

        if insertData.lastrowid == None:
            return make_response(jsonify({"message": "Internal server error."}), 500)
        
        return make_response(jsonify({"message": "Registration successful."}), 200)
    

    except Exception as e:
        fs = open("logs/auth.log", "a")
        fs.write(f"{datetime.now()} | userRegisterVerify | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
    


