This application was originally developed for askbot Q&A forum
and is based on django-authopenid.

In addition to django-authopenid, this one supports logins via
Twitter, LinkedIn, LDAP, user name and password.

Bugs
====
Facebook authentication is currently broken.

Settings
========

Settings for this application may come from up to two places:

* ``django.conf.settings``
* Loaded from ``EXTRA_SETTINGS_MODULE`` - this, for example may be
  some settings module that holds values in the database and allows 
  editing them via a web - interface.

Settings that come from the django standard ``settings.py``:
------------------------------------------------------------

* ``EXTRA_SETTINGS_MODULE`` (default - ``django.conf.settings``)
* ``SECRET_KEY``
* ``CUSTOM_AUTH_MODULE`` - dotted python path to a custom authentication plugin
* ``OPENID_TRUST_ROOT`` - defaults to the site url

Settings that come from the EXTRA_SETTINGS_MODULE:
--------------------------------------------------

The extra settings module defaults to ``django.conf.settings`` but may be
any module with the same interface.

Site settings
^^^^^^^^^^^^^

* ``APP_SHORT_NAME`` - short name of the site
* ``APP_URL`` - base url of the site
* ``LOCAL_LOGIN_ICON`` - path to local login icon relative to skin media - e.g. '/images/login.gif'

General app settings
^^^^^^^^^^^^^^^^^^^^
* ``SIGNIN_ALWAYS_SHOW_LOCAL_LOGIN`` - always display password login form
* ``ALLOW_ADD_REMOVE_LOGIN_METHODS`` - allow or disallow users to add or remove logins to their accounts

Recaptcha settings
^^^^^^^^^^^^^^^^^^

Recaptcha is used to attempt limitng registration of password accounts to real people.

* ``USE_RECAPTCHA`` - boolean ``True`` or ``False``, default  is ``False``
* ``RECAPTCHA_SECRET`` - recaptcha secret key
* ``RECAPTCHA_KEY`` - recaptcha private key

Email settings
^^^^^^^^^^^^^^

* ``EMAIL_UNIQUE`` - enforce email uniqueness - one account per email if ``True``
* ``EMAIL_VALIDATION`` - require email validation to activate the account
* ``ALLOW_ACCOUNT_RECOVERY_BY_EMAIL`` - allow/disallow recovery of account by email

Login provider settings
^^^^^^^^^^^^^^^^^^^^^^^

This application supports many login methods:
'local', 'AOL', 'Blogger', 'ClaimID', 'Facebook',
'Flickr', 'Google', 'Twitter', 'LinkedIn', 'LiveJournal',
'OpenID', 'Technorati', 'Wordpress', 'Vidoop', 'Verisign', 'Yahoo',

For each, there is a setting with format:
``SIGNIN_`` + uppercased provider name + ``_ENABLED``.

For example - ``SIGNIN_GOOGLE_ENABLED``.

In addition, certain providers requie public and private keys:

* TWITTER_KEY - twitter public key
* TWITTER_SECRET - tritter private key
* LINKEDIN_KEY
* LINKEDIN_SECRET
* FACEBOOK_KEY
* FACEBOOK_SECRET

Ldap parameters:

* LDAP_URL - url of the ldap service
* USE_LDAP_FOR_PASSWORD_LOGIN - boolean enables ldap
* LDAP_PROVIDER_NAME - name for the ldap provider for display
