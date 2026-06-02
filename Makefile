SKILLS_DIR := skills
DIST_DIR   := dist
SHARED_DIR := shared

SKILLS := $(notdir $(wildcard $(SKILLS_DIR)/*))

.PHONY: all clean pack list

all: $(SKILLS:%=$(DIST_DIR)/%.skill)

$(DIST_DIR)/%.skill: $(SKILLS_DIR)/%
	@mkdir -p $(DIST_DIR)
	@echo "Packing $*..."
	@tmp=$$(mktemp -d) && \
	  cp -r $< $$tmp/$* && \
	  mkdir -p $$tmp/$*/references && \
	  cp $(SHARED_DIR)/*.md $$tmp/$*/references/ 2>/dev/null; \
	  cd $$tmp && zip -qr $(CURDIR)/$@ $* --exclude "*.DS_Store" && \
	  rm -rf $$tmp
	@echo "  → $@"

pack:
	@test -n "$(SKILL)" || (echo "Usage: make pack SKILL=<skill-name>"; exit 1)
	@$(MAKE) $(DIST_DIR)/$(SKILL).skill

clean:
	rm -rf $(DIST_DIR)

list:
	@echo $(SKILLS) | tr ' ' '\n'
