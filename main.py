import streamlit as st


def main():
    st.set_page_config(
        page_title="Pandoc Block Editor", layout="wide"
    )  # Set page title and layout
    st.title("Pandoc Block Editor")
    st.write("Welcome to the Pandoc Block Editor (Streamlit Version)")
    # Further UI and logic will be added here


if __name__ == "__main__":
    main()
