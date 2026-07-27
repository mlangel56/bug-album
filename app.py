import datetime
import json
import streamlit as st
from supabase import Client, create_client

# Page Configuration
st.set_page_config(
    page_title="Bugpedia 🪲",
    page_icon="🪲",
    layout="centered"
)

# Direct document head manipulation (breaks out of Streamlit iframe)
st.html("""
    <script>
        // Update browser document title
        window.top.document.title = "Bugpedia 🪲";
        
        // Dynamically insert/update manifest tag in parent window head
        const manifestObj = {
            "name": "Bugpedia 🪲",
            "short_name": "Bugpedia 🪲",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#FAF6EE",
            "theme_color": "#C86D51",
            "icons": [{
                "src": "https://em-content.zobj.net/source/apple/354/bug_1f41b.png",
                "sizes": "192x192",
                "type": "image/png"
            }]
        };
        
        const stringManifest = JSON.stringify(manifestObj);
        const blob = new Blob([stringManifest], {type: 'application/json'});
        const manifestUrl = URL.createObjectURL(blob);
        
        let linkTag = window.top.document.querySelector('link[rel="manifest"]');
        if (!linkTag) {
            linkTag = window.top.document.createElement('link');
            linkTag.rel = 'manifest';
            window.top.document.head.appendChild(linkTag);
        }
        linkTag.href = manifestUrl;
    </script>
""")

