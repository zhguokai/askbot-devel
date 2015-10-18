How to upgrade Askbot
=====================

Always back up the database before the upgrade.

1) Django Version support.
--------------------------

Currently Askbot supports major versions of Django `1.5` and `1.6`.

This section and the "Django version upgrade" section were written
for the near future use.

All releases supporting these or lower versions of the Django
framework have major release numbers `0.6` and `0.7`.

Upcoming release of Askbot supporting Django `1.7` will have
major version `0.9`. 

Releases of `0.8` series will be made to allow transition
to higher versions of Django, not for production use although
they might just work too.

The reason for this is that starting Django `1.7` 
there is a built-in database migrations system, while before
an external application called ``South`` was used and
the database migration files for these 
two systems are not compatible.

In order to migrate from Django `1.6` and below,
please read section "Django version upgrade".

2) Upgrade of the Askbot software.
----------------------------------

There are two options - either upgrade in the current Python
environment or build entirely new environment.

If you decide to rebuild the Python environment, then proceed
as you would with a new installation, but specify the database
which contains previous data. (Remember to create a full backup
of your data first).

To perform the upgrade in the current environment,
uninstall the current version of askbot: ``pip uninstall askbot``.

If your previous installation was from pypi (Python Package Index),
install new version Askbot using your preferred method
(for example ``pip install askbot=={desired version}``, where
the `{desired version}` might be `0.7.54` or some other.

If your previous installation was from a git repository,
then pull the code from the remote repository and run
``python setup.py develop``.

Now try to run the command ``python manage.py migrate``.
If the system gives directions to modify the `settings.py` file
and/or install specific versions of some packages, please do that
until all packages and the ``settings.py`` file
are updated and the ``migrate`` command completes.

At this point you should have a new working version of Askbot.

3) Django version upgrade.
--------------------------
If your current version of Django is below `1.5`,
first install Django `1.5` or `1.6`, for example:
``pip uninstall django`` then ``pip install django<1.7``.

Upgrade askbot to the latest version of `0.8` series.
For pip you can use specification `askbot<0.9`, e.g.:
``pip uninstall askbot`` then ``pip install askbot<0.9``.

At this point you probably will need to modify the `settings.py` file
and possibly - install correct versions of specific packages.
If this is the case - directions will be given when you attempt
to run database migrations.

Run the database migrations ``python manage.py migrate``.

Now you have the database in the state usable with Django `1.7`,
all that is left to do is one more time
upgrade installed versions of Django and Askbot.

``pip uninstall django`` then ``pip install django<1.8``.

``pip uninstall askbot`` then ``pip install askbot<1.0``.

``python manage.py migrate``

Now you should have a fully migrated version of Askbot 
running on Django `1.7`.
