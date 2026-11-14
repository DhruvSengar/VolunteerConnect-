VolunteerConnect

Volunteer and Community Service Coordination Platform (Idea 22) Full Stack Development Lab (24B15CS314) | B.Tech CSE, 5th Semester | JIIT, Noida

Team
Ridhi Kapoor
Lakshya Saxena
Dhruv Sengar
Khushi Gupta
Features
Role-based authentication (volunteers, organizations, coordinators)
Organization and volunteer profiles
Opportunities tagged by cause, with volunteer sign-ups
Hour logging, reviews, milestones and certificates
AJAX interactions using vanilla JS and the Fetch API
CSV and PDF reporting (ReportLab)
Tech Stack

Django 5.2, SQLite, HTML/CSS, vanilla JavaScript, ReportLab

Setup (Windows / PowerShell)
powershell
git clone <repo-url>
cd <repo-folder>
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Open http://127.0.0.1:8000/

Project Structure
volunteerconnect/   project settings and root URLs
accounts/           users, organizations, volunteer profiles
core/               causes, opportunities, sign-ups, hours, reviews, certificates, milestones
reports/            CSV/PDF reporting views
templates/          HTML templates
static/             CSS and JS
Notes

db.sqlite3 is not committed. python manage.py migrate recreates it, including the seeded milestones.