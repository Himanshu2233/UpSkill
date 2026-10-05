"""Generate the JobTrack internship report; optional dependencies: python-docx, Pillow."""
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'report'
OUT.mkdir(parents=True, exist_ok=True)
GREEN = '167761'
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.top_margin = section.bottom_margin = Inches(1)
section.left_margin, section.right_margin = Inches(1), Inches(.9375)
section.header_distance, section.footer_distance = Inches(.3), Inches(.5)
section.different_first_page_header_footer = True
normal = doc.styles['Normal']
normal.font.name, normal.font.size = 'Arial', Pt(11)
normal.paragraph_format.line_spacing = 1.15
normal.paragraph_format.space_after = Pt(8)
for name, size in [('Heading 1', 16), ('Heading 2', 12), ('Heading 3', 11)]:
    style = doc.styles[name]
    style.font.name, style.font.size = 'Arial', Pt(size)
    style.font.color.rgb = RGBColor.from_string(GREEN)
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.space_before = Pt(12)
    style.paragraph_format.space_after = Pt(8)
doc.styles['Heading 1'].paragraph_format.page_break_before = True
doc.styles['Caption'].font.name = 'Arial'
doc.styles['Caption'].font.size = Pt(9)
doc.styles['Caption'].font.color.rgb = RGBColor.from_string('596A65')
doc.core_properties.title = 'Industrial Internship Report: JobTrack'
doc.core_properties.subject = 'Python Development - Flask Job Application Tracker'
doc.core_properties.author = '[Student name]'
doc.core_properties.keywords = 'Python, Flask, internship, JobTrack, SQLite'


def field(paragraph, instruction):
    run = paragraph.add_run()
    begin = OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'), 'begin')
    text = OxmlElement('w:instrText'); text.set(qn('xml:space'), 'preserve'); text.text = instruction
    separate = OxmlElement('w:fldChar'); separate.set(qn('w:fldCharType'), 'separate')
    end = OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'), 'end')
    for element in (begin, text, separate, end): run._r.append(element)


header = section.header.paragraphs[0]
header.text = '[College name / logo]'
header.runs[0].font.size = Pt(9)
header.runs[0].font.color.rgb = RGBColor.from_string('596A65')
footer = section.footer.paragraphs[0]
footer.text = 'Industrial Internship Report | JobTrack'
footer.add_run('                                      Page ')
field(footer, ' PAGE ')
for r in footer.runs: r.font.size = Pt(9)
settings = doc.settings.element
update = OxmlElement('w:updateFields'); update.set(qn('w:val'), 'true'); settings.append(update)


def p(text, style=None):
    paragraph = doc.add_paragraph(text, style)
    if style is None:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return paragraph


def h(text, level=1):
    return doc.add_heading(text, level)


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    for cell, label in zip(t.rows[0].cells, headers):
        cell.text = label
        shade = OxmlElement('w:shd'); shade.set(qn('w:fill'), GREEN); cell._tc.get_or_add_tcPr().append(shade)
        for r in cell.paragraphs[0].runs: r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
    repeat = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for cell, text in zip(t.add_row().cells, row): cell.text = str(text)
    for row in t.rows:
        prevent = OxmlElement('w:cantSplit'); row._tr.get_or_add_trPr().append(prevent)
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(4)
                para.paragraph_format.space_before = Pt(4)
                for r in para.runs: r.font.size = Pt(9)
    if widths:
        t.autofit = False
        for row in t.rows:
            for cell, width in zip(row.cells, widths): cell.width = Inches(width)
    p('')
    return t


def bullet(text): p(text, 'List Bullet')


def code(text):
    paragraph = p(text)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.line_spacing = 1
    for r in paragraph.runs: r.font.name = 'Consolas'; r.font.size = Pt(9)


