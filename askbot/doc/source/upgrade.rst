How to upgrade Askbot
=====================

Always back up the database before the upgrade.

1) Django Version support.
--------------------------

Currently Askbot supports major versions of Django `1.5`, `1.6`, `1.7` and `1.8`,
however - a corresponding version of Askbot must be selected for
each version of the Django framework as shown below:

+---------------------------------+-----------------------+
| Version of the Django framework | Version of Askbot (*) |
+=================================+=======================+
| `1.5.x`                         | `0.7.x`               |
+---------------------------------+-----------------------+
| `1.6.x`                         | `0.8.x` (**)          |
+---------------------------------+-----------------------+
| `1.7.x`                         | `0.9.x`               |
+---------------------------------+-----------------------+
| `1.8.x`                         | `0.10.x`              |
+---------------------------------+-----------------------+

Note (*): select latest version of the corresponding release series,
x means the latest minor release number.

To avoid looking up the latest version within the series, use the following
shortcut, using pip: `pip install askbot<0.9`. Here `<0.9` will
select the latest sub-version of `0.8` series.

Note (**): releases of series `0.8` must be used to migrate
From Django `1.5` and below. Read section "Django version upgrade"
for more information.

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
Django `1.7` came with a backwards incompatible change
in the database migrations. Previously `South` app was used
to make changes in the database schema and in Django `1.7` and
later Django has it's own database migrations system.

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
