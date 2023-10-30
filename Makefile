minify:
	node_modules/.bin/minify poe/static/poe/css/poe.css > poe/static/poe/css/poe.min.css

watch:
	tailwindcss -i main/tailwind/input.css -o main/static/main/css/tailwind.css --watch

build:
	tailwindcss -i main/tailwind/input.css -o main/static/main/css/tailwind.css --build