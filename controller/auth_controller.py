# Auth Controller

from flask import Blueprint, request, jsonify, make_response, session
from middleware.dataValidator import (
    validateEmail,
    validatePassword,
)
from middleware.tokenGenerator import generateToken
from middleware.tokenValidator import validateToken
from datetime import datetime

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
        fs = open("logs/user.log", "a")
        fs.write(f"{datetime.now()} | userLogin | {e}\n")
        fs.close()
        return make_response(jsonify({"message": "Internal server error."}), 500)
