# DELTA-X v2 — release checks. Nothing here calls a model or spends a token.
PY      ?= python3
WORK    ?= $(HOME)/delta-x-runs
TMP     := $(CURDIR)/.make-tmp
BASE    := grader/baselines/BASELINE-v3-tooled

.PHONY: help check compile selftest digests scorecards aggregate smoke prompts clean

help:
	@echo "make check       compile + self-tests + stimulus digests + scorecards + aggregation"
	@echo "make smoke       full pipeline end to end with the stub adapter (no model, no tokens)"
	@echo "make prompts     compose the six prompts into .make-tmp and print their digests"
	@echo "make digests     verify the composed prompts still match the published campaign"
	@echo "make scorecards  run grader/check_scorecard.py over every published scorecard"
	@echo "make aggregate   run analysis/aggregate.py over the published campaign"
	@echo "make clean       remove .make-tmp"
	@echo
	@echo "To run a real campaign:  harness/run_campaign.sh --run-id run1 --adapter claude_code"

check: compile selftest digests scorecards aggregate
	@echo
	@echo "all checks passed"

compile:
	@echo "== compiling =="
	@$(PY) -m py_compile harness/*.py harness/adapters/*.py grader/*.py analysis/*.py
	@for f in harness/*.sh harness/adapters/*.sh env/*.sh; do bash -n "$$f" || exit 1; done
	@$(PY) -c "import json; json.load(open('grader/rubric/items.json'))"
	@$(PY) -c "import json; d=json.load(open('grader/rubric/items.json')); \
	           t=sum(i['max'] for i in d['items']); assert t==d['total'], t; print('   rubric sums to', t)"
	@echo "   ok"

selftest:
	@echo "== adapter self-test =="
	@$(PY) -I harness/adapters/openai_agent.py --self-test | tail -1

digests: prompts
	@echo "== stimulus digests vs the published campaign =="
	@fail=0; for s in s1 s2 s2b s3 s4 s5; do \
	  a=$$(sha256sum $(TMP)/prompts/$$s.txt | cut -d' ' -f1); \
	  b=$$(grep "prompts/$$s.txt" $(BASE)/STIMULUS.txt | cut -d' ' -f1); \
	  if [ "$$a" = "$$b" ]; then echo "   $$s  match"; \
	  else echo "   $$s  DIFFERS  composed=$$a  published=$$b"; fail=1; fi; done; \
	if [ $$fail = 1 ]; then \
	  echo "   The harness no longer composes the stimulus the published campaign was measured on."; \
	  echo "   If that is intended, record the new digests and name the campaign they belong to."; \
	  exit 1; fi

prompts:
	@mkdir -p $(TMP)/prompts
	@$(PY) -I harness/build_prompts.py --repo . --out $(TMP)/prompts 2>/dev/null

scorecards:
	@echo "== scorecards reconcile =="
	@fail=0; for f in $(BASE)/scorecards/scorecard_*.json; do \
	  if $(PY) -I grader/check_scorecard.py "$$f" >/dev/null 2>&1; \
	    then echo "   $$(basename $$f)  publishable"; \
	    else echo "   $$(basename $$f)  UNGRADED"; fail=1; fi; done; \
	exit $$fail

aggregate:
	@echo "== aggregation =="
	@$(PY) -I analysis/aggregate.py $(BASE)/scorecards --label BASELINE-v3-tooled | sed -n '1,14p'

smoke:
	@echo "== offline pipeline check: driver -> collect -> audit -> digest =="
	@rm -rf $(TMP)/runs
	@bash harness/run_campaign.sh --run-id smoke --adapter stub --work $(TMP)/runs --stages s1,s2,s2b
	@$(PY) -I harness/collect_submission.py $(TMP)/runs/smoke --out $(TMP)/smoke-submission
	@$(PY) -I harness/audit_containment.py  $(TMP)/runs/smoke
	@$(PY) -I harness/harness_digest.py     $(TMP)/runs/smoke
	@echo "   the stub's artifacts are not a submission; this checks plumbing only"

clean:
	@rm -rf $(TMP)
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
