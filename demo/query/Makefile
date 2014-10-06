# Whatever it is you want to do other run demos, it should be forwarded to the
# to the top-level directory
.PHONY: all
all: demos

#! Run all dataset demos
demos:
	@echo "Running all query demo programs...."; \
	for demo in *.py ; do \
	  echo "===================================="; \
	  echo Running demo $$demo; \
	  echo "===================================="; \
	  python $$demo; \
	done

%:
	$(MAKE) -C ../.. $@
