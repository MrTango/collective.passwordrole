from urlparse import urlparse
from persistent.dict import PersistentDict

from zope.interface import implements
#from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from borg.localrole.interfaces import ILocalRoleProvider

from collective.passwordrole.interfaces import IPasswordRoleAnnotate
#from collective.passwordrole.interfaces import IPasswordRoleSchema
#from collective.passwordrole.interfaces import IPasswordRoleProviding
from collective.passwordrole.config import ANNOTATIONS_KEY

import logging
log = logging.getLogger("collective.passwordrole.passwordroleprovider")


class PasswordRoleAnnotateAdapter(object):
    implements(IPasswordRoleAnnotate)

    def __init__(self, context):
        self.annotations = IAnnotations(context).setdefault(ANNOTATIONS_KEY,
                                                            PersistentDict())

    @apply
    def pr_dict():
        def get(self):
            pr_dict = self.annotations.get('pr_dict', None)
            if not pr_dict:
                pr_dict = self.annotations['pr_dict'] = PersistentDict()
            return pr_dict

        def set(self, key, value):
            self.annotations['pr_dict'][key] = value

        return property(get, set)


class PasswordRoleLocalRolesProviderAdapter(object):
    implements(ILocalRoleProvider)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        """Returns the roles for the given principal in context"""
        roles_to_assign = ()
        request = self.context.REQUEST

        if (principal_id != 'Anonymous User'):
            return ()

        session = request.SESSION
        if 'collective.passwordrole' not in session.keys():
            return ()
        pr_allowed_paths =\
            session["collective.passwordrole"]["pr_allowed_paths"]
        pr_url = request.form.get('came_from')
        if pr_url:
            pr_path = urlparse(pr_url).path
        else:
            physical_path = self.context.getPhysicalPath()
            pr_path = '/' + '/'.join(request.physicalPathToVirtualPath(
                physical_path))

        if pr_path in pr_allowed_paths:
            roles_to_assign = ('Reader',)
        return roles_to_assign

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return ()
