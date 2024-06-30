import streamlit as st
import os
from os.path import join as osp
import subprocess
import zipfile
import io
import shutil
import time
import sys
from PIL import Image
import tempfile

os.environ["HYDRA_FULL_ERROR"] = "1"

def run_bash_script(input_image_path, output_path, progress_placeholder, status_text):
    bash_command = f"bash config/text_detection.sh -s {input_image_path} -t {output_path}"
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    progress = 0
    for line in process.stdout:
        st.text(line.strip())
        progress += 0.1
        progress_placeholder.progress(min(progress, 1.0))
    
    stderr_output = process.stderr.read()
    if stderr_output:
        status_text.error("Error output:")
        st.code(stderr_output, language="bash")
    
    rc = process.wait()
    return rc, stderr_output

def zip_result_files(result_folder):
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(result_folder):
            for file in files:
                if file.endswith(".png"):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, result_folder)
                    zip_file.write(file_path, arcname)
    
    return zip_buffer

def create_temp_structure():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create test_folder
    test_folder = os.path.join(temp_dir, "test_folder")
    os.makedirs(test_folder, exist_ok=True)
    
    # Create target_folder with mask and result subdirectories
    target_folder = os.path.join(temp_dir, "target_folder")
    os.makedirs(os.path.join(target_folder, "mask"), exist_ok=True)
    os.makedirs(os.path.join(target_folder, "result"), exist_ok=True)
    os.makedirs(os.path.join(target_folder, "bbox"), exist_ok=True)
    
    return temp_dir, test_folder, target_folder

def clear_temp_folder(temp_dir):
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
        st.success("Temporary files have been cleared.")

st.title("Text Detection App")

# Use session state to store the temporary directory path
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = None

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Create a temporary directory for processing if it doesn't exist
    if not st.session_state.temp_dir:
        temp_dir, input_path, output_path = create_temp_structure()
        st.session_state.temp_dir = temp_dir
        st.session_state.input_path = input_path
        st.session_state.output_path = output_path
    else:
        temp_dir = st.session_state.temp_dir
        input_path = st.session_state.input_path
        output_path = st.session_state.output_path

    st.write(f"Temp dir: {temp_dir}")

    input_file_path = os.path.join(input_path, uploaded_file.name)
    image = Image.open(uploaded_file)
    image.save(input_file_path)
    
    if st.button("Run Text Detection"):
        progress_placeholder = st.empty()
        status_text = st.empty()
        
        try:
            status_text.text("Running text detection...")
            rc, stderr_output = run_bash_script(input_path, output_path, progress_placeholder, status_text)
            if rc == 0:
                status_text.text("Text detection completed successfully!")
                result_folder = os.path.join(output_path, "result")
                if os.path.exists(result_folder):
                    st.write("You can now download the results.")
                    
                    # Add download button
                    zip_buffer = zip_result_files(result_folder)
                    st.download_button(
                        label="Download Results",
                        data=zip_buffer.getvalue(),
                        file_name="text_detection_results.zip",
                        mime="application/zip",
                        on_click=lambda: clear_temp_folder(st.session_state.temp_dir)
                    )
                else:
                    st.error("Result folder not found. The text detection might have failed.")
            else:
                st.error(f"Text detection failed with return code {rc}")
                if stderr_output:
                    st.error("Error details:")
                    st.code(stderr_output, language="bash")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            progress_placeholder.empty()
            status_text.empty()

    # Display directory contents for debugging
    if st.session_state.temp_dir:
        st.write(f"Contents of temp directory:")
        for root, dirs, files in os.walk(st.session_state.temp_dir):
            level = root.replace(st.session_state.temp_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            st.write(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                st.write(f"{subindent}{f}")

st.write("Note: The download button will appear after running text detection.")