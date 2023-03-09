from flask.views import MethodView
from flask_smorest import Blueprint, abort
from project.section_9.schemas import StoreSchema
from project.section_9.extension_db import db
from project.section_9.models import StoreModel, ItemModel, TagModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("stores", __name__, description=" Operations on stores")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    # del shop khi không có items
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        while True:
            store_id_item = ItemModel.query.filter(ItemModel.store_id == store_id).first()
            if not store_id_item:
                break
            db.session.delete(store_id_item)
            db.session.commit()
        while True:
            store_id_tag = TagModel.query.filter(TagModel.store_id == store_id).first()
            if not store_id_tag:
                break
            db.session.delete(store_id_tag)
            db.session.commit()
        db.session.delete(store)
        db.session.commit()
        return {"message": " Store Delete"}


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the store")
        return store
