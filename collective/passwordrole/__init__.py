# -*- extra stuff goes here -*-
from Products.PluggableAuthService.PluggableAuthService import (
    registerMultiPlugin)
from plugins import passwordrole
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("collective.passwordrole")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    registerMultiPlugin(passwordrole.PasswordRole.meta_type)  # Add to PAS menu
    context.registerClass(
        passwordrole.PasswordRole,
        constructors=(
            passwordrole.manage_addPasswordRoleForm,
            passwordrole.addPasswordRolePlugin
        ), visibility=None)
