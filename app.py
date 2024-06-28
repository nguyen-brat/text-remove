import streamlit as st
import os
import subprocess
import zipfile
import io
import shutil
import time

def run_bash_script(input_image_path, output_path, progress_placeholder):
    bash_command = f"bash config/text_detection.sh -s {input_image_path} -t {output_path}"
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    progress = 0
    for line in process.stdout:
        st.text(line.strip())
        progress += 0.1
        progress_placeholder.progress(min(progress, 1.0))
    
    rc = process.wait()
    return rc

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

st.title("Text Detection App")

uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Create a temporary directory for processing
    temp_dir = "temp_processing"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save the uploaded file temporarily
    input_path = os.path.join(temp_dir, "input")
    os.makedirs(input_path, exist_ok=True)
    input_file_path = os.path.join(input_path, uploaded_file.name)
    with open(input_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    output_path = os.path.join(temp_dir, "output")
    
    if st.button("Run Text Detection"):
        progress_placeholder = st.empty()
        status_text = st.empty()
        
        try:
            status_text.text("Running text detection...")
            rc = run_bash_script(input_path, output_path, progress_placeholder)
            
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
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Clean up temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)
            progress_placeholder.empty()
            status_text.empty()

st.write("Note: The download button will appear after running text detection.")