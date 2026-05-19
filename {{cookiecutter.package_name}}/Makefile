SHELL := /bin/bash
ROOT  := $(shell pwd)

# robot_agent and pyconnect are expected as sibling repos by default.
# Override on the command line if your layout differs:
#   make install ROBOT_AGENT_DIR=/path/to/robot_agent PYCONNECT_DIR=/path/to/pyconnect
ROBOT_AGENT_DIR ?= $(ROOT)/{{cookiecutter.robot_agent_relpath}}
PYCONNECT_DIR   ?= $(ROOT)/{{cookiecutter.pyconnect_relpath}}

ROS_SETUP ?= /opt/ros/humble/setup.bash

# Server port — override on the command line: make run PORT=8002
PORT ?= {{cookiecutter.default_port}}

.PHONY: install install-deps run terminate doctor new-skill test clean help

help:
	@echo "{{cookiecutter.package_name}} -- {{cookiecutter.description}}"
	@echo ""
	@echo "Targets:"
	@echo "  make install                          Editable-install {{cookiecutter.package_name}} (+ pyconnect, robot_agent if missing)"
	@echo "  make install-deps                     Install pyconnect + robot_agent only"
	@echo "  make doctor                           Pre-flight check (verifies env, ROS2, skill imports)"
	@echo "  make run                              Start the agent (PORT=$(PORT))"
	@echo "  make terminate                        Stop the agent listening on PORT=$(PORT)"
	@echo "  make new-skill SKILL=<name> [FILE=<file>]"
	@echo "                                        Scaffold a new skill (creates/appends file + updates skills_config)"
	@echo "  make test                             Smoke test: list skills via curl"
	@echo "  make clean                            Remove __pycache__ and *.egg-info"

install-deps:
	@if [ -d "$(PYCONNECT_DIR)" ]; then \
		pip install -e $(PYCONNECT_DIR); \
	else \
		echo "[{{cookiecutter.package_name}}] pyconnect not found at $(PYCONNECT_DIR) -- skipping"; \
	fi
	@if [ -d "$(ROBOT_AGENT_DIR)" ]; then \
		pip install -e $(ROBOT_AGENT_DIR); \
	else \
		echo "[{{cookiecutter.package_name}}] robot_agent not found at $(ROBOT_AGENT_DIR) -- skipping"; \
	fi

install: install-deps
	pip install -e $(ROOT)
	@echo ""
	@echo "[{{cookiecutter.package_name}}] Installed. Run with: make run"

run:
	source $(ROS_SETUP) && \
	cd $(ROOT) && \
	uvicorn {{cookiecutter.package_name}}.main:app --host 0.0.0.0 --port $(PORT) --reload

# Kill whatever is listening on $(PORT): SIGTERM, wait 3s, then SIGKILL if alive.
terminate:
	@pids=$$(lsof -t -i tcp:$(PORT) -sTCP:LISTEN 2>/dev/null); \
	if [ -z "$$pids" ]; then \
		echo "[{{cookiecutter.package_name}}] nothing listening on port $(PORT)"; \
		exit 0; \
	fi; \
	echo "[{{cookiecutter.package_name}}] SIGTERM -> PID(s): $$pids"; \
	kill -TERM $$pids 2>/dev/null || true; \
	for i in 1 2 3; do \
		sleep 1; \
		pids=$$(lsof -t -i tcp:$(PORT) -sTCP:LISTEN 2>/dev/null); \
		[ -z "$$pids" ] && break; \
	done; \
	if [ -n "$$pids" ]; then \
		echo "[{{cookiecutter.package_name}}] still alive after 3s, SIGKILL -> $$pids"; \
		kill -KILL $$pids 2>/dev/null || true; \
		sleep 1; \
	fi; \
	pids=$$(lsof -t -i tcp:$(PORT) -sTCP:LISTEN 2>/dev/null); \
	if [ -z "$$pids" ]; then \
		echo "[{{cookiecutter.package_name}}] port $(PORT) is free"; \
	else \
		echo "[{{cookiecutter.package_name}}] WARNING: port $(PORT) still occupied by: $$pids"; \
		exit 1; \
	fi

doctor:
	@source $(ROS_SETUP) 2>/dev/null || true; \
	python3 -m robot_agent.diagnose {{cookiecutter.package_name}} $(ROOT)/{{cookiecutter.package_name}}/data $(ARGS)

# Scaffold a new skill. SKILL is required; FILE defaults to <SKILL>.py.
#   make new-skill SKILL=wave
#   make new-skill SKILL=rotate FILE=arm.py
new-skill:
	@if [ -z "$(SKILL)" ]; then \
		echo "Usage: make new-skill SKILL=<skill_name> [FILE=<file>]"; \
		exit 2; \
	fi
	python3 -m robot_agent.new_skill {{cookiecutter.package_name}} $(SKILL) $(FILE)

test:
	@echo "[{{cookiecutter.package_name}}] Registered skills:"
	@curl -s http://localhost:$(PORT)/skills | python3 -m json.tool | head -40

clean:
	find $(ROOT) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(ROOT) -type d -name "*.egg-info"  -exec rm -rf {} + 2>/dev/null || true
	@echo "[{{cookiecutter.package_name}}] cleaned."
