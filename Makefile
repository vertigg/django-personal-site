minify:
	node_modules/.bin/minify main/static/main/css/bootstrap.css > main/static/main/css/bootstrap.min.css
	node_modules/.bin/minify poe/static/poe/css/poe.css > poe/static/poe/css/poe.min.css

watch:
	tailwindcss -i main/tailwind/input.css -o main/static/main/css/main.css --watch

build:
	tailwindcss -i main/tailwind/input.css -o main/static/main/css/main.css --build