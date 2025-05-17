import runpod
import subprocess
import os
import json
import shutil # For optional cleanup

# Ensure this path matches your project structure
INFERENCE_SCRIPT_PATH = "/app/Music-Source-Separation-Training/inference.py"

def run_command_and_stream_output(command_list, log_file_path=None, job=None, progress_prefix=""):
    """
    Executes a shell command, streams its output line by line, logs it,
    and optionally sends progress updates to RunPod.
    Cleans carriage returns for better log display.
    """
    print(f"Executing command: {' '.join(command_list)}")
    process = subprocess.Popen(
        command_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Merge stderr to stdout
        text=True,
        bufsize=1,  # Line-buffered
        universal_newlines=True # Ensure text mode works across platforms
    )

    output_lines = []
    log_f = None
    if log_file_path:
        log_f = open(log_file_path, 'a') # Append mode

    try:
        for line in iter(process.stdout.readline, ''):
            # Clean the line: remove carriage returns and leading/trailing whitespace
            cleaned_line = line.replace('\r', '').strip()
            if cleaned_line: # Only process non-empty lines
                print(cleaned_line) # Stream to RunPod worker logs
                output_lines.append(cleaned_line)
                if log_f:
                    log_f.write(cleaned_line + '\n') # Write cleaned line to log file
                
                if job:
                    # For verbose commands like S3 sync without --quiet, this might send many updates.
                    # Consider adding logic to send updates less frequently if needed (e.g., every Nth line, or on specific keywords).
                    runpod.serverless.progress_update(job, f"{progress_prefix}: {cleaned_line}")
    finally:
        if log_f:
            log_f.close()
        process.stdout.close()
        
    return_code = process.wait()
    if return_code != 0:
        print(f"Command failed with exit code {return_code}: {' '.join(command_list)}")
        print("Captured output before failure (last 10 lines):")
        for l in output_lines[-10:]: 
            print(l)
            
    return return_code, output_lines