def figure(path, caption, max_height=6.2):
    with Image.open(path) as im:
        width = min(6.45, max_height * im.width / im.height)
    paragraph = p('')
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run().add_picture(str(path), width=Inches(width))
    caption_p = p(caption, 'Caption'); caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def diagram(filename, boxes, arrows, size=(1500, 920)):
    im = Image.new('RGB', size, 'white'); draw = ImageDraw.Draw(im)
    font_path = 'C:/Windows/Fonts/arial.ttf'
    font = ImageFont.truetype(font_path, 26)
    for bounds, text in boxes:
        draw.rounded_rectangle(bounds, radius=18, fill='#eff6f2', outline='#167761', width=3)
        lines = text.split('\n'); x1,y1,x2,y2 = bounds
        for i,line in enumerate(lines):
            bb = draw.textbbox((0,0), line, font=font)
            draw.text(((x1+x2-(bb[2]-bb[0]))/2, (y1+y2)/2-len(lines)*18+i*36),line,font=font,fill='#192b2b')
    for start,end,label in arrows:
        draw.line([start,end], fill='#167761', width=4)
        import math
        angle = math.atan2(end[1]-start[1],end[0]-start[0])
        draw.polygon([end,(end[0]-18*math.cos(angle-.45),end[1]-18*math.sin(angle-.45)),(end[0]-18*math.cos(angle+.45),end[1]-18*math.sin(angle+.45))],fill='#167761')
        if label:
            bb=draw.textbbox((0,0),label,font=font)
            draw.text(((start[0]+end[0]-(bb[2]-bb[0]))/2,(start[1]+end[1])/2-32),label,font=font,fill='#596a65')
    path=OUT/filename; im.save(path); return path


# Cover and front matter.
p('[College logo]', 'Subtitle').alignment = WD_ALIGN_PARAGRAPH.CENTER
p('\n\n')
for text,size,color in [('INDUSTRIAL INTERNSHIP REPORT',18,'192B2B'),('JobTrack',32,GREEN),('Flask Job Application Tracker',18,'192B2B'),('Python Development - Virtual Internship',12,'596A65')]:
    paragraph=p(text); paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=paragraph.runs[0]; run.bold=True; run.font.size=Pt(size); run.font.color.rgb=RGBColor.from_string(color)
p('\n')
for text in ['Prepared by', '[Student name]', '[Roll / registration number]', '[Course / department]', '[College / university]', '', 'Internship period: [Start date] to [End date]', 'Mentor / supervisor: [Mentor name]', 'Program / organization: [Confirmed internship provider]', 'Submission date: [Submission date]']:
    p(text).alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_page_break()
h('Executive Summary',2)
summary = ('JobTrack is a server-rendered web application developed as a Python development internship final project. It helps a user maintain job applications, update their progress, and identify upcoming deadlines. The project turns a practical organizational problem into a working application with account-based access and persistent storage.\n\n'
           'The implementation uses Flask, Jinja, Bootstrap, SQLite through Flask-SQLAlchemy, Flask-Login, and Flask-WTF. Users can register, log in, add or update an application, view notes, and confirm deletion. A dashboard presents total applications and counts for Applied, Interviewing, Offered, and Rejected, alongside company/title search, status filtering, and active deadlines.\n\n'
           'The system separates authentication and tracker features into blueprints and uses an application factory for configuration and test isolation. Passwords are hashed; application queries enforce ownership; forms validate input and include CSRF protection. The completed local project includes repeatable fictional demo data, setup instructions, screenshots, and a recorded browser walkthrough.\n\n'
           'Verification includes 18 passing pytest cases and browser workflow checks on desktop and mobile layouts. This report describes those functional results without treating them as load-testing evidence. The project is intended for a local internship demonstration; public hosting, notifications, and advanced analytics remain future work.')
table(['Project summary'],[(summary,)], [6.5])
p('Student details, internship dates, mentor details, and submission links are editable placeholders. The actual internship duration should be entered from the student’s records; the sample’s six-week duration is not assumed.')
doc.add_page_break()
h('TABLE OF CONTENTS',2)
# Supply readable cached content even in viewers that cannot update Word fields.
toc_p = p('')
toc_run = toc_p.add_run()
for tag, value in [('w:fldChar', 'begin'), ('w:instrText', ' TOC \\o "1-2" \\h \\z \\u '), ('w:fldChar', 'separate')]:
    element = OxmlElement(tag)
    if tag == 'w:fldChar': element.set(qn('w:fldCharType'), value)
    else: element.text = value; element.set(qn('xml:space'), 'preserve')
    toc_run._r.append(element)
