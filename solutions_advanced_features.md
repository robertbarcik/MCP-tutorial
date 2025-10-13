# Solutions: MCP Advanced Features Exercises

This file contains solutions for the exercises in `2_MCP_resources_prompts_sampling.ipynb`.

---

## Exercise 1: Add Training Materials Resources

**Task**: Extend the HR server to include training materials as resources.

### Solution:

```python
# Add these two resources to HR_DOCUMENTS dictionary

HR_DOCUMENTS["hr://training/python-basics"] = {
    "title": "Python Programming Basics - Training Guide",
    "mimeType": "text/plain",
    "content": """
Python Programming Basics
=========================

What is Python?
Python is a high-level, interpreted programming language known for its simplicity
and readability. It's widely used in web development, data science, automation,
and AI/ML applications.

Basic Syntax:
- Variables: name = "Alice"
- Functions: def greet(name): return f"Hello, {name}"
- Loops: for i in range(10): print(i)
- Conditionals: if x > 5: print("Greater")

Why We Use Python:
- Easy to learn and read (great for beginners)
- Extensive library ecosystem (NumPy, Pandas, Django, etc.)
- Strong community support
- Versatile across many domains
- Cross-platform compatibility

Getting Started:
1. Install Python from python.org
2. Learn basic syntax and data types
3. Practice with small projects
4. Explore libraries relevant to your work
"""
}

HR_DOCUMENTS["hr://training/security-awareness"] = {
    "title": "Security Awareness Training",
    "mimeType": "text/plain",
    "content": """
Security Awareness Training
===========================

Password Best Practices:
- Use passwords at least 12 characters long
- Include uppercase, lowercase, numbers, and symbols
- Never reuse passwords across accounts
- Use a password manager (e.g., 1Password, LastPass)
- Enable multi-factor authentication (MFA) everywhere possible

Phishing Awareness:
- Verify sender email addresses carefully
- Never click suspicious links or download unknown attachments
- Look for urgent language ("Your account will be closed!")
- Check for spelling/grammar errors (common in phishing)
- When in doubt, contact the sender through official channels

Data Protection:
- Never share credentials via email or chat
- Lock your computer when away from desk (Cmd+Ctrl+Q on Mac, Win+L on Windows)
- Encrypt sensitive files before sharing
- Use company VPN when on public WiFi
- Report lost devices to IT immediately

Red Flags:
- Unexpected password reset emails
- Requests for sensitive information
- Links with misspelled domains (gooogle.com)
- Attachments from unknown senders

Report suspicious activity to security@company.com immediately.
"""
}

# Test your implementation
hr_server = HRResourceServer()  # Recreate server with new documents
training_resources = [r for r in hr_server.list_resources() if "training" in r['uri']]

print("Training Resources Added:")
for resource in training_resources:
    print(f"✅ {resource['name']} ({resource['uri']})")

# Read one of your new resources
print("\n" + "="*70)
doc = hr_server.read_resource("hr://training/python-basics")
print(doc['content'])
```

### Expected Output:

```
Training Resources Added:
✅ Python Programming Basics - Training Guide (hr://training/python-basics)
✅ Security Awareness Training (hr://training/security-awareness)

======================================================================

Python Programming Basics
=========================

What is Python?
Python is a high-level, interpreted programming language known for its simplicity
and readability...
```

---

## Exercise 2: Create an Interview Planning Prompt

**Task**: Add a new prompt template for planning candidate interviews.

### Solution Part 1: Prompt Definition

```python
interview_prompt_definition = {
    "name": "plan_interview",
    "description": "Structured interview planning workflow for hiring candidates",
    "arguments": [
        {"name": "candidate_name", "description": "Full name of the candidate", "required": True},
        {"name": "role", "description": "Position they're interviewing for", "required": True},
        {"name": "interview_date", "description": "Scheduled interview date (YYYY-MM-DD)", "required": True},
    ]
}

print("✅ Prompt definition created:")
print(interview_prompt_definition)
```

### Solution Part 2: Prompt Generator Function

