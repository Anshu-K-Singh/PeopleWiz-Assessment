from fasthtml.common import *
from auth import app, rt, db, resumes, Resume  
from groq import Groq
import PyPDF2
from datetime import datetime

import os
port = int(os.getenv("PORT", 5001))
serve(port=port)
# Groq setup
groq_client = Groq(api_key="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")


def tid(id): return f'resume-{id}'
id_curr = 'current-resume'

@patch
def __ft__(self: Resume):
    show = AX(self.name, f'/resumes/{self.id}', id_curr)
    edit = AX('edit', f'/edit/{self.id}', id_curr)
    return Li(self.date, ": ", show, ' | ', edit, id=tid(self.id))

def mk_file_input(**kw): return Input(id="resume", name="resume", type="file", accept=".pdf,.txt", required=True, **kw)
def mk_email_input(id, name, placeholder, **kw): return Input(id=id, name=name, placeholder=placeholder, required=True, **kw)


@rt("/")
def get(auth):
    upload_form = Form(Group(mk_file_input(), Button("Upload Resume")), enctype="multipart/form-data", hx_post="/upload", target_id='resume-list', hx_swap="afterbegin")
    email_form = Form(Group(
        mk_email_input("recipient", "recipient", "Recipient Name"),
        mk_email_input("company", "company", "Company Name"),
        mk_email_input("job", "job", "Job Title or Purpose"),
        Button("Generate Email")
    ), hx_post="/generate", target_id="email-output", hx_swap="innerHTML")
    card = Card(Ul(*resumes(), id='resume-list'), header=upload_form, footer=Div(id=id_curr))
    return Title(f"{auth}'s Cold Email Generator"), Main(
        H1(f"Welcome, {auth}"),
        A("Logout", href="/logout"),
        card,
        H2("Generate Cold Email"),
        email_form,
        Div(id="email-output"),
        cls="container"
    )


@rt("/upload")
async def post(resume: UploadFile, auth):
    content = ""
    if resume.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(resume.file)
        content = "\n".join(page.extract_text() for page in pdf.pages)
    elif resume.filename.endswith('.txt'):
        content = (await resume.read()).decode('utf-8')
    
    prompt = f"Extract the full name from this resume content:\n{content[:1000]}\nReturn only the name or 'Unknown' if not found."
    response = groq_client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "user", "content": prompt}], max_tokens=50)
    name = response.choices[0].message.content.strip() or "Unknown"
    
    date = datetime.now().strftime("%Y-%m-%d")
    resume_obj = Resume(username=auth, name=name, content=content, date=date)
    return resumes.insert(resume_obj)

@rt("/resumes/{id}")
def delete(id: int):
    resumes.delete(id)
    return clear(id_curr)

@rt("/edit/{id}")
def get(id: int):
    res = Form(Group(Input(id="name"), Textarea(id="content", name="content", rows=5), Input(id="date"), Button("Save")),
               Hidden(id="id"), Hidden(id="username"), hx_put="/", hx_swap="outerHTML", target_id=tid(id))
    return fill_form(res, resumes[id])

@rt("/")
def put(resume: Resume):
    return resumes.update(resume), clear(id_curr)

@rt("/resumes/{id}")
def get(id: int):
    resume = resumes[id]
    btn = Button('delete', hx_delete=f'/resumes/{resume.id}', target_id=tid(resume.id), hx_swap="outerHTML")
    return Div(H2(resume.name), P(f"Uploaded: {resume.date}"), Pre(resume.content[:500] + "..."), btn)

@rt("/generate")
def post(recipient: str, company: str, job: str, auth, id: int = None):
    resume = resumes[id] if id else resumes(order_by='id desc')[0]
    prompt = f"""
    Generate a professional cold email using this resume content:\n{resume.content[:1000]}
    The recipient is {recipient} from {company}. The purpose is related to '{job}'.
    Keep it concise, friendly, and persuasive. Include relevant skills or experiences from the resume.
    Format as:
    Subject: [subject line]
    Body: [email body with line breaks]
    """
    response = groq_client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "user", "content": prompt}], max_tokens=300)
    email_text = response.choices[0].message.content.strip()
    return Pre(email_text, cls="email-content")


serve()