from baselayer.app.handlers.base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from baselayer.app.access import auth_or_token
from ..models import DBSession, Project


class ProjectHandler(BaseHandler):
    @auth_or_token
    def get(self, project_id=None):
        if project_id is not None:
            proj_info = Project.get_if_owned_by(project_id, self.current_user)
        else:
            proj_info = self.current_user.projects

        return self.success(proj_info)

    @auth_or_token
    def post(self):
        data = self.get_json()

        p = Project(name=data['projectName'],
                    description=data.get('projectDescription', ''),
                    users=[self.current_user])
        DBSession().add(p)
        DBSession().commit()

        return self.success({"id": p.id}, 'cesium/FETCH_PROJECTS')

    @auth_or_token
    def put(self, project_id):
        # This ensures that the user has access to the project they
        # want to modify
        data = self.get_json()

        p = Project.get_if_owned_by(project_id, self.current_user)
        p.name = data['projectName']
        p.description = data.get('projectDescription', '')
        DBSession().commit()

        return self.success(action='cesium/FETCH_PROJECTS')

    @auth_or_token
    def delete(self, project_id):
        p = Project.get_if_owned_by(project_id, self.current_user)
        DBSession().delete(p)
        DBSession().commit()

        return self.success(action='cesium/FETCH_PROJECTS')
