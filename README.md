# AI ASSIGNMENT EVALUATOR SYSTEM

## **Purpose**
The Assignment Submission and Grading System is designed to manage assignments, submissions, and grading for educational institutions, facilitating interaction between students and teachers. It provides a platform for students to submit their assignments (both coding and theory-based), while enabling teachers to view, grade, and manage these submissions efficiently.

## **Goals**
1. **Assignment Creation:**
   - Teachers should be able to create coding and theory assignments, providing necessary details such as title, description, questions (for coding), and instructions.
2. **Student Submissions:**
   - Students can submit assignments via a user-friendly interface, either by uploading files (for theory) or submitting code (for coding assignments).
   - Support for test case-based coding assignments, where students' code can be evaluated based on predefined test cases.
3. **Grading System:**
   - Teachers can grade assignments (both coding and theory) directly from the system, providing feedback where necessary.
   - Grading forms with numeric input and options to review student submissions (view code or answers) for accurate assessments.
4. **View and Manage Submissions:**
   - Teachers can view all submissions, filter by grade, or check the status of submissions (graded/ungraded).
   - Provide an interface for students to see their grades, feedback, and submission status.
5. **User Roles:**
   - **Teachers:** Can create assignments, view and grade submissions, and manage assignments.
   - **Students:** Can submit assignments and view grades and feedback for their submissions.
6. **System Flexibility:**
   - The platform supports different types of assignments (e.g., coding, theoretical) and allows for various submission formats like code, PDFs, or text answers.
7. **User-friendly Interface:**
   - Use of modern UI elements, including Bootstrap for responsive design and easy navigation.
   - Ensure pages are intuitive and simple, providing a smooth experience for both students and teachers.
8. **Real-time Updates:**
   - Changes in assignment status (graded or not) and new submissions are updated in real time, keeping users informed of any changes.

## **Key Features**
- **Assignment Creation (Coding/Theory)**
- **Submission Handling (Code/PDF/Text)**
- **Grading System (Manual and Test Case-based)**
- **Submission View (Code preview, Answers preview)**
- **Teacher Dashboard and Management**
- **Student Dashboard (Submission status, Grades)**
- **Notifications/Alerts on New Grades or Feedback**
- **Responsive Design for Mobile and Desktop**

## **Project Structure Overview** *(Focus on app.py and templates/)*

### **1. app.py: Main Application Logic and Routes**
- **Flask App Setup:** This is the core of your Flask application. It initializes the Flask app, loads configurations, and connects to the database.
- **Routes and Views:** The app uses Blueprints to organize the code into smaller parts. You will have routes for the teacher, student, and authentication (login/register). The routes correspond to different actions the users can perform, like submitting assignments or viewing submissions.
- **Configuration:** The app is configured with settings like the secret key for sessions and the database URI.
- **Main Route:** The `@app.route('/')` defines the home page, which might just redirect users to the login page.

### **2. templates/: HTML Templates**
The `templates/` folder contains the HTML files used to render content for the user interface. These templates extend a base layout and are populated with dynamic content, passed from Flask routes.

- **base.html:** This is the skeleton template containing the basic layout of your web pages. Other templates will extend this base template to avoid code duplication (like headers, footers, and navigation). It includes links to CSS files for styling and defines blocks where specific content for each page can be injected (e.g., page title, body content).
- **Assignment Submission Templates** (e.g., `submit_assignment.html`): These pages allow users (students) to submit their assignments. They will contain forms where students can either enter code or upload files. The content (like assignment details, instructions, and questions) is dynamically inserted from the backend.
- **Submissions and Grading Templates:** Templates like `view_submissions.html` and `view_theory_submissions.html` are for teachers to view student submissions. These pages will list students, their submissions, grades, and timestamps.
- **Dashboards:** Templates like `student_dashboard.html` and `teacher_dashboard.html` provide the user with their respective dashboard views. Teachers can view all assignments, submissions, and grade them, while students can see their progress and submitted work.

## **Routes for Teacher**

