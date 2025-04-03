from fasthtml.common import *
from fastlite import NotFoundError

# Database setup
db = database('data/resume_emails.db')
users = db.t.users
resumes = db.t.resumes
if 'users' not in db.t:
    users.create(id=int, username=str, email=str, password=str, pk='username')
if 'resumes' not in db.t:
    resumes.create(id=int, username=str, name=str, content=str, date=str, pk='id')
User = users.dataclass()
Resume = resumes.dataclass()

# Authentication middleware
login_redir = RedirectResponse('/login', status_code=303)
def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth: return login_redir
    resumes.xtra(username=auth)

# App setup
app = FastHTML(before=Beforeware(before, skip=[r'/login', r'/register', r'/.*\.ico']),
               hdrs=(picolink, Style(':root { --pico-font-size: 100%; }')))
rt = app.route

# Authentication routes
@rt("/register")
def get():
    return Titled("Register",
                  Form(Input(type="text", name="username", placeholder="Username"),
                       Input(type="email", name="email", placeholder="Email"),
                       Input(type="password", name="password", placeholder="Password"),
                       Button("Register", type="submit"),
                       hx_post="/register", hx_target="#result"),
                  Div(id="result"),
                  A("Already have an account? Login", href="/login"))

@rt("/register")
def post(user: User, sess):
    try:
        users[user.username]
        return Div("Username already taken", id="result", style="color: red;")
    except NotFoundError:
        users.insert(user)
        sess['auth'] = user.username
        return RedirectResponse('/', status_code=303)

@rt("/login")
def get():
    return Titled("Login",
                  Form(Input(type="text", name="username", placeholder="Username"),
                       Input(type="password", name="password", placeholder="Password"),
                       Button("Login", type="submit"),
                       hx_post="/login", hx_target="#result"),
                  Div(id="result"),
                  A("Need an account? Register", href="/register"))

@rt("/login")
def post(username: str, password: str, sess):
    try:
        user = users[username]
        if user.password != password:
            return Div("Incorrect password", id="result", style="color: red;")
    except NotFoundError:
        return Div("Username not found", id="result", style="color: red;")
    sess['auth'] = username
    return RedirectResponse('/', status_code=303)

@rt("/logout")
def get(sess):
    del sess['auth']
    return login_redir