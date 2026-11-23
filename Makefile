PYTHON ?= python3

.PHONY: check test sync
check:
	$(PYTHON) tools/check_repo.py

test:
	$(PYTHON) -m unittest discover -s tests -v

sync: check test
	@test "$$(git branch --show-current)" = main || { echo "Refusing: not on main"; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo "Refusing: commit or preserve local changes first"; exit 1; }
	git push origin main
