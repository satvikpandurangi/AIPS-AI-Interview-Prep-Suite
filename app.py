import streamlit as st
import ai_services
import re

st.set_page_config(page_title="AIPS Platform", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("AIPS: AI Interview Prep Suite")

# --- GLOBAL STATE INITIALIZATION ---
if 'qa_list' not in st.session_state:
    st.session_state.qa_list = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 0
if 'target_role' not in st.session_state:
    st.session_state.target_role = "Full-Stack Developer"
if 'experience_level' not in st.session_state:
    st.session_state.experience_level = "Entry Level"

# --- DUMMY PROFILES DIRECTORY ---
DUMMY_PROFILES = {
    "Full-Stack Developer": "Name: Satvik\nEducation: 3rd Year CS Student\nProjects:\n1. E-Commerce Platform: Built a scalable e-commerce site using React, Node.js, and PostgreSQL with Stripe integration.\n2. Task Manager API: Developed a RESTful API using FastAPI and MongoDB.\nSkills: JavaScript, Python, React, Node.js, SQL, Docker.",
    "Embedded Systems Engineer": "Name: Satvik\nEducation: 2nd Semester ECE Student\nProjects:\n1. Phoenix-Eye: AI-driven multimodal diagnosis system for electronics repair.\n2. ASTRADRISHTI: Surveillance prototype using ESP32 and PIR sensors for motion detection.\nSkills: C/C++, Python, Embedded Systems, Microcontrollers, RTOS.",
    "Agentic AI Developer": "Name: Satvik\nEducation: 3rd Year AI Engineering Student\nProjects:\n1. Auto-Coder Agent: Created a multi-agent system using LangChain to generate, test, and debug Python code autonomously.\n2. Rag-Chatbot: Built a completely RAG-based customer service bot leveraging Gemini and Pinecone.\nSkills: Python, LangChain, LLMs, Prompt Engineering, Vector Databases.",
    "Data Analyst": "Name: Satvik\nEducation: Final Year Statistics Student\nProjects:\n1. Sales Forecasting: Built an ARIMA model to predict quarterly sales with 95% accuracy using Pandas and Scikit-Learn.\n2. Customer Segmentation Dashboard: Designed a PowerBI interactive dashboard tracking churn rate.\nSkills: Python, SQL, Pandas, Tableau, PowerBI, Statistical Analysis."
}

ROLE_OPTIONS = ["Full-Stack Developer", "Embedded Systems Engineer", "Agentic AI Developer", "Data Analyst"]
EXPERIENCE_OPTIONS = ["Entry Level", "Internship", "Junior"]

page = st.sidebar.radio("Navigation", ["1. Profile & Resume", "2. Study Plan", "3. Q&A Bank", "4. Mock Interview"])

if page == "1. Profile & Resume":
    st.header("Build Your Profile")
    
    # Using key automatically syncs the selectbox value with st.session_state
    selected_role = st.selectbox(
        "Target Role", 
        ROLE_OPTIONS, 
        index=ROLE_OPTIONS.index(st.session_state.target_role) if st.session_state.target_role in ROLE_OPTIONS else 0,
        key="target_role"
    )
    
    selected_level = st.selectbox(
        "Experience Level", 
        EXPERIENCE_OPTIONS, 
        index=EXPERIENCE_OPTIONS.index(st.session_state.experience_level) if st.session_state.experience_level in EXPERIENCE_OPTIONS else 0,
        key="experience_level"
    )
    
    # We fetch the specific dummy profile based on the current synchronized role
    profile_text = DUMMY_PROFILES.get(st.session_state.target_role, DUMMY_PROFILES["Full-Stack Developer"])
    
    profile_input = st.text_area(
        "Paste your raw experience, skills, and projects here:", 
        value=profile_text, 
        height=180
    )
    
    if st.button("Generate Tailored Resume"):
        if profile_input:
            with st.spinner("Optimizing Resume..."):
                # Always pass the currently selected role
                resume_md = ai_services.generate_resume(profile_input, st.session_state.target_role)
                st.markdown("### Your ATS-Optimized Resume")
                st.markdown(resume_md)
                st.download_button("Download as TXT", resume_md, file_name="resume.txt")
        else:
            st.warning("Please enter your profile data first.")

elif page == "2. Study Plan":
    st.header("Generate a 3-Day Study Plan")
    
    DOMAINS = {
        "Full-Stack Developer": "React & Node.js",
        "Embedded Systems Engineer": "C++ & RTOS",
        "Agentic AI Developer": "LangChain & Vector APIs",
        "Data Analyst": "Pandas & Data Visualization"
    }
    
    default_domain = DOMAINS.get(st.session_state.target_role, "General Framework")
    
    # Display their globally synced role and let them change the domain if they want
    st.info(f"Target Role: **{st.session_state.target_role}**")
    
    domain_input = st.text_input("Target Domain/Framework", value=default_domain)
    
    if st.button("Generate Study Plan"):
        if domain_input:
            with st.spinner("Crafting your study plan..."):
                study_plan_md = ai_services.generate_study_plan(st.session_state.target_role, domain_input)
                st.markdown("### Your Custom 3-Day Study Plan")
                st.markdown(study_plan_md)
                st.download_button("Download Study Plan", study_plan_md, file_name="study_plan.md")
        else:
            st.warning("Please provide a Target Domain/Framework.")

elif page == "3. Q&A Bank":
    st.header("Generate Preparation Material")
    
    # Display the synced preferences
    st.info(f"Generating questions for a **{st.session_state.experience_level}** **{st.session_state.target_role}**.")

    if st.button("Generate Q&A Bank"):
        with st.spinner("Curating questions..."):
            st.session_state.qa_list = ai_services.generate_qa(
                st.session_state.target_role, 
                st.session_state.experience_level
            )
            
            # Reset mock interview state
            st.session_state.messages = []
            st.session_state.q_idx = 0
            
            st.success("Questions loaded! Head to the Mock Interview tab to practice.")
            
            for q in st.session_state.qa_list:
                with st.expander(q['question']):
                    st.write(f"**Ideal Answer Outline:** {q['ideal_answer']}")

elif page == "4. Mock Interview":
    st.header("Continuous Mock Interview")
    st.subheader(f"Role: {st.session_state.target_role} | Level: {st.session_state.experience_level}")
    
    if not st.session_state.qa_list:
        st.info("Please generate the Q&A bank in the '3. Q&A Bank' page first.")
    else:
        # If we have QAs but haven't started questioning yet
        if not st.session_state.messages and st.session_state.q_idx == 0:
            first_q = st.session_state.qa_list[0]['question']
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Hi! Let's begin the interview. Here is your first question:\n\n**{first_q}**",
                "type": "question"
            })
            
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                if msg.get("type") == "evaluation":
                    score = msg.get("score", 0)
                    feedback = msg.get("feedback", "")
                    st.metric("Score", f"{score}/10")
                    # Provide visual separation based on score
                    if score >= 7:
                        st.success(feedback)
                    elif score >= 5:
                        st.warning(feedback)
                    else:
                        st.error(feedback)

        # Allow user to respond if we haven't asked all questions
        if st.session_state.q_idx < len(st.session_state.qa_list):
            if prompt := st.chat_input("Your Response:"):
                # Append user message to state
                st.session_state.messages.append({"role": "user", "content": prompt, "type": "answer"})
                
                current_q = st.session_state.qa_list[st.session_state.q_idx]['question']
                role = st.session_state.target_role 
                
                with st.spinner("Evaluating your response..."):
                    eval_text = ai_services.evaluate_answer(current_q, prompt, role)
                    
                    # Extract score out of 10
                    score = 0
                    score_match = re.search(r'(\d+)(?:\s)?/(?:\s)?10', eval_text)
                    if score_match:
                        score = int(score_match.group(1))

                    # Append evaluation message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Here is the feedback for your response:",
                        "type": "evaluation",
                        "score": score,
                        "feedback": eval_text
                    })
                    
                    st.session_state.q_idx += 1
                    
                    # Add next question if there is one
                    if st.session_state.q_idx < len(st.session_state.qa_list):
                        next_q = st.session_state.qa_list[st.session_state.q_idx]['question']
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Let's move on to the next question:\n\n**{next_q}**",
                            "type": "question"
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "That concludes our mock interview. Great job practicing! Feel free to visit the Q&A Bank to generate a new set of questions.",
                            "type": "question"
                        })
                
                st.rerun()
