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

# Direct document head manipulation
st.html("""
    <script>
        window.top.document.title = "Bugpedia 🪲";
        
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

# Custom Cottagecore / Botanical & Bookish TOC CSS Styling
st.markdown("""
    <style>
    .bug-card {
        background-color: #E3ECE2;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #C86D51;
        margin-bottom: 25px;
    }
    img {
        border-radius: 14px !important;
    }
    h1, h2, h3 {
        color: #3D3A37 !important;
        font-weight: 600;
    }
    
    /* Table of Contents Book Styling */
    .toc-title {
        text-align: center;
        letter-spacing: 4px;
        font-family: 'Georgia', serif;
        font-size: 1.8rem;
        color: #3D3A37;
        margin-top: 10px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .toc-divider {
        border-top: 2px solid #C86D51;
        width: 80%;
        margin: 0 auto 30px auto;
    }
    .toc-container {
        font-family: 'Georgia', serif;
        max-width: 650px;
        margin: 0 auto;
    }
    .toc-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 1.05rem;
        color: #3D3A37;
    }
    .toc-dots {
        flex-grow: 1;
        border-bottom: 2px dotted #C86D51;
        margin: 0 8px;
        position: relative;
        top: -4px;
        opacity: 0.6;
    }
    .toc-date {
        white-space: nowrap;
        padding-left: 8px;
        font-style: italic;
        color: #6B6560;
    }
    
    /* Clean text-style link for TOC items */
    div[data-testid="stColumn"] button[kind="tertiary"] {
        padding: 0 !important;
        font-family: 'Georgia', serif !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: #3D3A37 !important;
        background: transparent !important;
        border: none !important;
        text-align: left !important;
        line-height: inherit !important;
        box-shadow: none !important;
    }
    div[data-testid="stColumn"] button[kind="tertiary"]:hover {
        color: #C86D51 !important;
        text-decoration: underline !important;
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

# Fetch all bug entries
response = (
    supabase.table("bugs")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)
bugs = response.data or []

# Build sidebar menu choices dynamically
nav_options = ["📖 Table of Contents", "➕ Add New Entry"]
bug_menu_map = {}

for bug in bugs:
    sidebar_label = f"🪲 {bug['name']}"
    nav_options.append(sidebar_label)
    bug_menu_map[sidebar_label] = bug

# Initialize session state navigation if not set
if "nav_selection" not in st.session_state:
    st.session_state.nav_selection = "📖 Table of Contents"

# Navigation Sidebar
st.sidebar.title("📌 Journal Menu")
selected_option = st.sidebar.radio(
    "Go to:", 
    nav_options, 
    index=nav_options.index(st.session_state.nav_selection) if st.session_state.nav_selection in nav_options else 0,
    key="nav_selection"
)


# Helper function to extract image list
def get_image_list(bug_data):
    raw_images = bug_data.get("image_url") or []
    if isinstance(raw_images, str):
        try:
            parsed = json.loads(raw_images)
            return parsed if isinstance(parsed, list) else [raw_images]
        except Exception:
            return [raw_images] if raw_images else []
    elif isinstance(raw_images, list):
        return raw_images
    return []


# Helper function to format date consistently as "July 3, 2026"
def format_date_str(raw_date):
    if not raw_date:
        return "Unknown Date"
    try:
        if isinstance(raw_date, str):
            parsed_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d").date()
        else:
            parsed_date = raw_date
        return parsed_date.strftime("%B %d, %Y").replace(" 0", " ")
    except Exception:
        return str(raw_date)


# Helper function to display entry details & edit form
def display_bug_details(selected_bug):
    st.markdown(f"### {selected_bug['name']}")
    if selected_bug.get("species"):
        st.caption(f"*Scientific name: {selected_bug['species']}*")

    if selected_bug.get("category"):
        st.write(f"**Category:** {selected_bug['category']}")

    if selected_bug.get("location"):
        st.write(f"**📍 Location:** {selected_bug['location']}")

    if selected_bug.get("date_spotted"):
        formatted_date = format_date_str(selected_bug["date_spotted"])
        st.write(f"**Date First Spotted:** {formatted_date}")

    image_list = get_image_list(selected_bug)
    if image_list:
        st.markdown("#### 📷 Photos")
        if len(image_list) == 1:
            st.image(image_list[0], use_container_width=True)
        else:
            cols = st.columns(min(len(image_list), 3))
            for i, img_url in enumerate(image_list):
                with cols[i % 3]:
                    st.image(img_url, use_container_width=True)

    st.markdown("#### 📝 Field Notes")
    st.write(selected_bug["notes"] if selected_bug.get("notes") else "No notes added.")

    st.divider()

    # Edit section
    with st.expander("✏️ Edit This Entry"):
        with st.form(f"edit_bug_form_{selected_bug['id']}"):
            edit_name = st.text_input("Common Name", value=selected_bug.get("name", ""))
            edit_species = st.text_input("Scientific Name", value=selected_bug.get("species", ""))

            current_cat = selected_bug.get("category", CATEGORY_OPTIONS[0])
            cat_index = CATEGORY_OPTIONS.index(current_cat) if current_cat in CATEGORY_OPTIONS else 0
            edit_category = st.selectbox("Category", CATEGORY_OPTIONS, index=cat_index)

            edit_location = st.text_input("Location 📍", value=selected_bug.get("location", ""))

            existing_date = selected_bug.get("date_spotted")
            try:
                default_date = datetime.datetime.strptime(existing_date, "%Y-%m-%d").date() if existing_date else datetime.date.today()
            except Exception:
                default_date = datetime.date.today()

            edit_date = st.date_input("Date First Spotted 📅", value=default_date)
            
            new_photos = st.file_uploader(
                "Add Additional Photos (Optional)", 
                type=["jpg", "jpeg", "png"], 
                accept_multiple_files=True
            )
            
            edit_notes = st.text_area("Field Notes", value=selected_bug.get("notes", ""))

            update_submitted = st.form_submit_button("💾 Save Changes")

            if update_submitted:
                try:
                    existing_urls = get_image_list(selected_bug)

                    if new_photos:
                        for photo in new_photos:
                            file_bytes = photo.read()
                            clean_filename = edit_name.lower().replace(" ", "_")
                            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                            file_path = f"public/{clean_filename}_{timestamp}.jpg"

                            supabase.storage.from_("bug-photos").upload(
                                path=file_path,
                                file=file_bytes,
                                file_options={"content-type": photo.type, "upsert": "true"},
                            )
                            new_url = supabase.storage.from_("bug-photos").get_public_url(file_path)
                            existing_urls.append(new_url)

                    supabase.table("bugs").update({
                        "name": edit_name,
                        "species": edit_species,
                        "category": edit_category,
                        "location": edit_location,
                        "date_spotted": str(edit_date),
                        "image_url": existing_urls,
                        "notes": edit_notes,
                    }).eq("id", selected_bug["id"]).execute()

                    st.success("Entry updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating entry: {e}")


# ---------------- PAGE 1: TABLE OF CONTENTS (DEFAULT HOMEPAGE) ----------------
if selected_option == "📖 Table of Contents":
    st.markdown('<div class="toc-title">Table of Contents</div>', unsafe_allow_html=True)
    st.markdown('<div class="toc-divider"></div>', unsafe_allow_html=True)

    if not bugs:
        st.info("No entries added yet! Select '➕ Add New Entry' in the sidebar to make your first entry.")
    else:
        st.markdown('<div class="toc-container">', unsafe_allow_html=True)
        
        for bug in bugs:
            bug_name = bug.get("name", "Unnamed Entry")
            formatted_date = format_date_str(bug.get("date_spotted"))
            sidebar_label = f"🪲 {bug_name}"

            # 2 columns: Column 1 holds the clickable name, Column 2 holds dots + date
            col1, col2 = st.columns([0.45, 0.55], vertical_alignment="bottom")

            with col1:
                # Text button acting as direct link
                if st.button(bug_name, key=f"toc_link_{bug['id']}", type="tertiary"):
                    st.session_state.nav_selection = sidebar_label
                    st.rerun()

            with col2:
                # Leader dots and formatted date
                st.markdown(f"""
                    <div class="toc-row">
                        <span class="toc-dots"></span>
                        <span class="toc-date">{formatted_date}</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PAGE 2: ADD NEW ENTRY ----------------
elif selected_option == "➕ Add New Entry":
    st.subheader("Add a New Field Entry")

    with st.form("bug_entry_form", clear_on_submit=True):
        name = st.text_input("Common Name", placeholder="e.g., Monarch Butterfly, Amanita Muscaria")
        species = st.text_input("Scientific Name (Optional)", placeholder="e.g., Danaus plexippus")
        category = st.selectbox("Category", CATEGORY_OPTIONS)

        location = st.text_input("Location 📍", placeholder="e.g., Backyard Garden, Oak Creek Trail")
        date_spotted = st.date_input("Date First Spotted 📅", value=datetime.date.today())
        
        photos = st.file_uploader("Upload Bug/Plant/Fungi Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        notes = st.text_area("Field Notes & Wikipedia Summary", placeholder="Notes on habitat, behavior, or facts...")

        submitted = st.form_submit_button("✨ Save to Journal")

        if submitted:
            if name and photos:
                try:
                    uploaded_image_urls = []
                    
                    for index, photo in enumerate(photos):
                        file_bytes = photo.read()
                        clean_filename = name.lower().replace(" ", "_")
                        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                        file_path = f"public/{clean_filename}_{timestamp}_{index}.jpg"

                        supabase.storage.from_("bug-photos").upload(
                            path=file_path,
                            file=file_bytes,
                            file_options={
                                "content-type": photo.type,
                                "upsert": "true",
                            },
                        )

                        img_url = supabase.storage.from_("bug-photos").get_public_url(file_path)
                        uploaded_image_urls.append(img_url)

                    supabase.table("bugs").insert({
                        "name": name,
                        "species": species,
                        "category": category,
                        "location": location,
                        "date_spotted": str(date_spotted),
                        "image_url": uploaded_image_urls,
                        "notes": notes,
                    }).execute()

                    st.success(f"🌱 '{name}' has been added with {len(uploaded_image_urls)} photo(s)!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving entry: {e}")
            else:
                st.warning("Please provide at least a Name and at least one Photo!")

# ---------------- PAGE 3: INDIVIDUAL VIEW (FROM SIDEBAR OR TOC) ----------------
elif selected_option in bug_menu_map:
    selected_bug = bug_menu_map[selected_option]
    display_bug_details(selected_bug)