toc_entries = [
    '1  Preface', '2  Introduction', '    2.1  About UniConverge Technologies Pvt Ltd',
    '    2.2  About upskill Campus (USC)', '    2.3  Objectives', '    2.4  References', '    2.5  Glossary',
    '3  Problem Statement', '    3.1  Functional requirements', '    3.2  Constraints and acceptance criteria',
    '4  Existing and Proposed solution', '    4.1  Existing approaches', '    4.2  Proposed solution and value addition', '    4.3  Code and report submission',
    '5  Proposed Design / Model', '    5.1  High Level Diagram', '    5.2  Low Level Diagram and database model', '    5.3  Interfaces', '    5.4  Implementation and local execution',
    '6  Performance Test', '    6.1  Test Plan / Test Cases', '    6.2  Test Procedure', '    6.3  Performance Outcome',
    '7  My learnings', '8  Future work scope']
for entry in toc_entries:
    toc_entry = p(entry)
    toc_entry.alignment = WD_ALIGN_PARAGRAPH.LEFT
    toc_entry.paragraph_format.space_after = Pt(5)
    if not entry.startswith(' '): toc_entry.runs[0].bold = True
toc_end = OxmlElement('w:fldChar'); toc_end.set(qn('w:fldCharType'), 'end')
toc_entry.add_run()._r.append(toc_end)
p('To refresh the contents with page numbers after editing, right-click this list in Microsoft Word and choose Update Field, then Update entire table.').runs[0].font.size = Pt(9)

h('1  Preface')
p('This report presents the design, implementation, and verification of JobTrack, a Flask-based job application tracker for a Python development virtual internship. The project connects Python programming with web development, relational data storage, secure user workflows, and software testing. Its purpose is to demonstrate a complete, understandable solution that can be run and reviewed locally.')
p('A practical internship project provides an opportunity to move beyond isolated programming exercises. JobTrack requires related decisions about data modeling, routes, forms, page layouts, authentication, and failure handling. The work also emphasizes communicating a solution through documentation and demonstration artifacts.')
p('The final-project work was organized into requirement definition, backend development, interface development, testing, and presentation preparation. A one-week project schedule was used as the planning target. The student’s full internship period is [Start date] to [End date]; any earlier training activities should be added from actual records.')
table(['Project stage','Deliverable'],[
('Requirement definition','Define user workflows, statuses, deadline rules, and local-demo scope.'),
('Backend development','Implement User/Application models, authentication, and application routes.'),
('Interface development','Build dashboard, forms, detail pages, confirmation pages, and responsive styling.'),
('Verification','Run isolated tests and desktop/mobile browser workflows.'),
('Presentation','Prepare README, screenshots, report, and demonstration recording.')],[1.6,4.9])
p('Acknowledgement: I would like to thank [Mentor name], [Faculty / coordinator name], and [Internship organization] for their guidance and the opportunity to complete a practical project. These names and acknowledgements should be finalized to reflect the actual support received.')
p('The project encourages students and peers to begin with a clear problem, implement a small set of complete workflows, and verify them before adding more features. A useful and reproducible application provides a stronger learning outcome than a large collection of unfinished screens.')

