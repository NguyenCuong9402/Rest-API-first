from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from project.section_9.extension_db import db
from project.section_9.resources.item import blp as ItemBlueprint
from project.section_9.resources.store import blp as StoreBlueprint
from project.section_9.resources.tag import blp as TagBlueprint
from project.section_9.resources.user import blp as UserBlueprint
import secrets
from project.section_9.blocklist import BLOCKLIST
from flask_migrate import Migrate

def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db.init_app(app)
    migrate = Migrate(app,db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "jose"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    # mã đã thu hồi
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "the token has been revoked", "error": " token_revoked"}
            ), 401
        )

    # yêu cầu làm mới
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "the token is not fresh",
                    "error": " fresh_token_required"
                }
            ), 401
        )

    # set admin
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    # mã đã hết hạn
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"mes": "the token has expired.", "error": " token_expired"}), 401

    # mã không hợp lệ
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"mes": "signature verification failed.", "error": " invalid_expired"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify(
            {"description": " Request does not contain an access token",
             "error": "authorization_required"}
        ), 401)

    with app.app_context():
        db.create_all()
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app


App_main = create_app()
App_main.run()
