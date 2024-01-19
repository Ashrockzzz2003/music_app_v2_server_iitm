from flask import Blueprint, request, jsonify, make_response, session


admin = Blueprint("admin", __name__)

@admin.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "Admin API is up and running."}), 200)