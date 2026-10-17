.PHONY: realign machine

realign: machine
	@chmod +x compile_all.sh
	@./compile_all.sh

machine:
	@chmod +x compile_all.sh
	@./compile_all.sh
