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

def GET_PROJECT_ROOT():
    count = 0
    # goto the root folder of LogBar
    current_abspath = os.path.abspath(__file__)
    while True:
        if count > 1000:
            print("Can find root error")
            sys.exit()
        if os.path.split(current_abspath)[1] == 'text-remove':
            project_root = current_abspath
            break
        else:
            current_abspath = os.path.dirname(current_abspath)
    return project_root

def run_bash_script(input_image_path, output_path, progress_placeholder, status_text):
    bash_command = f"bash app/text-remove/config/text_detection.sh -s {input_image_path} -t {output_path}"
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    progress = 0
    for line in process.stdout:
        st.text(line.strip())
        progress += 0.1
        progress_placeholder.progress(min(progress, 1.0))
    
    # Capture and display stderr
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

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, ignore_errors=True)  # Remove directory and its contents
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
            
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
    
    return temp_dir, test_folder, target_folder

st.title("Text Detection App")
files = [f for f in os.listdir('.') if os.path.isfile(f)]
file_name = " || ".join(files)
st.write(file_name)
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Create a temporary directory for processing
    
    # Save the uploaded file temporarily
    _, input_path, output_path = create_temp_structure()
    # input_path = "test_folder"
    # output_path = "target_test"
    # os.makedirs(input_path, exist_ok=True)
    # os.makedirs(osp(output_path, "result"), exist_ok=True)
    # os.makedirs(osp(output_path, "mask"), exist_ok=True)

    input_file_path = os.path.join(input_path, uploaded_file.name)
    image = Image.open(uploaded_file)
    # image.save(os.path.join(PROJECT_ROOT, input_file_path))
    image.save(input_file_path)
    
    if st.button("Run Text Detection"):
        progress_placeholder = st.empty()
        status_text = st.empty()
        
        try:
            status_text.text("Running text detection...")
            #os.makedirs(input_path, exist_ok=True)
            #os.makedirs(osp(output_path, "result"), exist_ok=True)
            #os.makedirs(osp(output_path, "mask"), exist_ok=True)
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
                        mime="application/zip"
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
            # Clean up temporary files
            clear_folder(osp(output_path, "mask"))
            progress_placeholder.empty()
            status_text.empty()

st.write("Note: The download button will appear after running text detection.")