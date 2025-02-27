"""
This script allows users to debug Python code using the Gemini AI model.
File listing , custom file path 
Create v2 of selected file
Provide one line description of the file
queries -> debugging, suggestions, modification, error report
creates a changes file with the changes log
merge -> update original file
exit -> delete the new file

"""
"""
new features to be done

Github push pull 
UI 
"""




import os
import pathlib
from google import genai
from dotenv import load_dotenv
import requests
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, PhotoImage
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = input("Please enter your Gemini API key: ")
# Ask user for API key

# Initialize the Gemini client
lm_client = genai.Client(api_key=API_KEY)

# Hardcoded system instruction
sys_instruct = (
    "First, classify the user prompt into one of the following categories:\n"
    "1. General question about the program.\n"
    "2. Request to find all bugs in the program.\n"
    "3. Inquiry about a specific bug.\n"
    "4. Request for general suggestions about the program.\n"
    "5. Request to modify or fix part of the program.\n"
    "\nBased on the classification, structure the response accordingly, without explicitly mentioning the category.\n"
    "\nIf the prompt is a general question, provide a direct answer.\n"
    "If the prompt asks about all bugs, generate a structured debugging report including logical and syntax errors.\n"
    "If the prompt is about a specific bug, analyze only that part of the code and provide details.\n"
    "If the prompt requests general suggestions, provide improvements related to readability, efficiency, and maintainability.\n"
    "If the prompt asks for a modification or fix, identify the required change, ensure it does not alter the basic functionality of the program, and respond in the following format:\n"
    "\nError noticed: <Describe the issue>\n"
    "One-line solution: <Brief fix explanation>\n"
    "Code solution:\n"
    "```python\n"
    "<Modified code snippet>\n"
    "```\n"
    "Also, update the new version of the file with the corrected code and log all changes made."
    "\nWhen analyzing the code, use the following structured format:\n"
    "\n2. Errors Found:\n"
    "   - Logical Errors: Logical Error (N) (N = Number of logical errors detected)\n"
    "   - Syntax Errors: Syntax Error (M) (M = Number of syntax errors detected)\n"
    "   - Suggestions: Suggestion (S) (S = Number of suggestions for improvement)\n"
    "\n3. Error Details:\n"
    "   - For each error found, provide:\n"
    "     - Line Number: Where the error occurs.\n"
    "     - Error Type: (e.g., Logical Error, Syntax Error)\n"
    "     - Description: A short explanation of the issue.\n"
    "     - Solution: A concise fix for the issue.\n"
    "\n4. Code Improvement Suggestion (if applicable):\n"
    "   - If the script can be improved, briefly suggest an enhancement.\n"
    "\nEnsure that the response strictly follows this classification and format for clarity, conciseness, and actionability."
)

# Store conversation history
conversation_history = []

# Initialize the main window
root = tk.Tk()
root.title("Gemini AI Debugger")
root.geometry("800x600")  # Set initial size
root.resizable(True, True)  # Make the window size adjustable

# Set the app logo
logo_path = "logo.png"
logo = PhotoImage(file=logo_path)
root.iconphoto(False, logo)
# ...existing code...

# Create a text widget for displaying conversation history
conversation_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED)
conversation_text.pack(expand=True, fill=tk.BOTH)

# Create a scale widget for adjusting text size
def adjust_text_size(size):
    conversation_text.config(font=("TkDefaultFont", size))

text_size_scale = tk.Scale(root, from_=8, to=32, orient=tk.HORIZONTAL, label="Text Size", command=adjust_text_size)
text_size_scale.set(20)  # Set default text size
text_size_scale.pack(fill=tk.X)

# Create an entry widget for user input
user_input_entry = tk.Entry(root)
user_input_entry.pack(fill=tk.X)

# ...existing code...
def update_conversation(text):
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, text + "\n")
    conversation_text.config(state=tk.DISABLED)
    conversation_text.see(tk.END)

def get_user_input(prompt):
    update_conversation(prompt)
    user_input_entry.delete(0, tk.END)
    user_input_entry.focus()
    root.wait_variable(user_input_var)
    return user_input_var.get()

def show_message(title, message):
    update_conversation(f"{title}: {message}")

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        update_conversation(f"Selected file: {file_path}")
    return file_path
import os
import requests
import base64
from dotenv import load_dotenv

