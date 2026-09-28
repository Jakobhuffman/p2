.PHONY: all clean

ifeq ($(OS),Windows_NT)
all:
	@echo Windows detected - no chmod needed for local testing
else
all:
	chmod +x graph
endif

clean:
ifeq ($(OS),Windows_NT)
	-del /Q *.dot 2>NUL
else
	rm -f *.dot
endif
