BIN := bin/pomodoro
SRC := $(shell find src -name '*.py')
PREFIX ?= $(HOME)/.local

.PHONY: build install clean

build: $(BIN)

$(BIN): $(SRC)
	mkdir -p bin
	python3 -m zipapp src -m "pomodoro.__main__:main" -p "/usr/bin/env python3" -o $(BIN)
	chmod +x $(BIN)

install: build
	install -Dm755 $(BIN) $(PREFIX)/bin/pomodoro

clean:
	rm -rf bin