- **/teacher/dashboard**
  - **Purpose:** This is the teacher’s dashboard where they can see all assignments, their status, and links to manage submissions and grading.
  - **Behavior:** When a teacher accesses this page, it displays all assignments, along with their details (title, description, etc.), and allows the teacher to view or grade student submissions.
  
- **/teacher/assignments**
  - **Purpose:** Teachers use this route to manage assignments. It could show a list of all assignments or provide options to create new ones.
  - **Behavior:** The teacher can view details of each assignment and click on them to edit or view submissions.

- **/teacher/assignments/<assignment_id>**
  - **Purpose:** This page is for viewing details about a specific assignment.
  - **Behavior:** It displays the full details of the assignment (title, description, questions) and allows the teacher to interact with it further, such as viewing submissions.

- **/teacher/assignments/<assignment_id>/submissions**
  - **Purpose:** Teachers can view all student submissions for a specific assignment here.
  - **Behavior:** Displays a list of student submissions with options for grading and comments. Teachers can grade submissions and provide feedback through forms on this page.

- **/teacher/assignments/<assignment_id>/submissions/grade/<submission_id>**
  - **Purpose:** Teachers can grade individual submissions here.
  - **Behavior:** A form allows the teacher to input a grade for a specific student's submission, which is then saved in the database.

## **Routes for Student**

- **/student/dashboard**
  - **Purpose:** This route serves as the student’s dashboard.
  - **Behavior:** It displays assignments the student has access to, with links to submit work or view submission status. It may show progress, grades, or deadlines.

- **/student/assignments/<assignment_id>/submit**
  - **Purpose:** Students use this route to submit their work for a specific assignment.
  - **Behavior:** Displays a form for submitting code or uploading a PDF. After submission, the system may process the submission and store it in the database.

- **/student/assignments/<assignment_id>**
  - **Purpose:** This page displays the details of a specific assignment.
  - **Behavior:** Shows the assignment's title, description, and questions (and potentially the test cases for coding assignments). This is a read-only view for students.

- **/student/assignments/<assignment_id>/submissions**
  - **Purpose:** This route shows all the student’s submissions for an assignment, including their grade (if graded) and submission time.
  - **Behavior:** It allows the student to view feedback from the teacher and check if their assignment was successfully submitted.

## **Authentication Routes**

- **/login**
  - **Purpose:** This route handles the user login process.
  - **Behavior:** It displays a login form for both students and teachers to log into their accounts. After successful authentication, the user is redirected to their respective dashboard.

- **/register**
  - **Purpose:** This route is used to register new users (students or teachers).
  - **Behavior:** Displays a registration form for new users to create an account by providing necessary details like username, password, and role (student or teacher). After registration, the user can log in.

- **/logout**
  - **Purpose:** This route handles user logout.
  - **Behavior:** Logs out the current user and redirects them to the login page.

## **Assignment Creation (Teacher)**

- **/teacher/assignments/create**
  - **Purpose:** This page is for teachers to create new assignments.
  - **Behavior:** Displays a form for teachers to enter assignment details, including title, description, questions, and types of submissions (e.g., code or PDF).

## **Data Processing and Actions**

- **/submit_assignment/<assignment_id>**
  - **Purpose:** This is an action page for processing assignment submissions.
  - **Behavior:** This route would handle POST requests where students submit their assignments (code or file). It processes the file, saves it to the database, and provides feedback.

- **/grade_submission/<submission_id>**
  - **Purpose:** This route is triggered when a teacher grades a submission.
  - **Behavior:** Allows the teacher to enter a grade for the specific submission and save it to the database.

## **Flow of the Application**

### **1. Teacher’s Workflow:**
- The teacher logs in and can manage assignments through the teacher dashboard.
- They can create new assignments, view submissions, and grade them.
- Each assignment can be expanded to view specific submissions, and grading forms are available for each submission.

### **2. Student’s Workflow:**
- The student logs in and can see all assignments assigned to them.
- They can submit assignments through a dedicated form.
- After submission, they can view the status of their submission and check their grades once the teacher has graded it.
