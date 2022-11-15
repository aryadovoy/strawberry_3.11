from sqladmin import ModelView

from db.models import UserModel, FileModel


class AuthModelView(ModelView):

    def is_accessible(self, request) -> bool:
        # return True
        if user := request.session.get('user'):
            return user['is_active'] and user['is_superuser']
        return False

    def is_visible(self, request) -> bool:
        # return True
        if user := request.session.get('user'):
            return user['is_active'] and user['is_superuser']
        return False


class UserAdmin(AuthModelView, model=UserModel):
    column_list = [UserModel.id, UserModel.email, UserModel.is_active]


class FileAdmin(AuthModelView, model=FileModel):
    column_list = [FileModel.file_name, FileModel.is_deleted]


def init_admin_page(admin_app):
    admin_app.register_model(UserAdmin)
    admin_app.register_model(FileAdmin)
