# AHMS Team Setup Guide

## Part 1: Setup checklist (tick each one when it works)
1. Clone the repo: `git clone https://github.com/<username>/ahms.git` (copies the project to your computer)
2. Go into the folder: `cd ahms`
3. Create a venv: `python -m venv venv` (a private space for this project's libraries)
4. Activate it: Windows `venv\Scripts\activate`, Mac/Linux `source venv/bin/activate` (you should see (venv) in the terminal)
5. Install libraries: `pip install -r requirements.txt`
6. Copy the settings file: Windows `copy .env.example .env`, Mac/Linux `cp .env.example .env` (never share or commit .env)
7. Create the database: `python manage.py migrate`
8. Run the server: `python manage.py runserver`, then open http://127.0.0.1:8000
9. Run the tests: `pytest` (all tests should pass)
If something fails, copy the full error message into the group chat. Do not skip steps.

## Part 2: Git practice (each member, once)
Use your own name in the branch name, for example practice/ahsan.
1. `git pull origin main` (downloads new changes)
2. `git checkout -b practice/yourname` (makes your own line of work so you do not touch main)
3. Add one line to docs/practice.txt: Hello from <your name> (create the file if it does not exist)
4. `git status` (shows which files you changed)
5. `git add docs/practice.txt` (picks the file to save)
6. `git commit -m "Add practice line from yourname"` (saves the change with a short note)
7. `git push origin practice/yourname` (sends your branch to GitHub)
8. On GitHub click Compare & pull request, write one line, and click Create pull request
9. Review a teammate's pull request: Files changed, then Review changes, then Approve
10. After one approval click Merge pull request, then Confirm merge
11. `git checkout main` then `git pull origin main` (brings the merged work back to your computer)

## Done when
- All four members run the app locally and pytest passes.
- All four opened one practice pull request, each reviewed by a different member.
- docs/practice.txt on main has four lines.
- Nobody committed .env or db.sqlite3.
