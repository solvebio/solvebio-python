# Whatever it is you want to do other run demos, it should be forwarded to the
# to top-level irectories
.PHONY: all
all: demos

#! Run all demos
demos:
	@echo "Running all demo programs...."; \
	for demo in *.py ; do \
	  echo "===================================="; \
	  echo Running demo $$demo; \
	  echo "===================================="; \
	  python $$demo; \
	done; \
	for dir in dataset depository query; do \
	  $(MAKE) -C $$dir demos; \
	done;

%:
	$(MAKE) -C .. $@
