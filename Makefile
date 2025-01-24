# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help: hmo-claims-exercise Makefile help
# help:

.PHONY: help
# help: help				- Please use "make <target>" where <target> is one of
help:
	@grep "^# help\:" Makefile | sed 's/\# help\: //' | sed 's/\# help\://'

.PHONY: clean
# help: clean				- clean screen processes
clean:
	@echo "clean"
