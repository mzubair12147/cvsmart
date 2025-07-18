import pdfplumber
import json
import re
from django.conf import settings
from .models import ResumeUpload
from google import genai


def clean_and_tokenize(text):
    text = re.sub(r"[^\w\s]", " ", text)  # remove punctuation
    tokens = re.split(r"\s+", text.lower())
    return set(filter(None, tokens))


def extract_and_save_resume_text(resume_id, file_path):
    try:
        resume = ResumeUpload.objects.get(id=resume_id)
        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        
        resume.extracted_text = text[:4000]
        resume.save()

        analyze_and_save_resume_vs_job(resume_id)

    except ResumeUpload.DoesNotExist:
        print(f"❌ Resume with ID {resume_id} not found.")
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")


def analyze_and_save_resume_vs_job(resume_id):
    try:
        resume = ResumeUpload.objects.get(id=resume_id)
        resume_text = resume.extracted_text or ""
        job_description = resume.job_description or ""

        if not resume_text or not job_description:
            resume.analysis_result = json.dumps(
                {"error": "Missing resume or job description."}
            )
            resume.save()
            return

        # --- Non-AI rule-based keyword matching ---
        resume_words = clean_and_tokenize(resume_text)
        job_keywords = clean_and_tokenize(job_description)

        

        matching_keywords = sorted(job_keywords & resume_words)
        missing_keywords = sorted(job_keywords - resume_words)
        skill_match_percent = (
            round((len(matching_keywords) / len(job_keywords)) * 100, 2)
            if job_keywords
            else 0
        )

        non_ai_result = {
            "rule_based_score": skill_match_percent,
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "resume_word_count": len(resume_words),
        }

        # --- Gemini Markdown Prompt ---
        prompt = f"""
You are a professional resume screening assistant.

Compare the **resume** with the **job description** and return a well-structured, clean markdown report that includes the following clearly labeled sections, each separated properly for a web display:

---

### 🤖 ATS Match Score
- Provide a number from 0 to 100 indicating how well the resume matches the job description for an ATS system.

---

### 🧩 Skill Match Summary
- A brief 2–3 sentence overview explaining the degree of alignment between the candidate’s skills and the job requirements.

---

### ✅ Strengths
- List 4 to 6 bullet points highlighting the candidate’s key strengths relevant to the job.

---

### ❌ Weaknesses
- List 4 to 6 bullet points indicating critical gaps or mismatches between the resume and the job description.

---

### 💡 Suggestions to Improve
- List practical, actionable recommendations to help the candidate tailor their resume and improve job match success.

---

### resume text: 📄 {resume_text}
    job_description : {job_description}

    
---

**Instructions:**
- Format your entire response using clean and professional **Markdown**.
- Use emojis or bold headers to make sections visually distinct.
- Do **not** include any JSON, metadata, explanation, or headings outside the sections defined above.
- Focus only on the content asked above — make it easy to read on a web page.
"""

# """


        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        ai_markdown = response.text.strip()
        print("🧠 Gemini Markdown Response:\n", ai_markdown)

        # Combine results
        combined_result = {"non_ai_analysis": non_ai_result, "ai_markdown": ai_markdown}

        resume.analysis_result = json.dumps(combined_result)
        resume.save()

    except ResumeUpload.DoesNotExist:
        print(f"❌ Resume ID {resume_id} not found.")
        ResumeUpload.objects.filter(id=resume_id).update(
            analysis_result=json.dumps({"error": f"Resume ID {resume_id} not found."})
        )
    except Exception as e:
        print(f"❌ Gemini analysis error: {e}")
        ResumeUpload.objects.filter(id=resume_id).update(
            analysis_result=json.dumps({"error": f"Unexpected error: {str(e)}"})
        )
