.. _solr:

===========================================================
Installing Apache Solr with Apache Tomcat 7 in Ubuntu 12.04
===========================================================


This document describes the process of instalation of Apache Solr search engine in Ubuntu Server  12.04
for askbot use. To follow this steps you must have already askbot installed and running.

Getting the requirements
------------------------

We need the following packages installed::

    sudo apt-get install tomcat7 tomcat7-admin

We need to download Apache Solr from the `official site <http://lucene.apache.org/solr/downloads.html>`_::

    wget http://apache.mirrors.pair.com/lucene/solr/4.3.0/solr-4.3.0.tgz

Then we decompress it::

    tar -xzf solr-4.3.0.tgz

Setting up Tomcat
-----------------

After installing tomcat there are some configuration required to make it work. First we are going to add 
Tomcat users. Edit /etc/tomcat7/tomcat-users.xml and add the following::

    <?xml version='1.0' encoding='utf-8'?>
    <tomcat-users>
      <role rolename="manager"/>
      <role rolename="admin"/>
      <role rolename="admin-gui"/>
      <role rolename="manager-gui"/>
      <user username="tomcat" password="tomcat" roles="manager,admin,manager-gui,admin-gui"/>
    </tomcat-users>

This will allow you to connect to the web management interface. After doing it restart the service:

    service tomcat7 restart

To make see if it works go to: http://youripaddress:8080/manager it will ask for your tomcat user password 
described in the tomcat-users.xml

Installing Solr under Tomcat
----------------------------

Extract the solr tar archive from the previous download::

    tar -xzf solr-4.3.0.tgz

Copy the example/ directory from the source to /opt/solr/. Open the file /opt/solr/example/conf/solrconfig.xml 
and Modify the dataDir parameter as:: 

    <dataDir>${solr.data.dir:/opt/solr/example/solr/data}</dataDir>

Copy the .war file in dist directory to /opt/solr::

    cp dist/apache-solr-3.6.2.war  /opt/solr

Create solr.xml inside of /etc/tomcat/Catalina/localhost/ with the following contents::

    <?xml version="1.0" encoding="utf-8"?>
    <Context docBase="/opt/solr/apache-solr-3.6.2.war" debug="0" crossContext="true">
      <Environment name="solr/home" type="java.lang.String" value="/opt/solr/example/solr" override="true"/>
    </Context>

Restart tomcat server::
    
    service tomcat7 restart

By now you should be able to see the "solr" application in the tomcat manager and also access it in /solr/admin.


Configuring Askbot with Solr
----------------------------

Open settings.py file and configure the following::

    ENABLE_HAYSTACK_SEARCH = 'solr'
    HAYSTACK_SEARCH_ENGINE = 'solr'
    HAYSTACK_SOLR_URL = 'http://127.0.0.1:8080/solr'

After that create the solr schema and store the output to your solr instalation::

    python manage.py build_solr_schema > /opt/solr/example/solr/conf/schema.xml

Restart tomcat server::
    
    service tomcat7 restart

Build the Index for the first time::

    python manage.py rebuild_index

The output should be something like::

    All documents removed.
    Indexing 43 people.
    Indexing 101 posts.
    Indexing 101 threads.

You must be good to go after this, just restart the askbot application and test the search with haystack and solr


Keeping the index fresh
-----------------------

For this we recommend to use one of haystack `third party apps <http://django-haystack.readthedocs.org/en/latest/other_apps.html>`_ that use celery, 
plese check this `link <http://django-haystack.readthedocs.org/en/latest/other_apps.html>`_  for more info.