def github(file_path):
    """Handles listing, creating repositories, and uploading a file to GitHub."""
    
    # Load credentials from .env
    load_dotenv()
    github_user = os.getenv("Github_user")
    github_access_token = os.getenv("Github_accessToken")
    
    if not github_user or not github_access_token:
        show_message("Error", "Missing GitHub credentials in .env file.")
        return
    
    # GitHub API URL for listing repositories
    url = f"https://api.github.com/users/{github_user}/repos"
    headers = {
        "Authorization": f"token {github_access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repos = response.json()
        repo_names = [repo['name'] for repo in repos]
        repo_list = "\n".join([f"{i+1}. {repo}" for i, repo in enumerate(repo_names)])
        repo_list += f"\n{len(repo_names) + 1}. Create a new repository"

        choice = get_user_input(f"Your GitHub repositories:\n{repo_list}\n\nEnter the number of the repository you want to select:")
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(repo_names):
                selected_repo = repo_names[choice - 1]
                show_message("Selected Repository", f"Selected repository: {selected_repo}")
            elif choice == len(repo_names) + 1:
                new_repo_name = get_user_input("Enter the name of the new repository:")
                selected_repo = create_github_repository(new_repo_name, github_access_token)
                if not selected_repo:
                    return  # Exit if repo creation fails
            else:
                show_message("Error", "Invalid selection. Please enter a valid number.")
                return
        except ValueError:
            show_message("Error", "Invalid input. Please enter a number.")
            return
    else:
        show_message("Error", f"Unable to fetch repositories (Status Code: {response.status_code})")
        print(response.json())
        return

    # Upload the file to the selected repo
    upload_file_to_repo(selected_repo, file_path, github_user, github_access_token)


def create_github_repository(repo_name, github_access_token):
    """Creates a new GitHub repository and returns its name if successful."""
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"name": repo_name, "private": False}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        show_message("Repository Created", f"Repository '{repo_name}' created successfully.")
        return repo_name
    else:
        show_message("Error", f"Unable to create repository (Status Code: {response.status_code})")
        print(response.json())
        return None


def upload_file_to_repo(repo_name, file_path, github_user, github_access_token):
    """Uploads a file to the specified GitHub repository."""
    
    url = f"https://api.github.com/repos/{github_user}/{repo_name}/contents/{os.path.basename(file_path)}"

    with open(file_path, "rb") as file:
        content = base64.b64encode(file.read()).decode("utf-8")

    data = {
        "message": "Adding new file",
        "content": content,
        "branch": "main"
    }

    headers = {
        "Authorization": f"token {github_access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        show_message("File Uploaded", f"File uploaded successfully to {repo_name}.")
    else:
        show_message("Error", f"Unable to upload file (Status Code: {response.status_code})")
        print(response.json())


def list_only_files():
    cwd = os.getcwd()
    files = [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f))]
    file_list = "\n".join([f"{i+1}. {file}" for i, file in enumerate(files)])
    file_list += f"\n{len(files) + 1}. Provide my file path"
    choice = get_user_input(f"Files in the current directory:\n{file_list}\n\nEnter the number of the file you want to edit:")
    
    try:
        choice = int(choice)
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
        elif choice == len(files) + 1:
            selected_file = select_file()
            if not os.path.isfile(selected_file):
                show_message("Error", "Invalid file path. Please enter a valid file path.")
                return list_only_files()
        else:
            show_message("Error", "Invalid selection. Please enter a valid number.")
            return list_only_files()
    except ValueError:
        show_message("Error", "Invalid input. Please enter a number.")
        return list_only_files()
    
    # Create a copy of the selected file with _v2 suffix
    file_path = pathlib.Path(selected_file)
    new_file_name = f"{file_path.stem}_v2{file_path.suffix}"
    
    with open(selected_file, 'r') as original, open(new_file_name, 'w') as copy:
        copy.write(original.read())
    
    show_message("File Copied", f"A copy of '{selected_file}' has been created as '{new_file_name}'.")
    
    # Read file contents and ask LLM for a one-line description
    with open(new_file_name, 'r') as f:
        file_contents = f.read()
    
    # FIX: Pass correct number of arguments
    file_description = get_ai_response(file_contents, "Provide a one-line description of this Python script.", new_file_name, selected_file)
    
    show_message("File Description", f"\nSelected File: {selected_file} - {file_description}\n")
    
    return selected_file, new_file_name


def get_ai_response(python_code, user_input, new_file_name, selected_file):
    """Function to get AI response with system instruction and conversation history."""
    global conversation_history
    conversation_history.append(f"User: {user_input}")
    
    # Keep context manageable (limit last 5 exchanges)
    context = "\n".join(conversation_history[-5:])

    response = lm_client.models.generate_content(
        model="gemini-1.5-flash",
        config=genai.types.GenerateContentConfig(system_instruction=sys_instruct),
        contents=[python_code, context],
    )
    
    ai_response = response.text.strip()
    conversation_history.append(f"AI: {ai_response}")
    
    # If the response includes a code solution, update the new file and log changes
    if "```python" in ai_response:
        code_start = ai_response.find("```python") + 9
        code_end = ai_response.find("```", code_start)
        if code_end != -1:
            corrected_code = ai_response[code_start:code_end].strip()
            with open(new_file_name, 'w') as new_file:
                new_file.write(corrected_code)
            
            # Log changes in a separate file
            changes_file_name = f"{pathlib.Path(selected_file).stem}_changes.txt"
            with open(changes_file_name, 'w') as log_file:
                log_file.write(f"Changes made to {new_file_name}:\n\n")
                log_file.write(ai_response)
            show_message("File Updated", f"\nUpdated '{new_file_name}' with the corrected code. Changes logged in '{changes_file_name}'.")
    
    return ai_response

