from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
# we add the external method cputils_install
if not hasattr(app, 'cputils_install'):
    manage_addExternalMethod(app, 'cputils_install', '', 'CPUtils.utils', 'install')
# we run this method
app.cputils_install(app)

# disable authentication
app.cputils_change_authentication_plugins(activate='0', dochange='1')
import transaction
transaction.commit()
