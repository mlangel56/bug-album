import streamlit as st
from supabase import create_client, Client

# Page Configuration
st.set_page_config(
    page_title="My Field Guide",
    page_icon="🪲",
    layout="centered"
)

# Custom Cottagecore / Botanical CSS Styling
st.markdown("""
    
""", unsafe_allow_html=True)

# Initialize Supabase Client using Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# App Header
st.title("🌿 My Bug Field Journal 🪲")
st.caption("A cottagecore collection of local insects, photos & notes")

# Navigation Sidebar
st.sidebar.title("📌 Journal Menu")
page = st.sidebar.radio("Go to:", ["📖 Table of Contents", "➕ Add New Bug"])

# ---------------- PAGE 1: ADD NEW BUG ----------------
if page == "➕ Add New Bug":
    st.subheader(" Add a New Field Entry")
    
    with st.form("bug_entry_form", clear_on_submit=True):
        name = st.text_input("Bug Common Name", placeholder="e.g., Monarch Butterfly")
        species = st.text_input("Scientific Name (Optional)", placeholder="e.g., Danaus plexippus")
        category = st.selectbox("Category", ["Butterfly/Moth 🦋", "Beetle 🐞", "Bee/Wasp 🐝", "Spider 🕷️", "Other 🌿"])
        photo = st.file_uploader("Upload Bug Photo", type=["jpg", "jpeg", "png"])
        notes = st.text_area("Field Notes & Wikipedia Summary", placeholder="Notes on habitat, behavior, or facts...")
        
        submitted = st.form_submit_button("✨ Save to Journal")
        
        if submitted:
            if name and photo:
                try:
                    # 1. Upload Photo to Supabase Storage Bucket
                    file_bytes = photo.read()
                    clean_filename = name.lower().replace(" ", "_")
                    file_path = f"public/{clean_filename}.jpg"
                    
                    supabase.storage.from_("bug-photos").upload(
                        path=file_path,
                        file=file_bytes,
                        file_options={"content-type": photo.type, "upsert": "true"}
                    )
                    
                    # 2. Retrieve Public Image URL
                    image_url = supabase.storage.from_("bug-photos").get_public_url(file_path)
                    
                    # 3. Save details to database
                    supabase.table("bugs").insert({
                        "name": name,
                        "species": species,
                        "category": category,
                        "image_url": image_url,
                        "notes": notes
                    }).execute()
                    
                    st.success(f"🌱 '{name}' has been added to your field guide!")
                except Exception as e:
                    st.error(f"Error saving entry: {e}")
            else:
                st.warning("Please provide at least a Bug Name and a Photo!")

# ---------------- PAGE 2: TABLE OF CONTENTS ----------------
elif page == "📖 Table of Contents":
    st.subheader(" Entries")
    
    # Fetch entries from database
    response = supabase.table("bugs").select("*").order("created_at", desc=True).execute()
    bugs = response.data
    
    if not bugs:
        st.info("No entries added yet! Select '➕ Add New Bug' in the sidebar to make your first entry.")
    else:
        bug_names = [b["name"] for b in bugs]
        selected_bug_name = st.selectbox("Select an entry to view:", bug_names)
        
        # Find selected entry
        selected_bug = next(b for b in bugs if b["name"] == selected_bug_name)
        
        st.markdown("
", unsafe_allow_html=True)
        
        # Display entry card
        st.markdown(f"### {selected_bug['name']}")
        if selected_bug.get("species"):
            st.caption(f"*Scientific name: {selected_bug['species']}*")
        if selected_bug.get("category"):
            st.write(f"**Category:** {selected_bug['category']}")
            
        if selected_bug.get("image_url"):
            st.image(selected_bug["image_url"], use_column_width=True)
            
        st.markdown("#### 📝 Field Notes")
        st.write(selected_bug["notes"] if selected_bug.get("notes") else "No notes added.")