def handler(job):
    job_id = job.get("id", "unknown_job_id")
    job_input = job.get("input", {})

    print(f"Starting job: {job_id}")
    print(f"Job input: {json.dumps(job_input)}")

    input_s3_prefix = job_input.get("input_s3_prefix")
    output_s3_prefix = job_input.get("output_s3_prefix")

    if not input_s3_prefix or not output_s3_prefix:
        return {"error": "Missing 'input_s3_prefix' or 'output_s3_prefix' in job input."}

    # Get configuration from environment variables
    # These should be set in your RunPod template/Dockerfile
    model_type = os.environ.get("MODEL_TYPE")
    config_path = os.environ.get("CONFIG_PATH")
    checkpoint_path = os.environ.get("CHECKPOINT_PATH")
    local_input_dir = os.environ.get("LOCAL_INPUT_DIR", "/app/input")
    local_output_dir = os.environ.get("LOCAL_OUTPUT_DIR", "/app/output")

    if not all([model_type, config_path, checkpoint_path]):
        return {"error": "Environment variables MODEL_TYPE, CONFIG_PATH, CHECKPOINT_PATH must be set."}

    # Create unique subdirectories for this job to avoid collisions if multiple jobs run
    # This is good practice, though RunPod usually isolates jobs.
    # For simplicity here, we'll use the main dirs, assuming worker is refreshed or handles one job at a time.
    # If not, consider:
    # job_specific_input_dir = os.path.join(local_input_dir, job_id)
    # job_specific_output_dir = os.path.join(local_output_dir, job_id)
    # For now, using shared dirs that should be cleaned.
    
    # Clean and ensure local directories exist
    if os.path.exists(local_input_dir):
        shutil.rmtree(local_input_dir)
    os.makedirs(local_input_dir, exist_ok=True)
    
    if os.path.exists(local_output_dir):
        shutil.rmtree(local_output_dir)
    os.makedirs(local_output_dir, exist_ok=True)
    
    run_log_path = os.path.join(local_output_dir, f"runpod_job_{job_id}_run.log")
    inference_log_path = os.path.join(local_output_dir, f"inference_{job_id}_run.log")

    with open(run_log_path, 'w') as f:
        f.write(f"RunPod Job ID: {job_id}\n")
        f.write(f"Input Payload: {json.dumps(job_input)}\n")
        f.write(f"Local Input Dir: {local_input_dir}\n")
        f.write(f"Local Output Dir: {local_output_dir}\n")
        f.write(f"--- Start of Job Processing ---\n")

    try:
        runpod.serverless.progress_update(job, "Job accepted. Starting processing...")

        # 1. Download input files from S3
        runpod.serverless.progress_update(job, f"Downloading from {input_s3_prefix} to {local_input_dir} (verbose)...")
        s3_sync_down_cmd = ["aws", "s3", "sync", input_s3_prefix, local_input_dir] # Removed --quiet
        return_code, _ = run_command_and_stream_output(s3_sync_down_cmd, run_log_path, job, "S3 Download")
        if return_code != 0:
            return {"error": f"Failed to download from S3 (source: {input_s3_prefix}). Check logs.", "job_log_s3_path": f"{output_s3_prefix}/runpod_job_{job_id}_run.log (attempted)"}
        
        if not os.listdir(local_input_dir): # Check after potential verbose output
            empty_dir_msg = f"No files found in {local_input_dir} after S3 sync from {input_s3_prefix}."
            print(empty_dir_msg)
            with open(run_log_path, 'a') as f_log: # Log this specific error
                f_log.write(f"ERROR: {empty_dir_msg}\n")
            return {"error": empty_dir_msg}
        runpod.serverless.progress_update(job, "S3 Download complete.")

        # 2. Run inference
        runpod.serverless.progress_update(job, "Starting inference...")
        inference_cmd = [
            "python3", "-u", INFERENCE_SCRIPT_PATH,
            "--model_type", model_type,
            "--config_path", config_path,
            "--start_check_point", checkpoint_path,
            "--input_folder", local_input_dir,
            "--store_dir", local_output_dir
        ]
        return_code, _ = run_command_and_stream_output(inference_cmd, inference_log_path, job, "Inference")
        if os.path.exists(inference_log_path):
            with open(run_log_path, 'a') as main_log, open(inference_log_path, 'r') as inf_log:
                main_log.write("\n--- Inference Log Start ---\n")
                main_log.write(inf_log.read())
                main_log.write("\n--- Inference Log End ---\n")

        if return_code != 0:
            return {"error": "Inference script failed. Check logs.", "job_log_s3_path": f"{output_s3_prefix}/runpod_job_{job_id}_run.log (attempted)"}
        runpod.serverless.progress_update(job, "Inference complete.")

        # 3. Post-process local output directory (TBD)
        # =====================================================================
        # TODO: Implement post-processing of files in local_output_dir if needed.
        # For example, renaming files, generating a manifest, etc.
        # This logic could be in a separate script or Python functions here.
        # Example:
        # post_process_script = "/app/scripts/post_process.py"
        # if os.path.exists(post_process_script):
        #     runpod.serverless.progress_update(job, "Starting post-processing...")
        #     post_process_cmd = ["python3", post_process_script, "--directory", local_output_dir]
        #     rc, _ = run_command_and_stream_output(post_process_cmd, run_log_path, job, "Post-Process")
        #     if rc != 0:
        #         return {"error": "Post-processing script failed. Check logs."}
        #     runpod.serverless.progress_update(job, "Post-processing complete.")
        # else:
        #     print("No post-processing script found or configured. Skipping.")
        # =====================================================================
        runpod.serverless.progress_update(job, "Post-processing step (if any) skipped/completed.")

        # 4. Upload results (including logs) to S3
        runpod.serverless.progress_update(job, f"Uploading results from {local_output_dir} to {output_s3_prefix} (verbose)...")
        s3_sync_up_cmd = ["aws", "s3", "sync", local_output_dir, output_s3_prefix] # Removed --quiet
        return_code, _ = run_command_and_stream_output(s3_sync_up_cmd, run_log_path, job, "S3 Upload")
        if return_code != 0:
            return {"error": f"Failed to upload results to S3 (destination: {output_s3_prefix}). Some logs might be lost."}
        runpod.serverless.progress_update(job, "S3 Upload complete.")

        with open(run_log_path, 'a') as f:
            f.write(f"--- End of Job Processing ---\nJob completed successfully.\n")
            
        return {
            "status": "success",
            "message": "Processing complete. Output (including logs) uploaded to S3.",
            "output_s3_prefix": output_s3_prefix,
            "job_log_s3_path": f"{output_s3_prefix}/{os.path.basename(run_log_path)}",
            "inference_log_s3_path": f"{output_s3_prefix}/{os.path.basename(inference_log_path)}",
            # "refresh_worker": True # Optional: Uncomment if you want to refresh the worker after each job
        }

    except Exception as e:
        error_message = f"Unhandled exception in handler: {str(e)}"
        print(error_message) # To RunPod worker logs
        # Try to log to file as well
        if os.path.exists(os.path.dirname(run_log_path)): # Check if log dir exists for run_log_path
             with open(run_log_path, 'a') as f:
                f.write(f"CRITICAL ERROR in handler: {error_message}\n")
        
        # Attempt to upload logs even on failure
        if output_s3_prefix and os.path.exists(local_output_dir) and os.listdir(local_output_dir): # Check if output dir has content
            print(f"Attempting to upload logs/output from {local_output_dir} to {output_s3_prefix} after error (verbose)...")
            s3_sync_up_cmd_on_error = ["aws", "s3", "sync", local_output_dir, output_s3_prefix] # Removed --quiet
            run_command_and_stream_output(s3_sync_up_cmd_on_error) # Best effort

        return {"error": error_message, "job_log_s3_path": f"{output_s3_prefix}/{os.path.basename(run_log_path)} (attempted)"}
    finally:
        # Optional cleanup can be added here if refresh_worker is not True or for other reasons
        pass

if __name__ == "__main__":
    print("Starting RunPod serverless worker...")
    # You can provide a custom configuration for runpod.serverless.start if needed,
    # e.g., concurrency controls, though defaults are often fine to start.
    runpod.serverless.start({
        "handler": handler
    })
