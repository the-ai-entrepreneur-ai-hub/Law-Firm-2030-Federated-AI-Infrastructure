
# Product Requirements Document: AnwaltsAI (v1.0)

| **Document Information** | |
| :--- | :--- |
| **Product Name** | AnwaltsAI |
| **Version** | 1.0 |
| **Date** | October 26, 2023 |
| **Author** | Product Management |
| **Status** | Draft |
| **Audience** | Stakeholders, Engineering, Design, QA |

---

## 1. Introduction & Vision

### 1.1. Overview
AnwaltsAI is a specialized, AI-powered web application designed for legal professionals in Germany. At its core, the platform leverages a highly trained language model, specialized in German legal documentation, to automate and assist with the drafting of legal documents and correspondence. It aims to significantly enhance the productivity of lawyers and their assistants (Rechtsanwaltsfachangestellte - "Refas") by reducing the time spent on repetitive and formulaic drafting tasks, ensuring consistency, and providing intelligent assistance.

### 1.2. Problem Statement
Legal professionals spend a substantial amount of time drafting, reviewing, and responding to a wide range of documents, from simple payment reminders to complex contracts. This process is often manual, repetitive, and prone to human error. Existing tools are often generic and lack the specific domain knowledge required for the nuances of German law.

### 1.3. Solution & Goal
AnwaltsAI provides an intuitive interface to a powerful, legally-trained AI model. Users can generate new documents from scratch, use templates, or get assistance in responding to incoming correspondence and documents. By providing a tight feedback loop where user interactions (accepting, editing, or rejecting AI outputs) are used to continuously improve the model, AnwaltsAI will become an increasingly indispensable and intelligent partner for law firms.

**The primary goals are to:**
- **Increase Efficiency:** Drastically reduce the time required to draft standard legal documents and responses.
- **Improve Quality & Consistency:** Minimize errors and ensure a consistent tone and format across all firm documents.
- **Create a Learning System:** Build a platform that learns from user feedback to become more accurate and helpful over time.

---

## 2. User Personas

### 2.1. Dr. Anna Vogel (Admin / Lawyer)
- **Role:** Partner at a mid-sized German law firm.
- **Needs:**
  - Wants to maximize her team's billable hours by minimizing time on administrative tasks.
  - Needs to ensure all outgoing documents are of the highest legal and professional standard.
  - Requires oversight and the ability to set firm-wide standards (e.g., standard templates).
  - Is tech-savvy but extremely time-poor; the tool must be intuitive and reliable from the start.
- **Frustrations:** Inconsistent quality in first drafts from assistants; bottlenecks caused by her having to review every minor document.

### 2.2. Markus Schmidt (Assistant / "Refa")
- **Role:** Legal assistant responsible for case management, client communication, and initial document drafting.
- **Needs:**
  - A faster way to draft common documents like fee reminders, requests for information, and standard contracts.
  - Confidence that his initial drafts are accurate and require fewer revisions from the lawyer.
  - A centralized place to manage drafting tasks related to incoming emails and files.
- **Frustrations:** Tedious copy-pasting from old documents; uncertainty about using the correct phrasing; time wasted searching for the right template.

---

## 3. Features & Requirements

This PRD covers the Minimum Viable Product (MVP) for AnwaltsAI.

### 3.1. User Authentication & Roles (F-AUTH)

- **F-AUTH-01: Login Page**
  - A clean, professional login page shall be presented to all non-authenticated users.
  - Users will log in using an email and password combination.
  - The page will feature the AnwaltsAI logo.
- **F-AUTH-02: User Roles**
  - The system shall support two distinct user roles with different permission levels:
    - **Admin (e.g., Lawyer):** Full access to all features, including managing firm-wide templates and potentially user management in the future.
    - **Assistant (e.g., Refa):** Restricted access. Can use all core generation features but may have limitations on creating or editing firm-wide templates.
- **F-AUTH-03: Logout**
  - A clear and accessible logout button/icon shall be available within the application's main navigation, allowing users to securely end their session.

### 3.2. Main Dashboard (F-DASH)

- **F-DASH-01: Landing Page**
  - Upon successful login, the user shall be directed to a central dashboard.
- **F-DASH-02: Navigation Hub**
  - The dashboard will display large, clickable cards for primary application sections, as per the mockup:
    - **Document Generator:** "Create legal documents with ease."
    - **Mailbox:** "View and manage your emails."
    - **Saved Templates:** "Access your previously saved templates."
- **F-DASH-03: Persistent Navigation**
  - A persistent vertical navigation bar shall be present on the left side of the screen, providing access to all key areas: Home (Dashboard), Emails, Document Generator, Templates.

### 3.3. Email Portal / Inbox (F-MAIL)

- **F-MAIL-01: Inbox View**
  - This page will display a list of incoming emails.
  - **For v1.0, this can be populated with static, sample data.**
  - The list shall be presented in a table format with the following columns: **Sender**, **Subject**, **Date**.
- **F-MAIL-02: Attachment Indicator**
  - An icon or text label (e.g., "📎 Attachment") shall be displayed next to the subject for emails that contain attachments.
- **F-MAIL-03: Inbox Filtering & Views**
  - The user shall have controls to change the inbox view:
    - **Full view / Preview pane:** Toggles to adjust the layout of the email list.
    - **"Show AI-responses" filter:** A dropdown/toggle that filters the list to show only emails for which an AI-generated response or document has already been created.
- **F-MAIL-04: Email Detail & Action (Implied Feature)**
  - Clicking on an email in the list shall open a detailed view of that email (functionality can be limited for v1).
  - From the detail view, the user must have a clear call-to-action to "Generate Response" or "Create Document," which would pre-populate the AI Document Generator with the context of the email.

