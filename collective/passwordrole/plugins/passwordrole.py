from zope.site.hooks import getSite
from zope.component import getMultiAdapter
from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import (
    IAuthenticationPlugin)
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
#from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
#from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
#from zope.annotation.interfaces import IAnnotations
#from zope.site.hooks import getSite
#from collective.passwordrole.config import ANNOTATIONS_KEY

import logging
log = logging.getLogger("collective.passwordrole.plugins.passwordrole")


manage_addPasswordRoleForm = PageTemplateFile(
    '../www/addPasswordRolePAS', globals(),
    __name__='manage_addPasswordRoleForm')


def addPasswordRolePlugin(self, id, title='', REQUEST=None):
    ''' Add a PasswordRole PAS Plugin to Plone PAS
    '''
    o = PasswordRole(id, title)
    self._setObject(o.getId(), o)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '%s/manage_main?manage_tabs_message=PasswordRole+PAS+Plugin+added.'
            % self.absolute_url())


class PasswordRole(BasePlugin):
    ''' PasswordRole Plugin for PAS
    '''
    meta_type = 'PasswordRole PAS'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    # IExtractionPlugin
    #
    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        # Avoid creating anon user if this is a regular user
        # We actually have to poke request ourselves to avoid users from
        # root becoming anonymous...

        portal = getSite()
        cstate = getMultiAdapter((portal, request),
                name='plone_context_state')

        session = request.SESSION
        if not session.has_key('collective.passwordrole'):
            return {}

        pr_allowed_paths = session['collective.passwordrole'].get(
            'pr_allowed_paths')
        pr_path = '/' + '/'.join(request.physicalPathToVirtualPath(
                                request.physicalPathFromURL(
                                    cstate.current_base_url())))

        if pr_path not in pr_allowed_paths:
            return {}

        if getattr(request, '_auth', None):
            return {}

        return dict(PasswordRole=True)

    #
    # IAuthenticationPlugin
    #
    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        if credentials.has_key('login'):
            return None
        passwordrole = credentials.get('PasswordRole')
        if not passwordrole:
            return None
        return ('Anonymous User', 'Anonymous User')


classImplements( PasswordRole
               , IExtractionPlugin
               , IAuthenticationPlugin
               )

InitializeClass(PasswordRole)
