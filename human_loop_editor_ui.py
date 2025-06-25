import streamlit as st

def editor_ui():
    st.title("Human-in-the-loop-Editor")

    content = st.text_area("Ai-Generated-content:", height=300)
    if st.button("Save-Final-Version"):
        with open("output/finalversion.txt","w",encoding="utf-8") as f:
            f.write(content)
        st.success("Final-Version-Saved")

if __name__=="__main__":
    editor_ui()          