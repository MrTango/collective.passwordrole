from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from plugins.passwordrole import addPasswordRolePlugin

def importVarious(context):
    ''' Install the PasswordRole PAS plugin
    '''
    out = StringIO()
    portal = context.getSite()

    uf = getToolByName(portal, 'acl_users')
    installed = uf.objectIds()

    if 'passwordrole_pas' not in installed:
        addPasswordRolePlugin(uf, 'passwordrole_pas', 'PasswordRole PAS')
        activatePluginInterfaces(portal, 'passwordrole_pas', out)
    else:
        print >> out, 'passwordrole_pas already installed'

    print out.getvalue()
