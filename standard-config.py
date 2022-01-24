from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
import transaction
zapp = app  # noqa
# we add the external method cputils_install
if not hasattr(zapp, 'cputils_install'):
    manage_addExternalMethod(zapp, 'cputils_install', '', 'CPUtils.utils', 'install')
# we run this method
zapp.cputils_install(zapp)
transaction.commit()
# we add the properties hiddenProducts, shownProducts
# from Products.CPUtils.hiddenProductsList import dic_hpList
# to be continued
