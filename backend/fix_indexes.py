import glob

for file in glob.glob("app/models/*.py"):
    with open(file, "r") as f:
        content = f.read()
    content = content.replace(", index=True, index=True", ", index=True")
    with open(file, "w") as f:
        f.write(content)
