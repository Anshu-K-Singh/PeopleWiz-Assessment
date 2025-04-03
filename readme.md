

# AI-Powered Resume-Based Cold Email Generator: Development Approach

## 1. Introduction


### Objectives
- Provide a simple, user-friendly interface for uploading resumes and generating emails.
- Leverage AI to extract information from resumes and craft persuasive email content.
- Implement secure user authentication to personalize and protect data.
- Enable persistent storage and management of resumes.

### Technologies
- **FastHTML**: A Python framework combining server-side rendering with HTMX for dynamic updates and PicoCSS for styling.
- **Groq API**: Utilizes the LLaMA 3 70B model for natural language processing tasks.
- **SQLite**: Lightweight database for storing user and resume data.
- **PyPDF2**: Library for extracting text from PDF resumes.


## . Development Approach


#### User Workflow
1. **Registration**: New users create an account with a username, email, and password.
2. **Login**: Existing users authenticate to access their dashboard.
3. **Resume Management**: Users upload, view, edit, or delete resumes.
4. **Email Generation**: Users input recipient details, and the AI crafts an email based on their resume.
5. **Logout**: Users end their session securely.

#### 3.1.2 Data Model
- **Users**: Stores authentication data (username, email, password).
- **Resumes**: Stores resume data (username, name, content, date), linked to users via the username.

### Implementation 

#### Environment Setup
The initial step involved setting up the Python environment and installing dependencies. FastHTML was chosen for its simplicity, while the Groq API provided powerful AI capabilities. SQLite was selected for its lightweight nature, suitable for a small-scale application, and PyPDF2 was added to handle PDF parsing.

#### Database Design
The database was designed with two tables:
- **Users**: A primary key of `username` ensures uniqueness, with `email` and `password` for authentication.
- **Resumes**: Linked to `users` via `username`, with fields for resume metadata and content. FastLite’s dataclass generation simplified interaction with these tables.

#### Authentication System
Authentication was implemented using FastHTML’s session management and middleware:
- **Middleware**: A `Beforeware` function checks for an authenticated session (`auth` in session data). Unauthenticated requests redirect to the login page, except for public routes (`/login`, `/register`).
- **Registration**: Users submit a form, and the system checks for username availability. If available, the user is registered and logged in by setting the session.
- **Login**: Credentials are verified against the database. Successful logins set the session, while failures display an error.
- **Logout**: Clears the session and redirects to login.

#### Core Features
1. **Resume Upload**:
   - Users upload PDF or text files via a form with `multipart/form-data` encoding.
   - The backend parses the file (PDFs with PyPDF2, text files directly) and uses Groq’s LLaMA model to extract the user’s name.
   - Parsed data is stored in the `resumes` table with a timestamp.

2. **Resume Management**:
   - **Create**: Handled by the upload process.
   - **Read**: Displays a list of resumes for the authenticated user, with clickable links to view details.
   - **Update**: An edit form allows modification of resume fields.
   - **Delete**: Removes a resume from the database and updates the UI.

3. **Email Generation**:
   - Users input recipient details (name, company, job/purpose) in a form.
   - The backend selects the latest resume (or a specific one if enhanced) and sends its content to Groq’s LLaMA model with a prompt to generate a professional email.
   - The response is formatted and displayed dynamically using HTMX.

#### UI Design
The interface was kept minimalistic using FastHTML’s component system and PicoCSS:

### AI Integration
Groq’s LLaMA model was integrated for two purposes:
- **Resume Parsing**: Extracts the user’s name from resume content, falling back to “Unknown” if unclear.
- **Email Generation**: Crafts a cold email by analyzing resume content and tailoring it to the recipient’s context. Prompts were designed to ensure concise, formatted outputs.






--- 