from os import listdir, remove
with open("used_posts.json", "w", encoding="utf-8") as f:
    f.write(r'{"hi":"hi"}')
for file in listdir("output"):
    remove("output/" + file)
