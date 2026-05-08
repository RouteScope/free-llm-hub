.PHONY: all fix merge validate render verify install clean stats pipeline clean-all

all: pipeline

pipeline:
	@printf "\n▶ 1/4 Fixing missing websites...\n"
	@python scripts/fix_websites.py
	@printf "\n▶ 2/4 Merging YAML files...\n"
	@./scripts/merge.sh
	@printf "\n▶ 3/4 Validating...\n"
	@python scripts/validate.py
	@printf "\n▶ 4/4 Rendering README...\n"
	@python scripts/render_readme.py
	@printf "\n✅ Done!\n"

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

fix:
	@python scripts/fix_websites.py

merge:
	@./scripts/merge.sh

validate:
	@python scripts/validate.py

render:
	@python scripts/render_readme.py

verify:
	@python scripts/verify_endpoints.py

stats:
	@python scripts/validate.py 2>&1 | tail -30

clean:
	@rm -rf data/hub.yaml data/verified.json README.md __pycache__
	@find . -name "*.pyc" -delete
	@echo "🧹 Cleaned"

clean-all: clean
	@rm -rf .venv
