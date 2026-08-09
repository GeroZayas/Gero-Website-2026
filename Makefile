run:
	python3 main.py


git:
	git add -A && \
	printf "message: "; \
	read MESSAGE; \
	git commit -m "$$MESSAGE" && \
	git push