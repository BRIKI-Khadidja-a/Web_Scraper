import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'register'

def check_auth_status():
    """check if user is already logged in from session"""
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            return True
    except:
        pass
    return False

def get_user_role(user_id):
    """ retrieve user role from database"""
    try:
        result = supabase.table("users").select("role").eq("id", user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]["role"]
    except Exception as e:
        st.error(f"Error fetching user role: {str(e)}")
    return None

def login_page():
    """display login page"""
    st.title("Welcome Back")
    st.markdown("""
    Sign in to access your personalized dashboard and continue your journey with us.
    """)
    
    email = st.text_input("Email", key="login_email").strip()
    password = st.text_input("Password", type="password", key="login_password")
    

    if st.button("Submit", use_container_width=True):
        if not email or not password:
            st.error("Please enter both email and password.")
            return
        
        try:
            with st.spinner("Logging in..."):
                auth_res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
            
            if auth_res.user:
                st.session_state.user = auth_res.user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
        except Exception as e:
            st.error("Login failed. Please check your credentials.")

    st.divider()
    st.subheader("Don't have an account ?")
    if st.button("Go to Register", use_container_width=True):
        st.session_state.page = 'register'
        st.rerun()

def register_page():
    """display registration page"""
    st.title("Get Started Today 🚀")
    
    st.markdown("""
    ### Are you a student searching for internships or a company building your team?
    
    Join our platform to unlock new opportunities. Students can explore internships tailored 
    to their skills and career goals, while companies connect with motivated candidates who 
    bring fresh ideas and enthusiasm to the workplace.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**👨‍🎓 Students**: Create a profile, browse internships, and apply to opportunities that match your skills and interests.")
    with col2:
        st.info("**🏢 Companies**: Post internship positions, review applications, and connect with top student talent.")

    st.divider()
    st.subheader("Register Now!")
    role = st.selectbox("Choose your role", ["student", "company"])
    email = st.text_input("Email", key="reg_email").strip()
    password = st.text_input("Password", type="password", key="reg_password")
    
    student_data = {}
    company_data = {}
    
    if role == "student":
        st.subheader("Student Details")
        student_data["first_name"] = st.text_input("First name").strip()
        student_data["last_name"] = st.text_input("Last name").strip()
        student_data["university"] = st.text_input("University").strip()
        student_data["major"] = st.text_input("Major").strip()
        student_data["phone"] = st.text_input("Phone").strip()
    elif role == "company":
        st.subheader("Company Details")
        company_data["company_name"] = st.text_input("Company name").strip()
        company_data["industry"] = st.text_input("Industry").strip()
        company_data["location"] = st.text_input("Location").strip()
        company_data["phone"] = st.text_input("Phone").strip()
    

    if st.button("Submit", use_container_width=True):
        try:
            if not email:
                st.error("Email is required.")
                return
            if not password:
                st.error("Password is required.")
                return
            if len(password) < 6:
                st.error("Password must be at least 6 characters long.")
                return
            
            if role == "student":
                if not student_data["first_name"] or not student_data["last_name"]:
                    st.error("First name and Last name are required.")
                    return
            else:
                if not company_data["company_name"]:
                    st.error("Company name is required.")
                    return
            
            with st.spinner("Creating your account..."):
                auth_res = supabase.auth.sign_up({"email": email, "password": password})
            
            if auth_res.user is None:
                st.error("Registration failed. Please try again or use a different email.")
                return
            
            user_id = auth_res.user.id
            
            supabase.table("users").insert({
                "id": user_id, "email": email, "role": role
            }).execute()
            
            if role == "student":
                student_data["id"] = user_id
                supabase.table("student_profiles").insert(student_data).execute()
            else:
                company_data["id"] = user_id
                supabase.table("company_profiles").insert(company_data).execute()
            
            st.success("Your account has been created! Please login.")
            st.session_state.page = 'login'
            st.rerun()
            
        except Exception as e:
            st.error("Registration error: Please try again or use a different email.")

    st.divider()
    st.subheader("Already have an account ?")
    if st.button("Go to Login", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()

def student_page():
    """display student dashboard"""
    st.title("Student Dashboard")
    
 
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.page = 'login'
        st.rerun()

def company_page():
    """display company dashboard"""
    st.title("Company Dashboard")
    

    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.page = 'login'
        st.rerun()

def main():
    # check if user is already authenticated
    if st.session_state.user is None:
        check_auth_status()
    
    # route to appropriate page based on authentication status
    if st.session_state.user:
        # user is logged in, determine their role and show appropriate page
        role = get_user_role(st.session_state.user.id)
        
        if role == "student":
            student_page()
        elif role == "company":
            company_page()
        else:
            st.error("Unable to determine user role. Please contact support.")
            if st.button("Logout"):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.page = 'login'
                st.rerun()
    else:
        # user is not logged in, show login or register page
        if st.session_state.page == 'login':
            login_page()
        elif st.session_state.page == 'register':
            register_page()
 

if __name__ == "__main__":
    main()