h('2  Introduction')
p('Job applications often involve several companies, role titles, posting links, deadlines, and interview notes. A dedicated tracker can bring these details into one place. JobTrack applies Python to this everyday problem through a web interface that requires no separate frontend framework or REST client.')
h('2.1  About UniConverge Technologies Pvt Ltd',2)
p('The supplied sample identifies UniConverge Technologies (UCT) as an industrial partner. UCT’s official website describes a company founded in 2013 with expertise in wireless communication, Internet of Things, product development, and consulting services [1]. This background provides context for an industry-oriented internship report; it does not establish that JobTrack is a commissioned or deployed UCT product.')
h('2.2  About upskill Campus (USC)',2)
p('The official upskill Campus industrial internship page describes an online internship program offered with industrial partner UniConverge Technologies [2]. The sample also identifies The IoT Academy as part of its program context. These organization references are retained to align with the sample; the student should replace [Confirmed internship provider] with the organization stated in their own offer letter.')
h('2.3  Objectives',2)
for text in ['Develop a complete Python web application that solves a clear organizational problem.','Learn Flask routes, blueprints, templates, forms, and the application factory pattern.','Store user and application data in a relational SQLite database.','Implement authentication and restrict each account to its own records.','Provide usable application management, search, status counts, and deadline visibility.','Verify workflows and document installation, demonstration, and limitations.']: bullet(text)
h('2.4  References',2)
refs=[
('[1]','UniConverge Technologies, About Us','https://www.uniconvergetech.in/about-us'),
('[2]','upskill Campus, Industrial Internship Program','https://learn.upskillcampus.com/s/pages/industrial-internships'),
('[3]','Flask, Application Setup','https://flask.palletsprojects.com/en/stable/tutorial/factory/'),
('[4]','Flask, Testing Flask Applications','https://flask.palletsprojects.com/en/stable/testing/'),
('[5]','Project source and local artifacts','README.md; requirements.txt; jobtrack/; tests/; docs/VALIDATION.md; docs/screenshots/'),
('[6]','Supplied report-format reference','Sample_InternshipReport_USC_UCT (1).docx')]
for number,title,url in refs: p(number+' '+title+'\n'+url)
p('Web references checked on 1 October 2026. Implementation details and version numbers in this report are taken from the local project; newer documentation may describe newer library releases.')
h('2.5  Glossary',2)
table(['Term / acronym','Meaning in this project'],[
('Flask','Python web framework handling requests, routes, and rendered responses.'),('CRUD','Create, read, update, and delete application records.'),('ORM','Object-relational mapping between Python models and database tables.'),('CSRF','Cross-site request forgery; token protection checks state-changing forms.'),('Blueprint','Flask module grouping related routes.'),('Jinja','Template engine rendering server-side HTML.'),('SQLite','File-based relational database used for local storage.'),('HTTP / HTTPS','Protocols permitted for an optional job-posting URL.'),('pytest','Test framework used for automated verification.'),('USC / UCT','upskill Campus / UniConverge Technologies.')],[1.1,5.4])

h('3  Problem Statement')
p('A student or early-career job seeker may apply for several positions and maintain the information in scattered notes, emails, or spreadsheets. Without a consistent workflow, it becomes difficult to find a posting link, check application progress, identify approaching deadlines, or prepare from previous interview notes.')
p('The problem addressed by JobTrack is to provide a single, account-based place to record these opportunities and review progress. The user should be able to maintain accurate data without needing database knowledge and should be prevented from accessing another account’s applications.')
h('3.1  Functional requirements',2)
table(['Requirement','Implemented behavior'],[
('Accounts','Register with email/password, log in, and log out.'),('Application management','Create, view, edit, and delete after confirmation.'),('Required data','Company, job title, application date, and one supported status.'),('Optional data','HTTP/HTTPS posting URL, deadline, and notes.'),('Dashboard','Total and per-status counts for the complete account.'),('Discovery','Company/title text search and optional status filter.'),('Deadline visibility','Today through seven days ahead; exclude Offered and Rejected.'),('Account isolation','Look up records by both application ID and current user ID.')],[1.5,5.0])
h('3.2  Constraints and acceptance criteria',2)
p('The implementation is sized for a one-week final-project effort and a local demonstration. It uses server-rendered pages and SQLite, avoiding the setup overhead of a separate frontend and database server. Application dates use the host machine’s local calendar date.')
p('A reviewer should be able to follow the README, initialize the database, register or use the fictional demo account, and complete application management without errors. Invalid forms should remain editable with feedback, and unauthorized record access should fail. The interface should fit desktop and mobile screens.')
p('Email reminders, AI functions, scraping, file uploads, and hosting are outside the implemented scope. No financial data, resumes, or real applicant documents are required for the demonstration.')

