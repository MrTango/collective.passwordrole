collective.passwordrole
=======================

Username and password based sharing of private Plone content.

Description
-----------

If installed, you can use the Passwordrole tab on every Folder or other objects
to add Passwordroles. 
Then you can give external users without a Plone account
the direct url to this folder or content and the username password combination
of the added Passwordrole. The external user get a extendet plone login form 
and can use the external login form fields to get access to the private 
Plone content.

Warning
-------

Until now collective.passwordrole does now work with 
Products.PluggableAuthService > 1.9.0! If you use Plone >= 4.2.5 use must pin 
the version Products.PluggableAuthService to 1.9.0!