waiting_for_repo_number = False  # Add this global variable
def on_user_input(event=None):
    global waiting_for_repo_number, repo_names, new_python_code, selected_file, new_file_name  # Declare as global

    # Load GitHub credentials
    load_dotenv()
    github_user = os.getenv("Github_user")
    github_access_token = os.getenv("Github_accessToken")

    if not github_user or not github_access_token:
        show_message("Error", "Missing GitHub credentials in .env file.")
        return

    user_prompt = user_input_entry.get().strip()
    user_input_var.set(user_prompt)
    update_conversation(f"User: {user_prompt}")
    user_input_entry.delete(0, tk.END)
    
    if waiting_for_repo_number:
        # Handle repository number input
        try:
            choice = int(user_prompt)
            if 1 <= choice <= len(repo_names):
                selected_repo = repo_names[choice - 1]
                show_message("Selected Repository", f"Selected repository: {selected_repo}")
            elif choice == len(repo_names) + 1:
                new_repo_name = get_user_input("Enter the name of the new repository:")
                selected_repo = create_github_repository(new_repo_name, github_access_token)
                if not selected_repo:
                    return  # Exit if repo creation fails
            else:
                show_message("Error", "Invalid selection. Please enter a valid number.")
                return
        except ValueError:
            show_message("Error", "Invalid input. Please enter a number.")
            return
        
        # Upload the file to the selected repo
        upload_file_to_repo(selected_repo, new_file_name, github_user, github_access_token)
        waiting_for_repo_number = False  # Reset the flag
        return

    if user_prompt.lower() == "exit":
        delete_choice = get_user_input(f"Do you want to delete the new file '{new_file_name}'? (y/n):").strip().lower()
        if delete_choice == "y":
            os.remove(new_file_name)
            update_conversation("File Deleted: Deleted '{new_file_name}'.")
        update_conversation("Goodbye: Exiting the program. Goodbye! 👋")
        root.quit()
    elif user_prompt.lower() == "merge":
        with open(selected_file, 'w') as original, open(new_file_name, 'r') as new_file:
            original.write(new_file.read())
        update_conversation(f"Merge Complete: Merged contents into '{selected_file}'.")

    elif user_prompt.lower() == "commit":
        repo_names = list_github_repositories()  # Function to list repositories
        waiting_for_repo_number = True  # Set the flag to wait for repo number input

    else:
        ai_response = get_ai_response(new_python_code, user_prompt, new_file_name, selected_file)
        update_conversation(f" \n \n Debugging Report: {ai_response}")

def list_github_repositories():
    """Function to list GitHub repositories and return their names."""
    # Load credentials from .env
    load_dotenv()
    github_user = os.getenv("Github_user")
    github_access_token = os.getenv("Github_accessToken")
    
    if not github_user or not github_access_token:
        show_message("Error", "Missing GitHub credentials in .env file.")
        return []
    
    # GitHub API URL for listing repositories
    url = f"https://api.github.com/users/{github_user}/repos"
    headers = {
        "Authorization": f"token {github_access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repos = response.json()
        repo_names = [repo['name'] for repo in repos]
        repo_list = "\n".join([f"{i+1}. {repo}" for i, repo in enumerate(repo_names)])
        repo_list += f"\n{len(repo_names) + 1}. Create a new repository"

        update_conversation(f"Your GitHub repositories:\n{repo_list}\n\nEnter the number of the repository you want to select:")
        return repo_names
    else:
        show_message("Error", f"Unable to fetch repositories (Status Code: {response.status_code})")
        print(response.json())
        return []

def main():
    global user_input_var, new_python_code, selected_file, new_file_name  # Declare as global
    user_input_var = tk.StringVar()
    user_input_entry.bind("<Return>", on_user_input)
    selected_file, new_file_name = list_only_files()
    
    if selected_file and new_file_name:
        new_python_file = pathlib.Path(new_file_name)
        new_python_code = new_python_file.read_text()  # Assign to global variable
        
        update_conversation("Enter your debugging request ( type 'exit' to quit, 'merge' to update original file, 'commit' to commit the changes on github):")

if __name__ == "__main__":
    main()
    root.mainloop()