h('4  Existing and Proposed solution')
h('4.1  Existing approaches',2)
p('The following comparison describes typical workflow choices rather than a benchmark of commercial products. Notes and spreadsheets are easy to start but require manual organization; email folders retain correspondence but do not provide one structured application record. JobTrack focuses on a small, dedicated workflow suitable for demonstrating Python development.')
table(['Approach','Typical strength','Limitation for this workflow'],[
('Notes / documents','Flexible and quick to write.','Statuses, dates, and links are not consistently structured.'),('Spreadsheet','Can store rows and use filters.','Forms, authenticated ownership, and deadline logic require extra setup.'),('Email folders','Retain recruiter conversations.','Application details and next steps remain spread across messages.'),('JobTrack','Structured forms, account-specific records, dashboard, and deadlines.','Local-demo scope; no external integrations or notifications.')],[1.15,2.3,3.05])
h('4.2  Proposed solution and value addition',2)
p('JobTrack stores each application with an owning user and a consistent set of fields. The dashboard summarizes progress while the detail page preserves posting links and notes. Separate create/edit forms validate input before committing data. A dedicated confirmation page reduces accidental deletion.')
p('The main value is a complete workflow: capture an opportunity, review it, update progress, and prepare for deadlines. Summary counts remain account-wide even when the list is filtered. This prevents a filtered view from changing the user’s understanding of their overall application activity.')
h('4.3  Code and report submission',2)
table(['Submission item','Location / placeholder'],[
('Source repository','[GitHub project repository URL]'),('Report submission','[GitHub report URL / submission portal link]'),('Setup guide','README.md'),('Screenshots','docs/screenshots/'),('Walkthrough recording','docs/recordings/jobtrack-walkthrough.webm'),('Narration script','docs/DEMO.md')],[1.8,4.7])
p('The repository and submission URLs must be filled after publication. No public repository or external submission is claimed in this report.')

