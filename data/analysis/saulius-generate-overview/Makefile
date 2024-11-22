# --*- Makefile -*-------------------------------------------------------------
#$Author: vantanas $
#$Date: 2024-04-09 14:56:12 +0300 (Tue, 09 Apr 2024) $
#$Revision: 353 $
#$URL: svn+ssh://saulius-grazulis.lt/home/saulius/svn-repositories/makefiles/Makefile-backbone $
#------------------------------------------------------------------------------
#*
# Include all local Make files (Makelocal*, see the patterns below),
# and all local Make configuration files. All targets from these files
# will become available for the 'make' command.
#
# USAGE:
#    # builds prerequisites of every 'all' targets in every Makelocal* file:
#    make
#    make all
#
#    # cleans all generated files using every 'Makelocal*' file's rules:
#    make clean
#    make distclean
#
# Dependencies: needs GNU Make or compatible Make system.
#**

MAKEFILE_DIRS = . makefiles/enabled
MAKEFILE_WCARDS = $(addsuffix /Makelocal*, ${MAKEFILE_DIRS})
MAKECONF_WCARDS = $(addsuffix /Makeconf*, ${MAKEFILE_DIRS})

MAKECONF_FILES = $(sort $(filter-out %.example, \
	$(filter-out %~, $(wildcard $(MAKECONF_WCARDS)) \
)))

ifneq ("${MAKECONF_FILES}","")
include ${MAKECONF_FILES}
endif

.PHONY: all clean distclean cleanAll

all:

clean:

cleanAll distclean: clean

MAKELOCAL_FILES = $(sort $(filter-out %~, $(wildcard $(MAKEFILE_WCARDS))))

ifneq ("${MAKELOCAL_FILES}","")
include ${MAKELOCAL_FILES}
endif
