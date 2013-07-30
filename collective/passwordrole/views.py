# python imports
from urlparse import urlparse

import z3c.form.form
from AccessControl import AuthEncoding
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from z3c.form import button
from zope import schema
from zope.publisher.browser import BrowserView
from zope.site.hooks import getSite

from Products.statusmessages.interfaces import IStatusMessage
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model

from collective.passwordrole.config import ANNOTATIONS_KEY
from collective.passwordrole.interfaces import IPasswordRoleProviding
from collective.passwordrole.passwordroleprovider import IPasswordRoleAnnotate
from collective.passwordrole import _


import logging
log = logging.getLogger("collective.passwordrole.views.PasswordroleView")


class IPasswordroleAddCredentialForm(model.Schema):
    """ Passwordrole add credentials form fields
    """
    username = schema.TextLine(
        title=_(u"Username"),
        required=True
    )
    password = schema.Password(
        title=_(u"Password"),
        required=True
    )


class PasswordroleAddCredentialForm(AutoExtensibleForm, z3c.form.form.Form):
    """ form to add new passwordrole credentials to context annotations
    """
    schema = IPasswordroleAddCredentialForm
    ignoreContext = True

    label = _(u"Add passwordrole")
    description = _(u"You can add new passwordrole credentials here.")

    @button.buttonAndHandler(u'add passwordrole')
    def handleApply(self, action):
        data, errors = self.extractData()
        msg = IStatusMessage(self.request)
        if errors:
            msg.addStatusMessage(self.formErrorsMessage)
            return

        annotations = IPasswordRoleAnnotate(self.context)
        username = data['username']
        password = self._encryptPassword(data['password'])
        annotations.pr_dict[username] = password
        msg.addStatusMessage(_(u"passwordrole added"))
        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/manage-passwordroles')

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """
        """

    def _encryptPassword(self, pw):
        return AuthEncoding.pw_encrypt(pw, 'SSHA')


class ManagePasswordrolesView(BrowserView):
    """ Show all password roles in context and allow to delete one.
    """
    def passwordroles(self):
        """ return passwordroles list
        """
        context = self.context
        annotations = IPasswordRoleAnnotate(context)
        if not annotations:
            log.debug("No \"%s\" annotations not found for: %s." % (
                ANNOTATIONS_KEY, context.absolute_url_path()))
            return []
        return annotations.pr_dict.keys()

    def delete_passwordrole(self):
        """
        """
        msg = IStatusMessage(self.request)
        id = self.request.get('id')
        if not id:
            msg.addStatusMessage(_(u"no id to delete given!"))
            return self.request.RESPONSE.redirect(
                self.request.HTTP_REFERER)
        context = self.context
        annotations = IPasswordRoleAnnotate(context)
        if not annotations:
            log.info("No \"%s\" annotations not found for: %s." % (
                ANNOTATIONS_KEY, context.absolute_url_path()))
            return
        if id in annotations.pr_dict.keys():
            del annotations.pr_dict[id]
            msg.addStatusMessage(_(u"Passwordrole \'%s\' deleted.") % id)
        return self.request.RESPONSE.redirect(
            self.request.HTTP_REFERER)


class PasswordroleView(BrowserView):
    """ give access to objects if matching username/password
        found in annotations
    """

    def __call__(self):
        """
        """
        if self.check_passwordrole_credentials(self.request):
            log.debug("redirect to %s" % self.request.get('came_from'))
            return self.request.RESPONSE.redirect(
                self.request.get('came_from'))
        else:
            log.debug("redirect to %s" % self.request.HTTP_REFERER)
            return self.request.RESPONSE.redirect(self.request.HTTP_REFERER)

    def check_passwordrole_credentials(self, request):
        """ check passwordrole creadentials for given path, user, pw
            combination
        """
        session = request.SESSION
        if 'collective.passwordrole' not in session.keys():
            session["collective.passwordrole"] = PersistentMapping({
                "pr_allowed_paths": PersistentList(),
            })

        pr_allowed_paths =\
            session["collective.passwordrole"]["pr_allowed_paths"]
        pr_url = request.form.get('came_from')
        if not pr_url:
            return
        pr_path = urlparse(pr_url).path

        if pr_path not in pr_allowed_paths:
            # check credentials in annotations and store path in session
            ac_name = request.get('__ac_name')
            ac_password = request.get('__ac_password')
            if not ac_name:
                return

            portal = getSite()
            pr_context = portal.unrestrictedTraverse(pr_path.lstrip('/'))
            if not IPasswordRoleProviding.providedBy(pr_context):
                return
            annotations = IPasswordRoleAnnotate(pr_context)
            parent_annotations = IPasswordRoleAnnotate(
                pr_context.aq_inner.aq_parent)
            if not annotations:
                log.debug("look in parent annotations for \
                        passwordrole credentials")
                annotations = parent_annotations
            if not annotations:
                log.info("No \"%s\" annotations not found for: %s." % (
                    ANNOTATIONS_KEY, pr_path))
                return
            credential_pw = annotations.pr_dict.get(ac_name)
            if not credential_pw:
                credential_pw = parent_annotations.pr_dict.get(ac_name)
            if not credential_pw:
                log.info("No password found for credential: %s." %
                         ac_name)
                return
            if not AuthEncoding.pw_validate(credential_pw, ac_password):
                log.info("Password does not matched for credential: %s." %
                         ac_name)
                return

            pr_allowed_paths.append(pr_path)
        return True

    def _encryptPassword(self, pw):
        return AuthEncoding.pw_encrypt(pw, 'SSHA')