h('5  Proposed Design / Model')
h('5.1  High Level Diagram',2)
p('The browser sends requests to Flask. Authentication and tracker blueprints implement the routes; form classes validate submissions; SQLAlchemy reads and writes the SQLite database. Jinja templates and local Bootstrap/CSS files produce the user interface. Flask’s application factory initializes configuration and extensions [3].')
architecture=diagram('architecture.png',[
((450,30,1050,150),'User browser\nForms, links, dashboard'),
((450,240,1050,360),'Flask application factory\nConfiguration and extensions'),
((80,450,670,580),'Authentication blueprint\nRegister / login / logout'),
((830,450,1420,580),'Tracker blueprint\nCRUD / search / deadlines'),
((450,700,1050,830),'SQLAlchemy models + SQLite\nUser and Application tables')],
[((750,150),(750,240),'HTTP'),((590,360),(375,450),''),((920,360),(1125,450),''),((375,580),(590,700),''),((1125,580),(920,700),'')])
figure(architecture,'Figure 1. High-level architecture of JobTrack.',4.8)
p('Responses are server-rendered HTML; the project exposes no separate public REST API. Static styles are bundled locally for an offline-capable demonstration. The database and generated local secret key reside in the ignored instance directory.')
h('5.2  Low Level Diagram and database model',2)
data_model=diagram('database-model.png',[
((40,120,660,590),'USER\nid: integer primary key\nemail: unique, required\npassword_hash: required'),
((840,40,1460,790),'APPLICATION\nid: integer primary key\nuser_id: foreign key, indexed\ncompany: required (120)\ntitle: required (160)\nposting_url: optional (2048)\napplication_date: required date\ndeadline: optional date\nstatus: supported value\nnotes: text')],
[((660,350),(840,350),'1 : many')],size=(1500,830))
figure(data_model,'Figure 2. User-to-Application relationship and stored fields.',4.1)
p('One user can own many applications. The indexed user_id supports account-specific queries. A database check constraint limits statuses to Applied, Interviewing, Offered, and Rejected. Passwords are stored as PBKDF2-SHA256 hashes using Werkzeug; the original password is not stored.')
p('The dashboard selects the current user’s records, calculates total and status counts, and then applies search/status criteria to the displayed list. Applications are ordered by descending application date and ID. Upcoming deadlines are sorted by date and ID and include the two boundary dates, today and today plus seven days.')
p('For view, edit, and delete operations, the record lookup includes both the requested ID and current user ID. A missing or foreign-owned record produces HTTP 404. This same ownership check applies to GET and POST operations.')
workflow=diagram('application-flow.png',[
((450,20,1050,120),'Authenticated user submits form'),
((450,200,1050,310),'CSRF and form validation'),
((40,400,650,530),'Invalid input\nDisplay feedback; do not save'),
((850,400,1460,530),'Valid input\nCheck ownership when applicable'),
((850,620,1460,750),'Commit database transaction\nRedirect to detail or dashboard')],
[((750,120),(750,200),''),((590,310),(345,400),''),((920,310),(1155,400),''),((1155,530),(1155,620),'')],size=(1500,800))
figure(workflow,'Figure 3. Form submission and persistence flow.',4.1)
h('5.3  Interfaces',2)
table(['Method / path','Purpose'],[
('GET /','Protected dashboard; accepts q and status query parameters.'),('GET, POST /auth/register','Account registration form and submission.'),('GET, POST /auth/login','Login form and submission.'),('POST /auth/logout','CSRF-protected logout.'),('GET, POST /applications/new','Create an application.'),('GET /applications/<id>','Display an owned record.'),('GET, POST /applications/<id>/edit','Edit an owned record.'),('GET, POST /applications/<id>/delete','Show confirmation; delete on valid POST.')],[2.8,3.7])
p('Company and job title are trimmed and required. Email syntax and password length are validated, and registration requires matching passwords. Application dates must parse as valid calendar dates. Optional posting URLs require an HTTP or HTTPS scheme and hostname. Notes are limited to 10,000 characters by form validation.')
p('CSRF protection is enabled globally. Jinja escapes displayed user content, while job links open with noopener and noreferrer. Sessions use HttpOnly and SameSite=Lax cookies, and responses include no-store, nosniff, and SAMEORIGIN headers. These controls support the local workflow; no public deployment security review is claimed.')

for image,caption,description,height in [
('login-desktop.png','Figure 4. Login interface.','The authentication screen provides email/password login and a link to registration. Form errors remain visible next to invalid input.',4.8),
('dashboard-desktop.png','Figure 5. Desktop dashboard with fictional demo data.','The dashboard combines account-wide statistics, searchable application records, and the next seven days of active deadlines.',5.8),
('application-form-desktop.png','Figure 6. Application entry form.','The create/edit form captures company, role, posting URL, dates, status, and notes using labeled fields.',5.6),
('application-detail-desktop.png','Figure 7. Application details after editing.','The detail page displays dates, posting link, status, and notes, with explicit edit and delete actions.',4.8),
('delete-confirmation.png','Figure 8. Deletion confirmation.','The confirmation page supports both cancellation and a CSRF-protected deletion submission.',4.0),
('dashboard-mobile.png','Figure 9. Responsive dashboard at a 390-pixel viewport.','On smaller screens, statistic cards wrap and the deadline panel follows the application list. Browser checks found no document horizontal overflow.',6.0),
('empty-dashboard.png','Figure 10. New account with an empty dashboard.','A newly registered user sees an invitation to add an application and cannot see the demo account’s records.',4.8)]:
    doc.add_page_break(); p(description); figure(ROOT/'docs'/'screenshots'/image,caption,height)

