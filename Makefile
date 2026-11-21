run:
	python3 main.py

generate-blog-posts-files:
	python3 -m services.markdown_html_factory.generate_html_blog_posts

git:
	git add -A && \
	printf "message: "; \
	read MESSAGE; \
	git commit -m "$$MESSAGE" && \
	git push