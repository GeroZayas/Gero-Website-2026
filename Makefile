run:
	clear && python3 main.py

generate-blog-posts-files:
	python3 -m services.markdown_html_factory.generate_html_blog_posts

db:
	python3 -m services.db.db

git:
	git add -A && \
	printf "message: "; \
	read MESSAGE; \
	git commit -m "$$MESSAGE" && \
	git push


help:
	@cat Makefile

scratch:
	python3 scratch_buffer.py