h('5.4  Implementation and local execution',2)
table(['Component','Responsibility'],[
('Application factory / extensions','Configure database, session handling, login, and CSRF integrations.'),('Models / forms','Define persisted entities and validate submitted values.'),('Authentication blueprint','Register accounts, verify passwords, and manage sessions.'),('Tracker blueprint','Enforce ownership and implement CRUD/dashboard behavior.'),('Templates / static assets','Render the responsive interface with Jinja and local Bootstrap.'),('CLI / tests','Initialize database, seed fictional records, and verify behavior.')],[1.8,4.7])
p('Validated environment: Windows, Python 3.8.10, and Microsoft Edge. Direct dependency versions are Flask 3.0.3, Werkzeug 3.0.6, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.36, Flask-Login 0.6.3, Flask-WTF 1.2.1, WTForms 3.1.2, email-validator 2.2.0, pytest 8.3.5, and python-dotenv 1.0.1. Bootstrap 5.3.3 is bundled locally.')
p('A reviewer can run the project in PowerShell with the following commands. The virtual environment and database are created locally; initialization does not delete existing tables or records.')
code('python -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n.\\.venv\\Scripts\\python.exe -m flask --app jobtrack init-db\n.\\.venv\\Scripts\\python.exe -m flask --app jobtrack seed-demo\n.\\.venv\\Scripts\\python.exe -m flask --app jobtrack run')
p('Open http://127.0.0.1:5000. The fictional demo login is demo@jobtrack.example with password DemoPass123!. The seed command creates six applications only when the demo account is absent; rerunning preserves existing demo data. These credentials are demonstration data only.')
p('SECRET_KEY and DATABASE_URL may be configured through .env. If no key is provided, the application creates a persistent local key in instance/secret.key. The default database is instance/jobtrack.sqlite. Test configuration replaces this database with a temporary SQLite file.')

h('6  Performance Test')
p('The verification objective was to establish functional correctness, account isolation, and interface usability for a small local demonstration. The available results do not measure production throughput or latency. Functional test execution time is reported separately from application response time.')
h('6.1  Test Plan / Test Cases',2)
table(['Test group','Scenario and expected result','Observed'],[
('Authentication','Protected pages redirect; registration hashes passwords; valid login succeeds; invalid login fails.','Pass'),
('Registration validation','Reject malformed email, short password, mismatched confirmation, and duplicate email.','Pass'),
('CRUD / confirmation','Create, read, edit, cancel deletion, then confirm deletion; deleted URL returns 404.','Pass'),
('Field validation (9 cases)','Reject blank company/title, malformed dates, invalid URL forms, unsupported status, and overlong notes.','Pass'),
('Content safety','Accept optional HTTP/HTTPS link; escape script text in notes.','Pass'),
('Ownership','Second account cannot list, read, edit, or delete the first account’s records.','Pass'),
('Search / counts / dates','Verify search/filter, literal wildcard search, full-account counts, and deadline boundaries.','Pass'),
('CSRF','Reject tokenless registration, create, and logout; permit valid token registration.','Pass'),
('Empty/error pages','Show empty dashboard, deadline empty state, form page, and 404.','Pass'),
('CLI seeding','Initialize and rerun seed without duplicating demo users or applications.','Pass')],[1.15,4.7,.65])
p('The table groups related checks. The suite collects 18 pytest cases because field validation is parameterized into nine separate cases. This count is not a code-coverage percentage or a claim that every possible input was tested.')
h('6.2  Test Procedure',2)
p('Automated tests use the application factory with testing configuration, a temporary SQLite database, and a test client. Tables are created for each fixture and removed afterward. Most functional tests disable CSRF to focus on workflows; the dedicated CSRF test enables it and verifies both rejection and a valid token path. Flask’s test client supports this isolated approach [4].')
code('.\\.venv\\Scripts\\python.exe -m pytest -q')
p('The latest report-generation verification run completed with 18 tests passing in 7.41 seconds on the local environment. Test duration depends on the machine and password hashing overhead; it should not be presented as a web-response benchmark.')
p('Browser checks used headless Microsoft Edge and Playwright with a 1440 x 1000 desktop viewport and a 390 x 844 mobile viewport. The walkthrough performed demo login, combined search/filter, reset, creation, editing, deletion cancellation and confirmation, logout, registration, empty-state display, and direct cross-account URL rejection. It also captured screenshots and a silent video. No JavaScript page errors were observed.')
h('6.3  Performance Outcome',2)
table(['Measure / constraint','Result or limitation'],[
('Automated functional verification','18 passed; no failed cases in the latest run.'),('Dependency consistency','pip check reported no broken requirements in the validated environment.'),('Account isolation','Foreign-owned detail/edit/delete requests rejected in tests; browser read rejection also verified.'),('Responsive layout','No document horizontal overflow on tested dashboard/form at 390 x 844.'),('Demo data size','Six fictional seeded records; not a large-dataset benchmark.'),('Response latency / throughput','Not measured; no p95 latency or requests-per-second result is claimed.'),('Concurrency / production load','Not tested. SQLite and Flask development-server behavior were not load-benchmarked.')],[2.0,4.5])
p('The dashboard currently loads all of the account’s applications to calculate counts and deadlines, then queries the filtered list. This is understandable for a small internship demo but can become inefficient for large datasets. Pagination, database aggregation, and indexed deadline queries should be evaluated before scaling. A production database and WSGI server would be needed for a hosted version.')
p('The result supports a functioning local demonstration with verified core workflows. Further work should measure latency, memory use, concurrent access, and recovery behavior using a realistic dataset before making production-readiness claims.')

