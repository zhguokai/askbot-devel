==========
Askbot API
==========

Askbot has API to access forum data in read-only mode.
Current version of API is 1.

All data is returned in json format.

All urls start with `/api/v1/` and the following endpoints are available:

`/api/v1/info/`
---------------

Returns basic parameters of the site.

`/api/v1/users/`
----------------

Returns, count, number of pages and basic data for each user.
Optional parameters: page (<int>), sort (reputation|oldest|recent|username)

`/api/v1/users/<user_id>/`
--------------------------

Returns basic information about a given user.

`/api/v1/questions/`
--------------------

*`/api/v1/questions/`
*`/api/v1/questions/<question_id>/`
