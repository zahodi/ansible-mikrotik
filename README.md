Ansible MikroTik modules
========================

Introduction
------------

This repository provides Ansible modules to manage MikroTik RouterOS-based
devices.

Requirements
------------

Ansible=2.4.2.0

At this time there are no external dependencies. However, there are additional
Python modules that are required by the Ansible modules. You may find these in
`pythonlibs`. Before using Ansible you should add these libraries to your
Python path:
`export PYTHONPATH="$PYTHONPATH:$PWD/pythonlibs"`

Development
-----------
-----------

In order to test this module, you'll need a RouterOS instance to target. If you
have an existing RouterOS-based MikroTik device, you need only make sure the
API service is enabled.

AWS EC2
-------
You can use an ec2 CHR image for testing. Keep in mind that as of right now we can only set up two interfaces on most ec2 instances.
https://aws.amazon.com/marketplace/pp/B01E00PU50?qid=1517274040207&sr=0-1&ref_=srh_res_product_title

Vagrant
-------
This repository provides a Vagrantfile for setting up the x86 build
of RouterOS for testing. To use it, you must first ensure Vagrant and
VirtualBox are installed. Then, run `./create_vagrant_mikrotik.sh` to download
the official MikroTik Cloud Hosted Router (CHR) image from MikroTik, package
it as a Vagrant .box file, and register the .box with Vagrant.

Then, you need only run `vagrant up` in the repository root to start the CHR.

Ansible setup
------------

To use pipenv ensure pipenv is installed:

`pip install pipenv`

Then enable virtualenv and install dependencies:

`pipenv shell`

`pipenv install`

Installing
----------

These modules are still in a very early stage of development; stay tuned for
installation instructions later! :)
