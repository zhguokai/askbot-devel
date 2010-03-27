This branch is created to develop a multi-auth application (django app)
Here is a thread on the subject
http://groups.google.com/group/askbot/browse_thread/thread/1916dfcf666dd56c

Login system will do this
============================
* accept federated logins (openid of multiple kinds, oauth, 
  facebook, live, twitter) 
* allow password login (one per account) 
* be extendable to accept external password verification (where third
  party programmer is responsible for the implementation) 
* support account recovery by email 
* serve as single signon system for multiple sites hosted at same 
  toplevel domain (e.g. a.site.com b.site.com ) where those are not all 
  necessarily Django sites (they may be php or asp based or anything 
  else) 
* allow to "attach" itself to multiple pre-existing sites with 
  independent user account systems and later take over the 
  responsibility for the simultaneous login to those sites 
* allow multiple login methods per user account 
* user may be logged in through multiple methods at the same time 
* user may be logged in via email recovery alone (even if no login 
  methods are registered yet for the account) 
* restrict one account per email address 
* allow admin configuration through the web (setup keys, enable/ 
  disable specific methods etc.) 
* handle avatar and serve it to the "client" applications. 
* login application may work under own urls or may be injectable into 
  other applications 
