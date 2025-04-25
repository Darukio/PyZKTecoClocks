import markdown

# Lee el contenido del archivo Markdown
with open("README.md", "r", encoding="utf-8") as f:
    text = f.read()

# Convierte el contenido a HTML
html = markdown.markdown(text)

# Escribe el resultado en un archivo HTML
with open("README.html", "w", encoding="utf-8") as f:
    f.write(html)
