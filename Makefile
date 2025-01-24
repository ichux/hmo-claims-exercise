# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help: hmo-claims-exercise Makefile help
# help:

.PHONY: help
# help: help				- Please use "make <target>" where <target> is one of
help:
	@grep "^# help\:" Makefile | sed 's/\# help\: //' | sed 's/\# help\://'

.PHONY: upgrade
# help: upgrade				- run upgrade
upgrade:
	@rm -f instance/intron_db.db; flask db upgrade

.PHONY: sql
# help: sql				- free data
sql:
	@cat rawsql.sql | sqlite3 instance/intron_db.db

.PHONY: run
# help: run				- run app
run:
	@flask run

.PHONY: test
# help: test				- run tests
test:
	@python3 -m unittest app/home/test_views.py
