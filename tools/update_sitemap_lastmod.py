"""Set <lastmod> in sitemap.xml from the date of each page's last git commit.

Run from the repo root after committing page changes:  python tools/update_sitemap_lastmod.py
Commits that touch many pages at once (favicon, footer, head tags) are site-wide
template changes, not content changes, so they are skipped.
"""
import re
import subprocess

SITE = "https://montegudauri.com"


def page_file(loc):
    path = loc[len(SITE):].strip("/")
    if path == "":
        return "index.html"
    if path in ("ka", "ru"):
        return path + "/index.html"
    return path + ".html"


SITEWIDE = 10  # a commit changing this many pages or more is a template change


def last_commit_date(path):
    log = subprocess.run(["git", "log", "--format=@%H %cs", "--name-only", "--", "*.html"],
                         capture_output=True, text=True, check=True).stdout
    for block in log.split("@")[1:]:
        lines = block.strip().splitlines()
        files = [l.strip() for l in lines[1:] if l.strip()]
        if path in files and len(files) < SITEWIDE:
            return lines[0].split()[1]
    return ""


raw = open("sitemap.xml", "rb").read().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
text = raw.replace("\r\n", "\n")
text = re.sub(r"\n\s*<lastmod>[^<]*</lastmod>", "", text)


def add(m):
    loc = m.group(1)
    date = last_commit_date(page_file(loc))
    if not date:
        return m.group(0)
    return m.group(0) + "\n    <lastmod>%s</lastmod>" % date


text = re.sub(r"<loc>([^<]+)</loc>", add, text)
open("sitemap.xml", "wb").write(text.replace("\n", nl).encode("utf-8"))