h('7  My learnings')
p('The completed project provides practical learning in connecting Python logic to a web interface and persistent data. The following learning summary is written for the student to review and personalize before submission.')
table(['Area','Learning demonstrated by the project'],[
('Python web development','Map requests to route functions and render HTML through Jinja templates.'),('Application organization','Use an application factory and blueprints instead of placing all features in one file.'),('Data modeling','Represent one-to-many ownership through User and Application tables.'),('Authentication / authorization','Understand the difference between being logged in and having permission to access a record.'),('Validation and safety','Validate dates/URLs, hash passwords, protect forms against CSRF, and escape user content.'),('Testing','Use isolated databases, parameterized invalid-input cases, and direct foreign-record requests.'),('Interface design','Provide useful empty states, explicit destructive-action confirmation, and responsive layouts.'),('Technical communication','Prepare reproducible setup instructions, evidence, diagrams, screenshots, and a clear demo.')],[1.8,4.7])
p('One useful distinction is authentication versus authorization. A session identifies the logged-in user, but each application lookup still has to verify ownership. Another is input validation versus output escaping: accepting appropriate values and safely displaying text address different risks.')
p('Testing the exact deadline boundaries also shows why business rules should be explicit. Today and the seventh day are included; past deadlines and the eighth day are excluded; Offered and Rejected records are not shown as upcoming active deadlines. This turns a vague feature description into reproducible behavior.')
p('Personal reflection: [Add your own challenges, mentor feedback, training activities, and how this project supports your career goals. Include only experiences that actually occurred.]')

h('8  Future work scope')
table(['Possible enhancement','Purpose / work required'],[
('Pagination and database aggregation','Improve dashboard behavior with many application records; benchmark before/after changes.'),('Email reminders','Add opt-in reminders, background scheduling, and notification delivery tests.'),('CSV import/export','Support data portability with validation and safe handling of spreadsheet content.'),('Status history','Record dated transitions and follow-up actions; currently only the latest status is stored.'),('Account management','Add email verification, password reset, and account settings.'),('Production deployment','Introduce a WSGI server, HTTPS, secure cookies, deployment secrets, database backups, and migrations.'),('Accessibility review','Extend automated/manual checks for contrast, screen readers, keyboard workflows, and error announcements.'),('Performance evaluation','Measure realistic dataset size, response latency, concurrent usage, and database contention.')],[1.7,4.8])
p('These items are proposed extensions and are not included in the implemented version. The present result is a complete local application for internship evaluation, supported by tests, documentation, screenshots, and a silent walkthrough. Before submission, fill the cover details and repository links and review the personal learning narrative.')

destination = OUT / 'JobTrack_Internship_Report.docx'
doc.save(destination)
print(destination)
