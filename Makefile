PROJECT=namesdb-public
APP=namesdbpublic
USER=ddr
SHELL = /bin/bash

APP_VERSION := $(shell cat VERSION)
GIT_SOURCE_URL=https://github.com/denshoproject/namesdb-public

# Release name e.g. stretch
DEBIAN_CODENAME := $(shell lsb_release -sc)
# Release numbers e.g. 8.10
DEBIAN_RELEASE := $(shell lsb_release -sr)
# Sortable major version tag e.g. deb8
DEBIAN_RELEASE_TAG = deb$(shell lsb_release -sr | cut -c1)

ifeq ($(DEBIAN_CODENAME), bullseye)
	PYTHON_VERSION=python3.9
endif

# current branch name minus dashes or underscores
PACKAGE_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | tr -d _ | tr -d -)
# current commit hash
PACKAGE_COMMIT := $(shell git log -1 --pretty="%h")
# current commit date minus dashes
PACKAGE_TIMESTAMP := $(shell git log -1 --pretty="%ad" --date=short | tr -d -)

# Media assets and Elasticsearch will be downloaded from this location.
# See https://github.com/densho/ansible-colo.git for more info:
# - templates/proxy/nginx.conf.j2
# - templates/static/nginx.conf.j2
PACKAGE_SERVER=ddr.densho.org/static/namesdbpublic

SRC_REPO_ASSETS=https://github.com/denshoproject/ddr-public-assets.git

INSTALL_BASE=/opt
INSTALL_NAMESDBPUBLIC=$(INSTALL_BASE)/namesdb-public
INSTALL_ASSETS=/opt/ddr-public-assets
REQUIREMENTS=./requirements.txt
PIP_CACHE_DIR=$(INSTALL_BASE)/pip-cache

VIRTUALENV=$(INSTALL_NAMESDBPUBLIC)/venv/ndbpub

CONF_BASE=/etc/ddr
CONF_PRODUCTION=$(CONF_BASE)/namesdbpublic.cfg
CONF_LOCAL=$(CONF_BASE)/namesdbpublic-local.cfg

SQLITE_BASE=/var/lib/ddr
LOG_BASE=/var/log/ddr

MEDIA_BASE=/var/www/namesdbpublic
MEDIA_ROOT=$(MEDIA_BASE)/media
ASSETS_ROOT=$(MEDIA_BASE)/assets
STATIC_ROOT=$(MEDIA_BASE)/static

SUPERVISOR_GUNICORN_CONF=/etc/supervisor/conf.d/namesdbpublic.conf
NGINX_CONF=/etc/nginx/sites-available/namesdbpublic.conf
NGINX_CONF_LINK=/etc/nginx/sites-enabled/namesdbpublic.conf


.PHONY: help


help:
	@echo "namesdb-public Install Helper"
	@echo ""
	@echo "Most commands have subcommands (ex: install-ddr-cmdln, restart-supervisor)"
	@echo ""
	@echo "get     - Clones namesdb-public, wgets static files & ES pkg."
	@echo "install - Performs complete install. See also: make howto-install"
	@echo "test    - Run unit tests"
	@echo ""
	@echo "migrate - Init/update Django app's database tables."
	@echo ""
	@echo "branch BRANCH=[branch] - Switches namesdb-public and supporting repos to [branch]."
	@echo ""
	@echo "deb       - Makes a DEB package install file."
	@echo "remove    - Removes Debian packages for dependencies."
	@echo "uninstall - Deletes 'compiled' Python files. Leaves build dirs and configs."
	@echo "clean     - Deletes files created while building app, leaves configs."
	@echo ""

howto-install:
	@echo "HOWTO INSTALL"
	@echo "- Basic Debian netinstall"
	@echo "- edit /etc/network/interfaces"
	@echo "- reboot"
	@echo "- apt-get install openssh fail2ban ufw"
	@echo "- ufw allow 22/tcp"
	@echo "- ufw allow 80/tcp"
	@echo "- ufw enable"
	@echo "- apt-get install make"
	@echo "- adduser ddr"
	@echo "- git clone $(SRC_REPO_PUBLIC) $(INSTALL_NAMESDBPUBLIC)"
	@echo "- cd $(INSTALL_NAMESDBPUBLIC)/namesdbpublic"
	@echo "- make install"
	@echo "- [make branch BRANCH=develop]"
	@echo "- [make install]"
	@echo "- Place copy of 'ddr' repo in $(DDR_REPO_BASE)/ddr."
	@echo "- make migrate"
	@echo "- make restart"



get: get-namesdb-public

install: install-prep get-app install-app install-daemons install-configs

test: test-app

coverage: coverage-app

uninstall: uninstall-app uninstall-configs

clean: clean-app


install-prep: ddr-user install-core git-config install-misc-tools

ddr-user:
	-addgroup --gid=1001 ddr
	-adduser --uid=1001 --gid=1001 --home=/home/ddr --shell=/bin/bash --disabled-login --gecos "" ddr
	-addgroup ddr plugdev
	-addgroup ddr vboxsf
	printf "\n\n# ddrlocal: Activate virtualnv on login\nsource $(VIRTUALENV)/bin/activate\n" >> /home/ddr/.bashrc; \

install-core:
	apt-get --assume-yes install bzip2 curl gdebi-core git-core logrotate ntp p7zip-full wget

git-config:
	git config --global alias.st status
	git config --global alias.co checkout
	git config --global alias.br branch
	git config --global alias.ci commit

install-misc-tools:
	@echo ""
	@echo "Installing miscellaneous tools -----------------------------------------"
	apt-get --assume-yes install ack-grep byobu elinks htop mg multitail


install-daemons: install-nginx install-redis

