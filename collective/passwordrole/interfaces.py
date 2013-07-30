from zope.interface import Interface, Attribute
from zope.annotation.interfaces import IAttributeAnnotatable

class IPasswordRoleProviding(IAttributeAnnotatable):
    """Mark objects able to dispatch 'Password' roles, and therefor annotatable
    """

class IPasswordRoleSchema(Interface):
    """Schema used to manage the usernames and passwords
    """

class IPasswordRoleAnnotate(Interface):
    """Provide access to annotated token roles infos token role dispatching.
    """

    pr_dict = Attribute("dictionary with user/password combinations")

class IPasswordroleTool(Interface):
    def get_passwords_from_annotations(self, context):
        """ return the usernames/passwords from annotations """
