import streamlit as st
import os
import json
from sqlalchemy import create_engine, inspect

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="DB Metadata Extractor",
    layout="wide"
)

st.title("SQLite Database Metadata Extractor")

uploaded_file = st.file_uploader(
    "Upload SQLite Database (.db)",
    type=["db"]
)

if uploaded_file:

    db_path = os.path.join(
        UPLOAD_FOLDER,
        uploaded_file.name
    )

    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Database Uploaded Successfully")

    if st.button("Generate Metadata JSON"):

        try:

            engine = create_engine(
                f"sqlite:///{db_path}"
            )

            inspector = inspect(engine)

            metadata = {}

            for table in inspector.get_table_names():

                metadata[table] = {
                    "columns": [],
                    "primary_keys": inspector.get_pk_constraint(table),
                    "foreign_keys": inspector.get_foreign_keys(table)
                }

                for column in inspector.get_columns(table):

                    metadata[table]["columns"].append(
                        {
                            "name": column["name"],
                            "type": str(column["type"]),
                            "nullable": column["nullable"]
                        }
                    )

            json_path = os.path.join(
                OUTPUT_FOLDER,
                "metadata.json"
            )

            with open(json_path, "w") as f:
                json.dump(
                    metadata,
                    f,
                    indent=4
                )

            st.success(
                "Metadata Generated Successfully"
            )

            st.json(metadata)

            with open(json_path, "rb") as f:

                st.download_button(
                    label="Download JSON",
                    data=f,
                    file_name="metadata.json",
                    mime="application/json"
                )

        except Exception as e:

            st.error(str(e))