# Custom Cottagecore / Botanical CSS Styling
st.markdown("""
    <style>
    /* Card container styling */
    .bug-card {
        background-color: #E3ECE2;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #C86D51;
        margin-bottom: 25px;
    }
    /* Rounded images */
    img {
        border-radius: 14px !important;
    }
    /* Soft header styling */
    h1, h2, h3 {
        color: #3D3A37 !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Master list of category options
CATEGORY_OPTIONS = [
    "Butterfly/Moth 🦋",
    "Beetle 🐞",
    "Bee/Wasp 🐝",
    "Spider 🕷️",
    "Fungi 🍄",
    "Plants 🪴",
    "Other 🌿",
]

# Initialize Supabase Client using Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# App Header
st.title("🌿 Bugpedia 🪲")
st.caption("A cottagecore collection of local insects, fungi, plants, photos & notes")

# Fetch all bug entries for dynamic sidebar building
response = (
    supabase.table("bugs")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)
bugs = response.data or []

# Build sidebar menu choices dynamically
nav_options = ["📖 Table of Contents", "➕ Add New Bug"]
bug_menu_map = {}

for bug in bugs:
    sidebar_label = f"🪲 {bug['name']}"
    nav_options.append(sidebar_label)
    bug_menu_map[sidebar_label] = bug

# Navigation Sidebar
st.sidebar.title("📌 Journal Menu")
selected_option = st.sidebar.radio("Go to:", nav_options)


# Helper function to display entry details & edit form
def display_bug_details(selected_bug):
    st.markdown(f"### {selected_bug['name']}")
    if selected_bug.get("species"):
        st.caption(f"*Scientific name: {selected_bug['species']}*")

    if selected_bug.get("category"):
        st.write(f"**Category:** {selected_bug['category']}")

    # Location Display
    if selected_bug.get("location"):
        st.write(f"**📍 Location:** {selected_bug['location']}")

    # Formatted Date Display
    if selected_bug.get("date_spotted"):
        raw_date = selected_bug["date_spotted"]
        try:
            if isinstance(raw_date, str):
                parsed_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
            else:
                parsed_date = raw_date
            formatted_date = parsed_date.strftime("%B %d, %Y").replace(" 0", " ")
        except Exception:
            formatted_date = raw_date
        st.write(f"**Date First Spotted:** {formatted_date}")

    if selected_bug.get("image_url"):
        st.image(selected_bug["image_url"], use_container_width=True)

    st.markdown("#### 📝 Field Notes")
    st.write(selected_bug["notes"] if selected_bug.get("notes") else "No notes added.")

    st.divider()

    # Edit section
    with st.expander("✏️ Edit This Entry"):
        with st.form(f"edit_bug_form_{selected_bug['id']}"):
            edit_name = st.text_input("Bug Common Name", value=selected_bug.get("name", ""))
            edit_species = st.text_input("Scientific Name", value=selected_bug.get("species", ""))

            current_cat = selected_bug.get("category", CATEGORY_OPTIONS[0])
            cat_index = CATEGORY_OPTIONS.index(current_cat) if current_cat in CATEGORY_OPTIONS else 0
            edit_category = st.selectbox("Category", CATEGORY_OPTIONS, index=cat_index)

            # Location Edit Field
            edit_location = st.text_input("Location 📍", value=selected_bug.get("location", ""))

            existing_date = selected_bug.get("date_spotted")
            try:
                default_date = datetime.datetime.strptime(existing_date, "%Y-%m-%d").date() if existing_date else datetime.date.today()
            except Exception:
                default_date = datetime.date.today()

            edit_date = st.date_input("Date First Spotted 📅", value=default_date)
            edit_notes = st.text_area("Field Notes", value=selected_bug.get("notes", ""))

            update_submitted = st.form_submit_button("💾 Save Changes")

            if update_submitted:
                try:
                    supabase.table("bugs").update({
                        "name": edit_name,
                        "species": edit_species,
                        "category": edit_category,
                        "location": edit_location,
                        "date_spotted": str(edit_date),
                        "notes": edit_notes,
                    }).eq("id", selected_bug["id"]).execute()

                    st.success("Entry updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating entry: {e}")


# ---------------- PAGE 1: ADD NEW BUG ----------------
if selected_option == "➕ Add New Bug":
    st.subheader("Add a New Field Entry")

    with st.form("bug_entry_form", clear_on_submit=True):
        name = st.text_input("Bug Common Name", placeholder="e.g., Monarch Butterfly")
        species = st.text_input("Scientific Name (Optional)", placeholder="e.g., Danaus plexippus")
        category = st.selectbox("Category", CATEGORY_OPTIONS)

        location = st.text_input("Location 📍", placeholder="e.g., Backyard Garden, Oak Creek Trail")
        date_spotted = st.date_input("Date First Spotted 📅", value=datetime.date.today())
        photo = st.file_uploader("Upload Bug Photo", type=["jpg", "jpeg", "png"])
        notes = st.text_area("Field Notes & Wikipedia Summary", placeholder="Notes on habitat, behavior, or facts...")

        submitted = st.form_submit_button("✨ Save to Journal")

        if submitted:
            if name and photo:
                try:
                    file_bytes = photo.read()
                    clean_filename = name.lower().replace(" ", "_")
                    file_path = f"public/{clean_filename}.jpg"

                    supabase.storage.from_("bug-photos").upload(
                        path=file_path,
                        file=file_bytes,
                        file_options={
                            "content-type": photo.type,
                            "upsert": "true",
                        },
                    )

                    image_url = supabase.storage.from_("bug-photos").get_public_url(file_path)

                    supabase.table("bugs").insert({
                        "name": name,
                        "species": species,
                        "category": category,
                        "location": location,
                        "date_spotted": str(date_spotted),
                        "image_url": image_url,
                        "notes": notes,
                    }).execute()

                    st.success(f"🌱 '{name}' has been added to your field guide!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving entry: {e}")
            else:
                st.warning("Please provide at least a Bug Name and a Photo!")

# ---------------- PAGE 2: TABLE OF CONTENTS ----------------
elif selected_option == "📖 Table of Contents":
    st.subheader("Entries Overview")

    if not bugs:
        st.info("No entries added yet! Select '➕ Add New Bug' in the sidebar to make your first entry.")
    else:
        bug_names = [b["name"] for b in bugs]
        selected_bug_name = st.selectbox("Select an entry to view:", bug_names)
        selected_bug = next(b for b in bugs if b["name"] == selected_bug_name)

        display_bug_details(selected_bug)

# ---------------- PAGE 3: INDIVIDUAL BUG VIEW (FROM SIDEBAR) ----------------
elif selected_option in bug_menu_map:
    selected_bug = bug_menu_map[selected_option]
    display_bug_details(selected_bug)