### 3.4. AI Document Generator (F-GEN)
This is the core feature of the application.

- **F-GEN-01: Multi-Input Interface**
  - The generator page will have a two-panel layout: inputs on the left, and AI-generated output on the right.
  - The user shall have three primary methods for providing context to the AI:
    1. **Prompt Area:** A text area where the user can type a natural language command (e.g., "Generate a contract for the sale of commercial real estate from Paul Müller to Erika Becker.").
    2. **Template Selection:** A dropdown menu to select from a list of pre-defined system templates or user-saved custom templates (e.g., "Payment Reminder," "NDA").
    3. **Document Upload:** A drag-and-drop area that accepts `.PDF` and `.DOCX` files. The AI will use the content of the uploaded document as context for the prompt.
- **F-GEN-02: Generation Command**
  - A prominent "Generate" button will initiate the AI generation process. The system should display a loading or processing indicator while the model is working.
- **F-GEN-03: Output Display**
  - The AI-generated document shall be displayed in a text box on the right-hand panel.
  - **The text in this box must be fully editable by the user.**
- **F-GEN-04: Post-Generation User Feedback Loop**
  - Below the output box, three action buttons must be present. These actions are critical for the RLHF (Reinforcement Learning from Human Feedback) data collection.
    1. **✅ Accept:** The user is satisfied with the document. Clicking this confirms the output.
       - *System Action:* Log the prompt, context, and generated text as a "positive" example. The user should then be able to copy the text or download the file.
    2. **✏️ Improve (or "Edit & Regenerate"):** The user is mostly satisfied but wants to make changes.
       - *User Flow:* User edits the text directly in the output box -> Clicks "Improve".
       - *System Action:* Log the original prompt, the original generation, and the user's edited version. Send the edited text back to the model with the original context to generate a new, improved version. This provides a rich "correction" signal.
    3. **❌ Reject:** The user finds the output unsatisfactory.
       - *User Flow:* User clicks "Reject". A small modal or text field should appear, prompting for brief feedback (e.g., "Why was this result unhelpful?").
       - *System Action:* Log the prompt, context, and generated text as a "negative" example. Log the user's qualitative feedback. The user can then modify their prompt and try again.

### 3.5. Template Management (F-TMP)

- **F-TMP-01: Saving a Custom Template**
  - On the Document Generation page, a toggle or checkbox labeled "Save output as custom template" shall be available.
  - If this is checked when a user clicks "Accept" on a generated document, the system will prompt them to enter a name for the new template.
  - The saved template will then be available in the "Template" dropdown for future use.
- **F-TMP-02: Template Management Page**
  - A dedicated "Templates" page (accessible from the main navigation) will list all of the user's custom-saved templates.
  - Users will be able to view, rename, or delete their custom templates from this page.
- **F-TMP-03: System Templates**
  - The application will come pre-loaded with a set of common German legal templates (e.g., "Mahnung" (Payment Reminder), "NDA"). These cannot be deleted by the user.
- **F-TMP-04: Template Usage**
  - When a user selects a template, its structure is sent to the model along with the user's specific prompt. The prompt provides the dynamic data to fill in or modify the static template structure (e.g., Prompt: "Use this for client John Schmidt, invoice #123, amount €500").

---

## 4. Technical Considerations & Non-Functional Requirements

- **AI Model:** The backend will integrate with a pre-trained language model specialized in German legal texts. API calls will need to be structured to pass all context (prompt, template, uploaded files).
- **Security & Data Privacy:** As the application will handle highly sensitive legal data, it must be compliant with GDPR. All data in transit and at rest must be encrypted. User data must be strictly isolated.
- **Document Parsing:** The backend must include libraries capable of accurately parsing text content from `.PDF` and `.DOCX` files.
- **Feedback Data Pipeline:** A robust logging mechanism must be built to capture the full context of each generation request and the user's subsequent action (Accept, Improve, Reject + feedback). This data needs to be stored in a structured way for future model retraining.
- **Performance:** AI generation should be reasonably fast. The UI must provide clear feedback to the user (e.g., spinners, progress indicators) to manage expectations during wait times.
- **Scalability:** The architecture should be designed to handle a growing number of users and generation requests.

---

## 5. Success Metrics (KPIs)

- **User Adoption:**
  - Number of active users (Daily/Weekly/Monthly).
  - User retention rate.
- **Feature Engagement:**
  - Average number of documents generated per active user per week.
  - Template creation rate (number of custom templates saved).
- **AI Model Quality:**
  - **Accept/Reject Ratio:** Track the ratio of "Accept" clicks vs. "Reject" clicks. A primary goal is to see this ratio improve over time as the model learns.
  - **Improvement Rate:** Track the frequency of the "Improve" action. A high rate indicates the model is useful but not perfect. A decreasing rate over time is a positive sign.
  - Qualitative feedback analysis from the "Reject" reason.

---

## 6. Future Scope (Post-v1.0)

- **Full Email Integration:** IMAP/OAuth integration with major email providers (e.g., Outlook, Gmail) to create a live, fully functional inbox.
- **Advanced Editor:** Replace the plain text output box with a rich-text editor (WYSIWYG) to allow for formatting (bold, italics, lists, etc.).
- **Collaboration:** Features to allow users within the same firm to share, comment on, and co-edit generated documents.
- **Advanced Admin Panel:** A dedicated area for Admins to manage users, view firm-wide usage analytics, and manage official firm templates.
- **E-Signature Integration:** Integrate with services like DocuSign to allow for a seamless "generate-and-send-for-signature" workflow.
- **File Management System:** A more robust "Files" section to store and organize all generated and uploaded documents.
```