```python
def generate_interview_prompt(candidate_name, role, interview_date):
    """
    Generate an interview planning prompt.

    The prompt should help HR plan a structured interview that covers:
    - Interview format (phone screen, technical, behavioral, etc.)
    - Key competencies to assess
    - Sample questions for each interview stage
    - Evaluation criteria
    - Next steps
    """

    return f"""
Interview Planning Guide
{'='*60}

Candidate: {candidate_name}
Role: {role}
Interview Date: {interview_date}

Plan a comprehensive interview process for this candidate:

## 1. Interview Format

Structure the interview into multiple rounds:

**Round 1: Phone Screen (30 minutes)**
- Interviewer: HR/Recruiter
- Goals: Cultural fit, communication skills, basic qualifications
- Format: Conversational, high-level

**Round 2: Technical Assessment (60 minutes)**
- Interviewer: Hiring Manager or Senior Team Member
- Goals: Assess role-specific skills and problem-solving
- Format: Technical questions, coding/design challenges, or case studies

**Round 3: Behavioral Interview (45 minutes)**
- Interviewer: Team Lead or Department Head
- Goals: Leadership, collaboration, past experience
- Format: STAR method questions (Situation, Task, Action, Result)

**Round 4: Team Fit (30 minutes)**
- Interviewer: 2-3 team members
- Goals: Team dynamics, work style compatibility
- Format: Casual conversation, Q&A

**Round 5: Final Interview (30 minutes)**
- Interviewer: Executive or VP
- Goals: Long-term potential, company vision alignment
- Format: Strategic discussion, career goals

## 2. Key Competencies to Assess

For the {role} position, evaluate:

- **Technical Skills**: Proficiency in required technologies/tools
- **Problem-Solving**: Analytical thinking and creativity
- **Communication**: Clarity in explaining complex ideas
- **Collaboration**: Teamwork and interpersonal skills
- **Adaptability**: Handling change and ambiguity
- **Leadership Potential**: Initiative and influence (if applicable)
- **Cultural Fit**: Alignment with company values

## 3. Sample Interview Questions

**Phone Screen:**
- Why are you interested in this role and our company?
- Walk me through your current/most recent position
- What are you looking for in your next opportunity?
- What's your salary expectation range?

**Technical Questions:**
- Describe a challenging technical problem you solved recently
- [Role-specific]: For engineers, coding challenge; for designers, portfolio review
- How do you stay current with industry trends?
- What's your approach to [key skill for the role]?

**Behavioral Questions (STAR method):**
- Tell me about a time you disagreed with a teammate. How did you handle it?
- Describe a project that didn't go as planned. What did you learn?
- Give an example of when you took initiative beyond your job description
- How do you prioritize when juggling multiple deadlines?

**Team Fit Questions:**
- What's your preferred working style (independent vs collaborative)?
- How do you handle feedback and constructive criticism?
- What type of work environment helps you thrive?
- What questions do you have for the team?

## 4. Evaluation Criteria

Rate each candidate on a scale of 1-5 for:

- Technical Competence: _____/5
- Problem-Solving Ability: _____/5
- Communication Skills: _____/5
- Cultural Fit: _____/5
- Experience Relevance: _____/5
- Growth Potential: _____/5

**Overall Score**: _____/30

**Recommendation**:
- [ ] Strong Hire - Make offer immediately
- [ ] Hire - Good candidate, extend offer
- [ ] Maybe - Need more evaluation
- [ ] No Hire - Not a fit for this role

## 5. Logistics

- **Preparation**: Send candidate prep email with schedule, interviewers, format
- **Materials**: Share resume with all interviewers 24 hours in advance
- **Tools**: Zoom links for remote, conference rooms for on-site
- **Timing**: Allow 15-minute breaks between rounds
- **Backup Plan**: Have alternate interviewer if someone is unavailable

## 6. Next Steps

**After Interview:**
1. All interviewers submit feedback within 24 hours
2. Schedule debrief meeting to discuss candidate
3. Reach consensus on hiring decision
4. If positive: Prepare offer and check references
5. If negative: Send polite rejection email
6. Timeline: Decision within 2-3 business days

**Follow-Up:**
- Send thank-you email to candidate within 24 hours
- If extending offer: Explain compensation, benefits, start date
- If not moving forward: Provide constructive feedback (optional)

---
**Remember**: Be respectful, ask follow-up questions, and sell the opportunity!
"""

# Test your implementation
test_prompt = generate_interview_prompt(
    candidate_name="John Smith",
    role="Senior Backend Engineer",
    interview_date="2025-01-20"
)

print(test_prompt)
```

### Expected Output:

```
Interview Planning Guide
============================================================

Candidate: John Smith
Role: Senior Backend Engineer
Interview Date: 2025-01-20

Plan a comprehensive interview process for this candidate:

## 1. Interview Format

Structure the interview into multiple rounds:

**Round 1: Phone Screen (30 minutes)**
- Interviewer: HR/Recruiter
- Goals: Cultural fit, communication skills, basic qualifications
...
```

---

## Alternative Exercise Solutions

### Exercise 1: Alternative Training Topics

Here are additional training resource ideas you could implement:

**Option A: Git & Version Control Training**
```python
HR_DOCUMENTS["hr://training/git-basics"] = {
    "title": "Git & Version Control Training",
    "mimeType": "text/plain",
    "content": """
Git & Version Control Basics
============================

What is Git?
Git is a distributed version control system that tracks changes in code
and enables collaboration among developers.

Key Concepts:
- Repository: Project folder tracked by Git
- Commit: Snapshot of changes with a message
- Branch: Parallel version of code
- Merge: Combining branches
- Pull Request: Proposing changes for review

Essential Commands:
- git clone: Copy a repository
- git add: Stage changes
- git commit -m "message": Save changes
- git push: Upload to remote
- git pull: Download latest changes
- git branch: Create/list branches

Best Practices:
- Commit frequently with clear messages
- Use branches for new features
- Pull before pushing to avoid conflicts
- Review code before merging
- Never commit sensitive data (passwords, keys)
"""
}
```

