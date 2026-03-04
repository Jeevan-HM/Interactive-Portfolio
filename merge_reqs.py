import os

files = [
    "projects/AI-podcast/requirements.txt",
    "projects/FinBot/requirements.txt",
    "projects/Interactive-Portfolio/requirements.txt",
    "projects/Lawn-AI/YOLO_Image_Segmentation/requirements.txt",
    "projects/Lawn-AI/requirements.txt",
    "projects/Survey-Chat-Bot/requirements.txt",
    "requirements.txt",
]

all_reqs = []
for f in files:
    full_path = os.path.join("/Users/g1/Developer/Intuit", f)
    if os.path.exists(full_path):
        with open(full_path) as fp:
            all_reqs.extend(fp.read().splitlines())

req_dict = {}
for req in all_reqs:
    req = req.strip()
    if not req or req.startswith("#"):
        continue

    # Simple split
    parts = req.split("==")
    if len(parts) == 2:
        pkg, ver = parts[0].strip().lower(), parts[1].strip()
        if pkg not in req_dict:
            req_dict[pkg] = req
        else:
            if req_dict[pkg] != req:
                req_dict[pkg] = pkg  # remove version constraint on conflict
    else:
        pkg = req.lower().split()[0].split(">")[0].split("<")[0]
        req_dict[pkg] = req

with open("/Users/g1/Developer/Intuit/combined_requirements.txt", "w") as out:
    for pkg, line in req_dict.items():
        out.write(line + "\n")
