import os
import shutil
import google.generativeai as genai
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    print("Please create a .env file with your GEMINI_API_KEY.")
    # We don't exit here immediately to allow the user to see the message, 
    # but the API calls will fail later if not fixed.

def setup_gemini():
    """Configures the Gemini model with tools."""
    if API_KEY:
        genai.configure(api_key=API_KEY)
    
    # Define the tools
    tools = [find_files, organize_files]
    
    # Initialize model with tools
    # Using gemini-flash-latest as 1.5-flash was not found in the available models list
    model = genai.GenerativeModel('gemini-flash-latest', tools=tools)
    return model

def find_files(file_extension: str, search_path: str = "C:/") -> list[str]:
    """
    Finds all files with a specific extension in a given directory and its subdirectories.
    
    Args:
        file_extension: The extension to look for (e.g., 'pdf', 'txt'). 
                        Case insensitive. Do not include the dot.
        search_path: The root directory to start the search from. Defaults to C:/
                     Be careful with full C:/ scans, they can be slow.
    
    Returns:
        A list of absolute paths to the found files. Returns up to 50 files to avoid overwhelming the model.
    """
    print(f"\n[Robot] Searching for '{file_extension}' files in '{search_path}'...")
    
    found_files = []
    # Clean extension
    ext = file_extension.lower().lstrip('.')
    
    # Safety Check: limit recursiveness or notify user if scanning root
    if search_path.rstrip('/\\').endswith(':'):
        print(f"[Robot] Warning: Scanning entire drive {search_path}. This might take a while.")
    
    try:
        # Use glob for recursive search
        # Note: 'recursive=True' with '**' works in newer python versions
        search_pattern = os.path.join(search_path, f"**/*.{ext}")
        
        # Using iglob to be cleaner on memory, but glob.glob is fine for simple scripts
        # Limit to 50 for safety in this demo
        count = 0
        for file_path in glob.iglob(search_pattern, recursive=True):
            found_files.append(os.path.abspath(file_path))
            count += 1
            if count >= 50:
                print(f"[Robot] Found 50+ files, stopping search to keep output manageable.")
                break
                
    except Exception as e:
        return [f"Error during search: {str(e)}"]

    if not found_files:
        return [f"No files with extension .{ext} found in {search_path}"]
        
    print(f"[Robot] Found {len(found_files)} files.")
    return found_files

def organize_files(file_extension: str, source_path: str, target_folder_name: str) -> str:
    """
    Moves all files of a certain extension from a source path (recursive) into a single target folder.
    
    Args:
        file_extension: The extension of files to move (e.g., 'pdf').
        source_path: Where to look for files to move.
        target_folder_name: The name of the new folder to put files into.
                            This folder will be created inside the source_path.
        
    Returns:
        A status message describing what was done.
    """
    print(f"\n[Robot] Organizing: Moving all '.{file_extension}' files from '{source_path}' to '{target_folder_name}'...")
    
    # 1. Find the files first
    files_to_move = find_files(file_extension, source_path)
    
    # Check if find_files returned an error-like list
    if files_to_move and files_to_move[0].startswith("Error") or files_to_move[0].startswith("No files"):
        return files_to_move[0]

    # 2. Create target directory
    target_dir = os.path.join(source_path, target_folder_name)
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            print(f"[Robot] Created directory: {target_dir}")
        except Exception as e:
            return f"Failed to create target directory: {str(e)}"
    
    # 3. Move files
    moved_count = 0
    errors = []
    
    for file_path in files_to_move:
        # Skip if already in target dir to avoid issues
        if os.path.dirname(file_path) == os.path.abspath(target_dir):
            continue
            
        filename = os.path.basename(file_path)
        destination = os.path.join(target_dir, filename)
        
        # Handle duplicate filenames
        if os.path.exists(destination):
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination):
                destination = os.path.join(target_dir, f"{base}_{counter}{extension}")
                counter += 1
        
        try:
            shutil.move(file_path, destination)
            moved_count += 1
            print(f"  Moved: {filename}")
        except Exception as e:
            errors.append(f"Failed to move {filename}: {str(e)}")
            
    result_msg = f"Successfully moved {moved_count} files to {target_dir}."
    if errors:
        result_msg += f"\nErrors encountered: {'; '.join(errors)}"
        
    return result_msg

import time

def chat_session():
    model = setup_gemini()
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    print("---------------------------------------------------------")
    print("🤖 Gemini File System Robot Initialized!")
    print("I can help you find and organize files.")
    print("Example commands:")
    print(" - 'Find all PDFs in C:/Users/Rakesh/Documents'")
    print(" - 'Move all text files in my current folder to a folder named Archive'")
    print("Type 'exit' to quit.")
    print("---------------------------------------------------------")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        try:
            # Simple retry loop for quota errors
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = chat.send_message(user_input)
                    print(f"Robot: {response.text}")
                    break # Success, exit retry loop
                    
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str:
                        retry_count += 1
                        wait_time = 10 * retry_count
                        print(f"Rate limit hit. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        raise e # Re-raise other errors
            
            if retry_count >= max_retries:
                print("Error: Could not get a response after multiple retries due to rate limits.")
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not API_KEY:
         print("⚠️  WARNING: API Key missing. Please set GEMINI_API_KEY in .env file.")
    chat_session()