**Option B: Communication Skills Training**
```python
HR_DOCUMENTS["hr://training/effective-communication"] = {
    "title": "Effective Communication in the Workplace",
    "mimeType": "text/plain",
    "content": """
Effective Communication Training
================================

Written Communication:
- Be clear and concise
- Use proper grammar and punctuation
- Structure emails: greeting, purpose, action items, closing
- Respond within 24 hours (even if just to acknowledge)

Meeting Communication:
- Come prepared with agenda
- Start and end on time
- Take notes and share action items
- Give everyone a chance to speak
- Follow up with meeting summary

Presentation Skills:
- Know your audience
- Start with key takeaway
- Use visuals to support (not replace) your message
- Practice beforehand
- Handle Q&A confidently

Feedback:
- Give specific, actionable feedback
- Use "I" statements ("I noticed..." not "You always...")
- Balance constructive criticism with recognition
- Receive feedback graciously, don't be defensive

Collaboration:
- Ask clarifying questions
- Listen actively without interrupting
- Respect diverse perspectives
- Overcommunicate in remote settings
"""
}
```

### Exercise 2: Alternative Interview Prompts

**Option A: Performance Improvement Plan (PIP) Prompt**
```python
{
    "name": "create_performance_improvement_plan",
    "description": "Create a structured performance improvement plan for underperforming employees",
    "arguments": [
        {"name": "employee_id", "required": True},
        {"name": "performance_issues", "required": True},
        {"name": "duration_weeks", "required": True}
    ]
}
```

**Option B: Exit Interview Prompt**
```python
{
    "name": "conduct_exit_interview",
    "description": "Structured exit interview to gather feedback from departing employees",
    "arguments": [
        {"name": "employee_name", "required": True},
        {"name": "last_day", "required": True},
        {"name": "reason_for_leaving", "required": False}
    ]
}
```

---

## Testing Your Solutions

### Test Script for Exercise 1

```python
# Verify both training resources were added
assert "hr://training/python-basics" in HR_DOCUMENTS
assert "hr://training/security-awareness" in HR_DOCUMENTS

# Check structure
python_doc = HR_DOCUMENTS["hr://training/python-basics"]
assert "title" in python_doc
assert "mimeType" in python_doc
assert "content" in python_doc
assert len(python_doc["content"]) > 100  # Should have substantial content

print("✅ All assertions passed for Exercise 1!")
```

### Test Script for Exercise 2

```python
# Test the interview prompt generator
test_cases = [
    {
        "candidate_name": "Alice Johnson",
        "role": "Product Designer",
        "interview_date": "2025-02-01"
    },
    {
        "candidate_name": "Bob Smith",
        "role": "Data Scientist",
        "interview_date": "2025-02-15"
    }
]

for test in test_cases:
    prompt = generate_interview_prompt(**test)

    # Verify prompt contains key sections
    assert test["candidate_name"] in prompt
    assert test["role"] in prompt
    assert test["interview_date"] in prompt
    assert "Interview Format" in prompt
    assert "Competencies" in prompt
    assert "Questions" in prompt
    assert "Evaluation Criteria" in prompt

    print(f"✅ Interview prompt generated successfully for {test['candidate_name']}")

print("\n✅ All assertions passed for Exercise 2!")
```

---

## Common Mistakes & Tips

### Exercise 1 Common Mistakes:

❌ **Mistake**: Forgetting to include `mimeType`
```python
# Wrong:
HR_DOCUMENTS["hr://training/python"] = {
    "title": "Python Training",
    "content": "..."
}
```

✅ **Correct**:
```python
HR_DOCUMENTS["hr://training/python"] = {
    "title": "Python Training",
    "mimeType": "text/plain",  # Don't forget this!
    "content": "..."
}
```

❌ **Mistake**: Content too short or generic
```python
# Too short:
"content": "Python is a programming language."
```

✅ **Better**:
```python
# Include useful details (5-10 lines minimum):
"content": """
Python Programming Basics
=========================

What is Python?
Python is a high-level programming language...

Basic Syntax:
- Variables: x = 5
...
"""
```

### Exercise 2 Common Mistakes:

❌ **Mistake**: Forgetting to use f-string interpolation
```python
# Wrong - static text:
return "Interview Planning Guide for Senior Engineer"
```

✅ **Correct**:
```python
# Dynamic with arguments:
return f"Interview Planning Guide for {role}"
```

❌ **Mistake**: Not including enough detail
```python
# Too brief:
return f"Interview {candidate_name} for {role}"
```

✅ **Better**:
```python
# Structured with sections:
return f"""
Interview Planning Guide
...
## 1. Interview Format
...
## 2. Key Competencies
...
"""
```

---

## Extension Challenges

If you finished the exercises, try these advanced challenges:

### Challenge 1: Add Resource Metadata
Extend resources to include tags, authors, and last updated dates.

### Challenge 2: Create a "Salary Negotiation" Prompt
Build a prompt that helps HR navigate salary negotiations with candidates.

### Challenge 3: Combine Resources and Prompts
Create a prompt that references specific resources (e.g., "onboard_employee" prompt that mentions handbook resources).

---

**Happy Learning! 🎓**
