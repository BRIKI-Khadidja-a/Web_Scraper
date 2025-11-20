import streamlit as st
from supabase import create_client
import os
import base64
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "register"


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
    """retrieve user role from database"""
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
    st.markdown(
        """
    Sign in to access your personalized dashboard and continue your journey with us.
    """
    )

    email = st.text_input("Email", key="login_email").strip()
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Submit", use_container_width=True):
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        try:
            with st.spinner("Logging in..."):
                auth_res = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )

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
        st.session_state.page = "register"
        st.rerun()


def register_page():
    """display registration page"""
    st.title("Get Started Today 🚀")

    st.markdown(
        """
    ### Are you a student searching for internships or a company building your team?
    
    Join our platform to unlock new opportunities. Students can explore internships tailored 
    to their skills and career goals, while companies connect with motivated candidates who 
    bring fresh ideas and enthusiasm to the workplace.
    """
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "**👨‍🎓 Students**: Create a profile, browse internships, and apply to opportunities that match your skills and interests."
        )
    with col2:
        st.info(
            "**🏢 Companies**: Post internship positions, review applications, and connect with top student talent."
        )

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
                st.error(
                    "Registration failed. Please try again or use a different email."
                )
                return

            user_id = auth_res.user.id

            supabase.table("users").insert(
                {"id": user_id, "email": email, "role": role}
            ).execute()

            if role == "student":
                student_data["id"] = user_id
                supabase.table("student_profiles").insert(student_data).execute()
            else:
                company_data["id"] = user_id
                supabase.table("company_profiles").insert(company_data).execute()

            st.success("Your account has been created! Please login.")
            st.session_state.page = "login"
            st.rerun()

        except Exception as e:
            st.error("Registration error: Please try again or use a different email.")

    st.divider()
    st.subheader("Already have an account ?")
    if st.button("Go to Login", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()


def student_page():
    """Display the student dashboard with internship listings and application flow"""
    if "user" not in st.session_state or not st.session_state.user:
        st.error("You must be logged in to view this page.")
        return

    user_id = st.session_state.user.id

    # Sidebar actions
    with st.sidebar:
        st.header("Student Menu")
        st.caption("Browse internships and track your applications.")
        if st.button("🚪 Logout", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    # Fetch student profile for personalization
    profile_data = None
    try:
        profile_res = (
            supabase.table("student_profiles").select("*").eq("id", user_id).execute()
        )
        profile_data = profile_res.data[0] if profile_res.data else None
    except Exception as e:
        st.warning(f"Unable to load profile information: {str(e)}")

    first_name = profile_data["first_name"] if profile_data else "Student"
    st.title(f"👋 Welcome back, {first_name}!")
    if profile_data:
        st.caption(
            f"{profile_data.get('major', 'N/A')} · {profile_data.get('university', 'Unknown University')}"
        )

    st.divider()

    # Load internships and existing applications
    try:
        internships_res = (
            supabase.table("internships")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        internships = internships_res.data or []
    except Exception as e:
        st.error(f"Unable to load internships: {str(e)}")
        return

    try:
        applications_res = (
            supabase.table("applications")
            .select("*")
            .eq("student_id", user_id)
            .execute()
        )
        applications = {app["internship_id"]: app for app in (applications_res.data or [])}
    except Exception as e:
        st.warning(f"Unable to load your applications: {str(e)}")
        applications = {}

    # Fetch company data for labels
    company_map = {}
    company_ids = list({internship["company_id"] for internship in internships})
    if company_ids:
        try:
            companies_res = (
                supabase.table("company_profiles")
                .select("id, company_name, location, phone")
                .in_("id", company_ids)
                .execute()
            )
            company_map = {company["id"]: company for company in (companies_res.data or [])}
        except Exception as e:
            st.warning(f"Unable to load company details: {str(e)}")

    # Filters
    col_search, col_type, col_location = st.columns([2, 1, 1])
    search_query = col_search.text_input(
        "🔍 Search internships", placeholder="Search by title, company or location"
    ).strip()
    job_type_filter = col_type.selectbox("Work type", ["All", "on-site", "remote", "hybrid"])
    locations = sorted({i["location"] for i in internships if i.get("location")})
    location_filter = col_location.selectbox("Location", ["All"] + locations) if locations else "All"

    def matches_filters(internship):
        if search_query:
            company = company_map.get(internship["company_id"], {})
            target = " ".join(
                [
                    internship.get("title", ""),
                    internship.get("location", ""),
                    company.get("company_name", ""),
                ]
            ).lower()
            if search_query.lower() not in target:
                return False
        if job_type_filter != "All" and internship.get("job_type") != job_type_filter:
            return False
        if location_filter != "All" and internship.get("location") != location_filter:
            return False
        return True

    filtered_internships = [internship for internship in internships if matches_filters(internship)]

    st.subheader(f"Available Internships ({len(filtered_internships)})")
    if not filtered_internships:
        st.info("No internships match your filters yet. Try adjusting your search.")
        return

    for internship in filtered_internships:
        company = company_map.get(internship["company_id"], {})
        application = applications.get(internship["id"])
        with st.container():
            st.markdown(f"### {internship['title']} · {company.get('company_name', 'Company')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"📍 {internship.get('location', 'N/A')}")
                st.caption(f"🧭 Duration: {internship.get('duration', 'N/A')}")
            with col2:
                st.caption(f"🛠️ Type: {internship.get('job_type', 'N/A')}")
                st.caption(f"💰 Salary: {internship.get('salary') or 'Not specified'}")
            with col3:
                if internship.get("spots_available"):
                    st.caption(f"👥 Spots: {internship['spots_available']}")
                if internship.get("application_deadline"):
                    st.caption(f"⏰ Apply before: {internship['application_deadline']}")

            st.write("**Description**")
            st.write(internship.get("description", "No description provided."))
            st.write("**Requirements**")
            st.write(internship.get("requirements", "No requirements provided."))

            if application:
                status = application.get("status", "pending").capitalize()
                st.success(f"You already applied · Status: {status}")
            else:
                with st.form(key=f"apply_form_{internship['id']}"):
                    cover_letter = st.text_area(
                        "Cover letter (optional)",
                        placeholder="Explain why you're a good fit for this internship.",
                        key=f"cover_{internship['id']}",
                    )
                    resume_file = st.file_uploader(
                        "Upload resume (PDF, optional)", type=["pdf"], key=f"resume_{internship['id']}"
                    )
                    submit = st.form_submit_button("📤 Apply now", use_container_width=True)

                    if submit:
                        resume_data = (
                            "\\x" + resume_file.read().hex() if resume_file else None
                        )
                        try:
                            supabase.table("applications").insert(
                                {
                                    "internship_id": internship["id"],
                                    "student_id": user_id,
                                    "cover_letter": cover_letter.strip() if cover_letter else None,
                                    "resume_pdf": resume_data,
                                    "status": "pending",
                                    "applied_at": datetime.utcnow().isoformat(),
                                }
                            ).execute()
                            st.success("Application submitted! 🎉")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Unable to submit application: {str(e)}")

            st.divider()


from datetime import datetime

from datetime import datetime


def company_page():
    """Display company dashboard with internship management"""

    # Get company profile
    user_id = st.session_state.user.id
    try:
        profile = (
            supabase.table("company_profiles").select("*").eq("id", user_id).execute()
        )
        company_name = profile.data[0]["company_name"] if profile.data else "Company"
    except:
        company_name = "Company"

    st.title(f"👔 {company_name} - Dashboard")

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        menu = st.radio(
            "",
            [
                "📊 Overview",
                "➕ Post New Internship",
                "📋 My Internships",
                "👥 Applications",
            ],
        )

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    # Route to appropriate section
    if menu == "📊 Overview":
        show_overview(user_id)
    elif menu == "➕ Post New Internship":
        show_post_internship_form()
    elif menu == "📋 My Internships":
        show_my_internships(user_id)
    elif menu == "👥 Applications":
        show_applications(user_id)


def show_overview(user_id):
    """Display overview statistics"""
    st.header("📊 Overview")

    try:
        # Get all internships for this company
        internships = (
            supabase.table("internships")
            .select("*")
            .eq("company_id", user_id)
            .execute()
        )
        total_internships = len(internships.data)

        # Tous les stages publiés sont actifs
        active_internships = total_internships

        # Get all applications for company's internships
        internship_ids = [i["id"] for i in internships.data]
        if internship_ids:
            applications = (
                supabase.table("applications")
                .select("*")
                .in_("internship_id", internship_ids)
                .execute()
            )
            total_applications = len(applications.data)
            pending_applications = len(
                [a for a in applications.data if a["status"] == "pending"]
            )
        else:
            total_applications = 0
            pending_applications = 0

        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Internships", total_internships)
        with col2:
            st.metric("Total Applications", total_applications)
        with col3:
            st.metric("Pending Review", pending_applications)

        st.divider()

        # Recent applications
        if internship_ids and applications.data:
            st.subheader("🆕 Recent Applications")
            recent_apps = sorted(
                applications.data, key=lambda x: x["applied_at"], reverse=True
            )[:5]

            for app in recent_apps:
                internship = next(
                    (i for i in internships.data if i["id"] == app["internship_id"]),
                    None,
                )

                # Get student info
                try:
                    student = (
                        supabase.table("student_profiles")
                        .select("*")
                        .eq("id", app["student_id"])
                        .execute()
                    )
                    student_name = (
                        f"{student.data[0]['first_name']} {student.data[0]['last_name']}"
                        if student.data
                        else "Unknown"
                    )
                except:
                    student_name = "Unknown"

                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{student_name}**")
                        st.caption(
                            f"Applied for: {internship['title'] if internship else 'Unknown'}"
                        )
                    with col2:
                        st.caption(
                            f"📅 {datetime.fromisoformat(app['applied_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}"
                        )
                    with col3:
                        status_color = {
                            "pending": "🟡",
                            "reviewed": "🔵",
                            "accepted": "🟢",
                            "rejected": "🔴",
                            "withdrawn": "⚪",
                        }
                        st.write(
                            f"{status_color.get(app['status'], '⚪')} {app['status'].capitalize()}"
                        )
                    st.divider()
        else:
            st.info(
                "No applications yet. Post an internship to start receiving applications!"
            )

    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")


def show_post_internship_form():
    """Display form to post a new internship"""
    st.header("➕ Post New Internship")

    # Vérification que l'utilisateur est connecté
    if "user" not in st.session_state or not st.session_state.user:
        st.error("❌ You must be logged in to post an internship")
        return

    user_id = st.session_state.user.id

    with st.form("post_internship_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Job Title *", placeholder="e.g., Full-Stack Developer Intern"
            )
            location = st.text_input("Location *", placeholder="e.g., Alger, Algeria")
            duration = st.text_input("Duration *", placeholder="e.g., 3 months")
            salary = st.text_input(
                "Salary", placeholder="e.g., 15000 DA/month or Non rémunéré"
            )

        with col2:
            job_type = st.selectbox("Work Type *", ["on-site", "remote", "hybrid"])
            spots_available = st.number_input(
                "Positions Available *", min_value=1, value=1
            )
            start_date = st.date_input("Start Date")
            application_deadline = st.date_input("Application Deadline")

        description = st.text_area(
            "Description *",
            height=150,
            placeholder="Describe the internship role, responsibilities, and what the intern will learn...",
        )

        requirements = st.text_area(
            "Requirements *",
            height=150,
            placeholder="List the required skills, qualifications, and experience...",
        )

        submitted = st.form_submit_button(
            "📤 Post Internship", use_container_width=True
        )

        if submitted:
            # Validation des champs obligatoires
            if (
                not title
                or not location
                or not duration
                or not description
                or not requirements
            ):
                st.error("Please fill in all required fields marked with *")
                return

            # Validation des dates
            if (
                application_deadline
                and start_date
                and application_deadline > start_date
            ):
                st.error("Application deadline must be before the start date")
                return

            # Préparer les données à insérer
            internship_data = {
                "company_id": user_id,
                "title": title.strip(),
                "description": description.strip(),
                "requirements": requirements.strip(),
                "location": location.strip(),
                "duration": duration.strip(),
                "start_date": start_date.isoformat() if start_date else None,
                "application_deadline": (
                    application_deadline.isoformat() if application_deadline else None
                ),
                "salary": salary.strip() if salary else None,
                "job_type": job_type,
                "spots_available": spots_available,
            }

            try:
                # Insérer dans la base
                result = supabase.table("internships").insert(internship_data).execute()

                if result.data:
                    st.success("✅ Internship posted successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to post internship. Please try again.")

            except Exception as e:
                st.error(f"❌ Error posting internship: {str(e)}")


def show_my_internships(user_id):
    """Display and manage company's internships"""
    st.header("📋 My Internships")

    # Initialiser l'état d'édition
    if "editing_internship" not in st.session_state:
        st.session_state.editing_internship = None

    try:
        internships = (
            supabase.table("internships")
            .select("*")
            .eq("company_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        if not internships.data:
            st.info("You haven't posted any internships yet.")
            return

        # Display internships
        for internship in internships.data:
            # Calculer le nombre de candidatures
            applications_count = (
                supabase.table("applications")
                .select("id", count="exact")
                .eq("internship_id", internship["id"])
                .execute()
            )
            app_count = (
                applications_count.count if hasattr(applications_count, "count") else 0
            )

            is_editing = st.session_state.editing_internship == internship["id"]

            with st.expander(
                f"📌 {internship['title']} ({app_count} applications)",
                expanded=is_editing,
            ):

                # MODE ÉDITION
                if is_editing:
                    st.subheader("✏️ Modifier le stage")

                    with st.form(key=f"edit_form_{internship['id']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            edit_title = st.text_input(
                                "Titre *", value=internship["title"]
                            )
                            edit_location = st.text_input(
                                "Lieu *", value=internship["location"]
                            )
                            edit_duration = st.text_input(
                                "Durée *", value=internship["duration"]
                            )
                            edit_salary = st.text_input(
                                "Salaire", value=internship.get("salary") or ""
                            )

                        with col2:
                            current_type_index = ["on-site", "remote", "hybrid"].index(
                                internship["job_type"]
                            )
                            edit_job_type = st.selectbox(
                                "Type de travail *",
                                ["on-site", "remote", "hybrid"],
                                index=current_type_index,
                            )
                            edit_spots = st.number_input(
                                "Postes disponibles *",
                                min_value=1,
                                value=internship["spots_available"],
                            )

                            # Gestion des dates
                            start_date_value = None
                            if internship.get("start_date"):
                                try:
                                    start_date_value = datetime.fromisoformat(
                                        internship["start_date"]
                                    ).date()
                                except:
                                    pass
                            edit_start_date = st.date_input(
                                "Date de début", value=start_date_value
                            )

                            deadline_value = None
                            if internship.get("application_deadline"):
                                try:
                                    deadline_value = datetime.fromisoformat(
                                        internship["application_deadline"]
                                    ).date()
                                except:
                                    pass
                            edit_deadline = st.date_input(
                                "Date limite", value=deadline_value
                            )

                        edit_description = st.text_area(
                            "Description *", value=internship["description"], height=150
                        )
                        edit_requirements = st.text_area(
                            "Exigences *", value=internship["requirements"], height=150
                        )

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save_button = st.form_submit_button(
                                "💾 Sauvegarder",
                                use_container_width=True,
                                type="primary",
                            )
                        with col_cancel:
                            cancel_button = st.form_submit_button(
                                "❌ Annuler", use_container_width=True
                            )

                        if save_button:
                            if (
                                not edit_title
                                or not edit_location
                                or not edit_duration
                                or not edit_description
                                or not edit_requirements
                            ):
                                st.error(
                                    "Veuillez remplir tous les champs obligatoires marqués avec *"
                                )
                            elif (
                                edit_deadline
                                and edit_start_date
                                and edit_deadline > edit_start_date
                            ):
                                st.error(
                                    "La date limite doit être avant la date de début"
                                )
                            else:
                                try:
                                    updated_data = {
                                        "title": edit_title.strip(),
                                        "location": edit_location.strip(),
                                        "duration": edit_duration.strip(),
                                        "salary": (
                                            edit_salary.strip() if edit_salary else None
                                        ),
                                        "job_type": edit_job_type,
                                        "spots_available": edit_spots,
                                        "start_date": (
                                            edit_start_date.isoformat()
                                            if edit_start_date
                                            else None
                                        ),
                                        "application_deadline": (
                                            edit_deadline.isoformat()
                                            if edit_deadline
                                            else None
                                        ),
                                        "description": edit_description.strip(),
                                        "requirements": edit_requirements.strip(),
                                    }

                                    supabase.table("internships").update(
                                        updated_data
                                    ).eq("id", internship["id"]).execute()
                                    st.success("✅ Stage mis à jour avec succès!")
                                    st.session_state.editing_internship = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erreur lors de la mise à jour: {str(e)}")

                        if cancel_button:
                            st.session_state.editing_internship = None
                            st.rerun()

                # MODE AFFICHAGE
                else:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"📍 **Lieu:** {internship['location']}")
                        st.write(f"⏱️ **Durée:** {internship['duration']}")
                        st.write(f"💼 **Type:** {internship['job_type']}")
                        st.write(f"💰 **Salaire:** {internship['salary'] or 'N/A'}")

                    with col2:
                        st.write(f"👥 **Postes:** {internship['spots_available']}")
                        if internship.get("start_date"):
                            st.write(f"📅 **Début:** {internship['start_date']}")
                        if internship.get("application_deadline"):
                            st.write(
                                f"⏰ **Limite:** {internship['application_deadline']}"
                            )
                        st.write(
                            f"📆 **Publié:** {datetime.fromisoformat(internship['created_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}"
                        )

                    st.divider()
                    st.write("**Description:**")
                    st.write(internship["description"])

                    st.write("**Exigences:**")
                    st.write(internship["requirements"])

                    # Boutons d'action
                    st.divider()
                    col_edit, col_delete = st.columns(2)

                    with col_edit:
                        if st.button(
                            "✏️ Modifier",
                            key=f"edit_btn_{internship['id']}",
                            use_container_width=True,
                        ):
                            st.session_state.editing_internship = internship["id"]
                            st.rerun()

                    with col_delete:
                        # Double confirmation pour la suppression
                        delete_key = f"delete_confirm_{internship['id']}"
                        if delete_key not in st.session_state:
                            st.session_state[delete_key] = False

                        if not st.session_state[delete_key]:
                            if st.button(
                                "🗑️ Supprimer",
                                key=f"delete_btn_{internship['id']}",
                                type="secondary",
                                use_container_width=True,
                            ):
                                st.session_state[delete_key] = True
                                st.rerun()
                        else:
                            if st.button(
                                "⚠️ Confirmer suppression",
                                key=f"confirm_btn_{internship['id']}",
                                type="secondary",
                                use_container_width=True,
                            ):
                                try:
                                    supabase.table("internships").delete().eq(
                                        "id", internship["id"]
                                    ).execute()
                                    st.success("✅ Stage supprimé avec succès!")
                                    st.session_state[delete_key] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erreur lors de la suppression: {str(e)}")

    except Exception as e:
        st.error(f"Erreur lors du chargement des stages: {str(e)}")


def show_applications(user_id):
    """Display all applications for company's internships"""
    st.header("👥 Applications")

    try:
        internships = (
            supabase.table("internships")
            .select("*")
            .eq("company_id", user_id)
            .execute()
        )
        if not internships.data:
            st.info("You don't have any internships yet.")
            return

        internship_ids = [i["id"] for i in internships.data]
        applications = (
            supabase.table("applications")
            .select("*")
            .in_("internship_id", internship_ids)
            .order("applied_at", desc=True)
            .execute()
        )
        if not applications.data:
            st.info("No applications received yet.")
            return

        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            filter_internship = st.selectbox(
                "Filter by Internship", ["All"] + [i["title"] for i in internships.data]
            )
        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "pending", "reviewed", "accepted", "rejected", "withdrawn"],
            )

        st.divider()

        for app in applications.data:
            # Appliquer les filtres
            internship = next(
                (i for i in internships.data if i["id"] == app["internship_id"]), None
            )

            if (
                filter_internship != "All"
                and internship
                and internship["title"] != filter_internship
            ):
                continue
            if filter_status != "All" and app["status"] != filter_status:
                continue

            student = (
                supabase.table("student_profiles")
                .select("*")
                .eq("id", app["student_id"])
                .execute()
            )
            student_data = student.data[0] if student.data else {}
            student_name = f"{student_data.get('first_name', 'Unknown')} {student_data.get('last_name', '')}"

            with st.expander(
                f"👤 {student_name} - {internship['title'] if internship else 'Unknown'} ({app['status'].upper()})"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Student:** {student_name}")
                    st.write(f"**University:** {student_data.get('university', 'N/A')}")
                    st.write(f"**Major:** {student_data.get('major', 'N/A')}")
                    st.write(f"**Phone:** {student_data.get('phone', 'N/A')}")

                with col2:
                    st.write(
                        f"**Applied on:** {datetime.fromisoformat(app['applied_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')}"
                    )
                    st.write(f"**Status:** {app['status'].capitalize()}")
                    st.write(
                        f"**Internship:** {internship['title'] if internship else 'Unknown'}"
                    )

                st.divider()

                if app.get("cover_letter"):
                    st.write("**Cover Letter:**")
                    st.write(app["cover_letter"])

                st.divider()

                resume_data = app.get("resume_pdf")
                if resume_data:
                    try:
                        resume_bytes = None
                        if isinstance(resume_data, str) and resume_data.startswith("\\x"):
                            resume_bytes = bytes.fromhex(resume_data[2:])
                        else:
                            resume_clean = "".join(str(resume_data).split())
                            padding = len(resume_clean) % 4
                            if padding:
                                resume_clean += "=" * (4 - padding)
                            resume_bytes = base64.b64decode(resume_clean)
                        if resume_bytes:
                            st.download_button(
                                "⬇️ Download resume",
                                data=resume_bytes,
                                file_name=f"resume_{student_name.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                key=f"download_resume_{app['id']}",
                                use_container_width=True,
                            )
                    except Exception as e:
                        st.warning(f"Unable to render resume: {str(e)}")

                # Actions
                col_accept, col_reject, col_review = st.columns(3)
                with col_accept:
                    if st.button(
                        "✅ Accept", key=f"accept_{app['id']}", use_container_width=True
                    ):
                        try:
                            supabase.table("applications").update(
                                {"status": "accepted"}
                            ).eq("id", app["id"]).execute()
                            st.success("Application accepted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                with col_reject:
                    if st.button(
                        "❌ Reject", key=f"reject_{app['id']}", use_container_width=True
                    ):
                        try:
                            supabase.table("applications").update(
                                {"status": "rejected"}
                            ).eq("id", app["id"]).execute()
                            st.success("Application rejected!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                with col_review:
                    if st.button(
                        "🔍 Mark as Reviewed",
                        key=f"review_{app['id']}",
                        use_container_width=True,
                    ):
                        try:
                            supabase.table("applications").update(
                                {"status": "reviewed"}
                            ).eq("id", app["id"]).execute()
                            st.success("Marked as reviewed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"Error loading applications: {str(e)}")


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
                st.session_state.page = "login"
                st.rerun()
    else:
        # user is not logged in, show login or register page
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            register_page()


if __name__ == "__main__":
    main()