install-nginx:
	@echo ""
	@echo "Nginx ------------------------------------------------------------------"
	apt-get --assume-yes remove apache2
	apt-get --assume-yes install nginx-light

remove-nginx:
	apt-get --assume-yes remove nginx-light

install-redis:
	@echo ""
	@echo "Redis ------------------------------------------------------------------"
	apt-get --assume-yes install redis-server

remove-redis:
	apt-get --assume-yes remove redis-server


install-virtualenv:
	@echo ""
	@echo "install-virtualenv -----------------------------------------------------"
	apt-get --assume-yes install python3-pip python3-venv
	python3 -m venv $(VIRTUALENV)
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) pip

 install-setuptools: install-virtualenv
	@echo ""
	@echo "install-setuptools -----------------------------------------------------"
	apt-get --assume-yes install python3-dev
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) setuptools

get-app: get-namesdb-public

install-app: install-virtualenv install-namesdb-public install-configs install-daemon-configs

test-app: test-namesdb-public

uninstall-app: uninstall-namesdb-public uninstall-configs uninstall-daemon-configs

clean-app: clean-namesdb-public


get-namesdb-public:
	@echo ""
	@echo "get-namesdb-public ---------------------------------------------------------"
	git pull

install-namesdb-public: install-setuptools mkdir-namesdb-public
	@echo ""
	@echo "install-namesdb-public -----------------------------------------------------"
	apt-get --assume-yes install sqlite3 supervisor
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) -r $(INSTALL_NAMESDBPUBLIC)/requirements.txt

mkdir-namesdb-public:
	@echo ""
	@echo "mkdir-namesdb-public --------------------------------------------------------"
# logs dir
	-mkdir $(LOG_BASE)
	chown -R ddr.ddr $(LOG_BASE)
	chmod -R 775 $(LOG_BASE)
# sqlite db dir
	-mkdir $(SQLITE_BASE)
	chown -R ddr.ddr $(SQLITE_BASE)
	chmod -R 775 $(SQLITE_BASE)
# media dir
	-mkdir -p $(MEDIA_BASE)
	-mkdir -p $(MEDIA_ROOT)
	chown -R ddr.ddr $(MEDIA_ROOT)
	chmod -R 755 $(MEDIA_ROOT)

test-namesdb-public: test-namesdb-public-ui test-namesdb-public-names

test-namesdb-public-ui:
	@echo ""
	@echo "test-namesdb-public-ui ----------------------------------------"
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALL_NAMESDBPUBLIC); python namessite/manage.py test ui

test-namesdb-public-names:
	@echo ""
	@echo "test-namesdb-public-names ----------------------------------------"
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALL_NAMESDBPUBLIC); python namessite/manage.py test names

shell:
	source $(VIRTUALENV)/bin/activate; \
	python namessite/manage.py shell

runserver:
	source $(VIRTUALENV)/bin/activate; \
	python namessite/manage.py runserver 0.0.0.0:8000

uninstall-namesdb-public: install-setuptools
	@echo ""
	@echo "uninstall-namesdb-public ---------------------------------------------------"
	source $(VIRTUALENV)/bin/activate; \
	pip3 uninstall -y -r $(INSTALL_NAMESDBPUBLIC)/requirements.txt

clean-namesdb-public:
	-rm -Rf $(VIRTUALENV)
	-rm -Rf *.deb


get-ddr-public-assets:
	@echo ""
	@echo "get-ddr-public-assets --------------------------------------------------"
	if test -d $(INSTALL_ASSETS); \
	then cd $(INSTALL_ASSETS) && git pull; \
	else cd $(INSTALL_NAMESDBPUBLIC) && git clone $(SRC_REPO_ASSETS); \
	fi


migrate:
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALL_NAMESDBPUBLIC) && python namessite/manage.py migrate --noinput
	chown -R ddr.ddr $(SQLITE_BASE)
	chmod -R 770 $(SQLITE_BASE)
	chown -R ddr.ddr $(LOG_BASE)
	chmod -R 775 $(LOG_BASE)


install-configs:
	@echo ""
	@echo "configuring namesdb-public -------------------------------------------------"
# base settings file
# /etc/ddr/namesdbpublic.cfg must be readable by all
# /etc/ddr/namesdbpublic-local.cfg must be readable by ddr but contains sensitive info
	-mkdir /etc/ddr
	cp $(INSTALL_NAMESDBPUBLIC)/conf/namesdbpublic.cfg $(CONF_PRODUCTION)
	chown root.root $(CONF_PRODUCTION)
	chmod 644 $(CONF_PRODUCTION)
	touch $(CONF_LOCAL)
	chown ddr.root $(CONF_LOCAL)
	chmod 640 $(CONF_LOCAL)

uninstall-configs:
	-rm $(SETTINGS)
	-rm $(CONF_PRODUCTION)
	-rm $(CONF_SECRET)


install-daemon-configs:
	@echo ""
	@echo "install-daemon-configs -------------------------------------------------"
# nginx settings
	cp $(INSTALL_NAMESDBPUBLIC)/conf/nginx.conf $(NGINX_CONF)
	chown root.root $(NGINX_CONF)
	chmod 644 $(NGINX_CONF)
	-ln -s $(NGINX_CONF) $(NGINX_CONF_LINK)
	-rm /etc/nginx/sites-enabled/default
# supervisord
	cp $(INSTALL_NAMESDBPUBLIC)/conf/supervisor.conf $(SUPERVISOR_GUNICORN_CONF)
	chown root.root $(SUPERVISOR_GUNICORN_CONF)
	chmod 644 $(SUPERVISOR_GUNICORN_CONF)

uninstall-daemon-configs:
	-rm $(NGINX_CONF)
	-rm $(NGINX_CONF_LINK)
