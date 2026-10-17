.PHONY: realign machine

realign: machine
	@chmod +x compile_all.sh
	@./compile_all.sh

machine:
	@chmod +x compile_all.sh
	@./compile_all.sh

.PHONY: constitution
constitution:
	python3 scripts/constitution.py new
	python3 scripts/constitution.py validate apex/RECORD.template.json
