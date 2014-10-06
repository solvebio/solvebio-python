# Whatever it is you want to do other run demos, it should be forwarded to the
# to top-level irectories
.PHONY: all
all: demos

#! Run all depository demos
demos:
	@echo "Running all depository demo programs...."; \
	for demo in *.py ; do \
	  echo "===================================="; \
	  echo Running demo $$demo; \
	  echo "===================================="; \
	  python $$demo; \
	done;

%:
	$(MAKE) -C .. $@
