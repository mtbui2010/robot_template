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

.PHONY: install install-deps run cli terminate doctor skill-generic skill-detect delete-skill test clean help

help:
	@echo "{{cookiecutter.package_name}} -- {{cookiecutter.description}}"
	@echo ""
	@echo "Targets:"
	@echo "  make install                          Editable-install {{cookiecutter.package_name}} (+ pyconnect, robot_agent if missing)"
	@echo "  make install-deps                     Install pyconnect + robot_agent only"
	@echo "  make doctor                           Pre-flight check (verifies env, ROS2, skill imports)"
	@echo "  make run                              Start the UI/HTTP agent (PORT=$(PORT))"
	@echo "  make cli ARGS=\"<skill>[::<inputs>] [k=v ...]\""
	@echo "                                        Run one skill via CLI (sources ROS, no server)"
	@echo "                                        e.g.  make cli ARGS=\"find::apple\""
	@echo "                                              make cli ARGS=\"--list\""
	@echo "  make terminate                        Stop the agent listening on PORT=$(PORT)"
	@echo "  make skill-generic SKILL=<name> [FILE=<file>]"
	@echo "                                        Scaffold a generic skill stub (creates/appends file + updates skills_config)"
	@echo "  make skill-detect  SKILL=<name> [FILE=<file>]"
	@echo "                                        Scaffold a detect-style skill (mock _fetch_data + detector client call)"
	@echo "  make delete-skill  SKILL=<name> [YES=1]"
	@echo "                                        Remove a skill from skills_config and from its file."
	@echo "                                        If that file holds only this skill, the whole file is deleted."
	@echo "                                        Prompts for confirmation unless YES=1."
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

# Run one skill via the CLI; sources ROS first.
# Pass everything verbatim via ARGS:
#   make cli ARGS="find::apple"
#   make cli ARGS="find::apple count=3 verbose=true"
#   make cli ARGS="--list"
cli:
	@source $(ROS_SETUP) && \
	cd $(ROOT) && \
	python3 -m {{cookiecutter.package_name}} $(ARGS)

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
#   make skill-generic SKILL=wave
#   make skill-generic SKILL=rotate FILE=arm.py
skill-generic:
	@if [ -z "$(SKILL)" ]; then \
		echo "Usage: make skill-generic SKILL=<skill_name> [FILE=<file>]"; \
		exit 2; \
	fi
	python3 -m robot_agent.new_skill {{cookiecutter.package_name}} $(SKILL) $(FILE) --template generic

# Scaffold a detect-style skill (mocks _fetch_data + detector TCP client call).
#   make skill-detect SKILL=find_apple
#   make skill-detect SKILL=find_apple FILE=detectors.py
skill-detect:
	@if [ -z "$(SKILL)" ]; then \
		echo "Usage: make skill-detect SKILL=<skill_name> [FILE=<file>]"; \
		exit 2; \
	fi
	python3 -m robot_agent.new_skill {{cookiecutter.package_name}} $(SKILL) $(FILE) --template detect

# Remove a skill. Prompts for confirmation; pass YES=1 to skip the prompt.
#   make delete-skill SKILL=wave
#   make delete-skill SKILL=wave YES=1
# If the target file holds only this skill, the entire file is deleted.
# Otherwise only `def <skill>` is spliced out.
delete-skill:
	@if [ -z "$(SKILL)" ]; then \
		echo "Usage: make delete-skill SKILL=<skill_name> [YES=1]"; \
		exit 2; \
	fi
	@if [ "$(YES)" = "1" ]; then \
		python3 -m robot_agent.delete_skill {{cookiecutter.package_name}} $(SKILL) --yes; \
	else \
		python3 -m robot_agent.delete_skill {{cookiecutter.package_name}} $(SKILL); \
	fi

test:
	@echo "[{{cookiecutter.package_name}}] Registered skills:"
	@curl -s http://localhost:$(PORT)/skills | python3 -m json.tool | head -40

clean:
	find $(ROOT) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(ROOT) -type d -name "*.egg-info"  -exec rm -rf {} + 2>/dev/null || true
	@echo "[{{cookiecutter.package_name}}] cleaned."
