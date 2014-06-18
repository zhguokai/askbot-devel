========================
Methods to extend Askbot
========================

Askbot can be extended without modifications of the core source code,
by creating a custom python modules containing your extensions and
adding configuration records to your `settings.py` file.
Some extensions are custom forms and others are 
loading custom data for the templates.

In addition, almost always along with the extension it will be 
necessary to customize your Askbot theme.

For example - if you want to display additional
content along with the question - you will create a module allowing
to author and query such content and customize the theme to
display that information.

Finally, in addition to creating Askbot extensions and themes,
it is possible to connect your custom application to Askbot
via askbot and built-in django signals (for this part read the
Django documentation about signals and the 
source code in the file `askbot.models.signals`).

In order to enable an extension - create your extension code and specify
dotted python path to that extensions via the correspondning `settings.py`
variable. For example::

    ASKBOT_NEW_QUESTION_FORM = 'location_extension.forms.AskAboutLocationForm'

Keep in mind that Askbot forms and the context extensions expect specific
variables. To see the details of the usage - look into the Askbot source code.
In order to create a custom form, most often you will want to inherit 
from the corresponding Askbot form.

The following table lists items that currently can be customized
along with the `settings.py` variables that enable the corresponding
extensions.

+-----------------------------------------------------------------------------------------------+
| Form extensions (more extensions may be added later)                                          |
+---------------------------------+-------------------------------------------------------------+
| Item                            | setting                                                     |
+=================================+=============================================================+
| New question form               | `ASKBOT_NEW_QUESTION_FORM`                                  |
+---------------------------------+-------------------------------------------------------------+
| Edit question form              | `ASKBOT_EDIT_QUESTION_FORM                                  |
+---------------------------------+-------------------------------------------------------------+
| Select question revision form   | `ASKBOT_SELECT_QUESTION_REVISION_FORM`                      |
+---------------------------------+-------------------------------------------------------------+
| New answer form                 | `ASKBOT_NEW_ANSWER_FORM`                                    |
+---------------------------------+-------------------------------------------------------------+
| Edit answer   form              | `ASKBOT_EDIT_ANSWER_FORM                                    |
+---------------------------------+-------------------------------------------------------------+
| Select answer revision form     | `ASKBOT_SELECT_ANSWER_REVISION_FORM`                        |
+---------------------------------+-------------------------------------------------------------+
| Extra context for the edit      | `ASKBOT_EDIT_ANSWER_PAGE_EXTRA_CONTEXT`                     |
| answer page                     |                                                             |
+---------------------------------+-------------------------------------------------------------+
| Extra context for the main page | `ASKBOT_QUESTIONS_PAGE_EXTRA_CONTEXT`                       |
+---------------------------------+-------------------------------------------------------------+
| Extra context for the tags page | `ASKBOT_TAGS_PAGE_EXTRA_CONTEXT`                            |
+---------------------------------+-------------------------------------------------------------+
| Extra context for the question  | `ASKBOT_QUESTIONS_PAGE_EXTRA_CONTEXT`                       |
| detail page                     |                                                             |
+---------------------------------+-------------------------------------------------------------+
| Extra context for the user      | `ASKBOT_USER_PROFILE_PAGE_EXTRA_CONTEXT`                    |
| profile page                    |                                                             |
+---------------------------------+-------------------------------------------------------------+
