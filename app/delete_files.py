from openai import OpenAI
import datetime
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
# Initialize the OpenAI client
client = OpenAI()

def upload_file():
    filename = input("Enter the filename to upload: ")
    assistant_id = input("Enter the assistant ID: ")
    try:
        with open(filename, "rb") as file:
            response = client.files.create(file=file, purpose="assistants", metadata={"assistant_id": assistant_id})
            print(response)
            print(f"File uploaded successfully: {response.filename} [{response.id}]")
    except FileNotFoundError:
        print("File not found. Please make sure the filename and path are correct.")


def list_files():
    assistant_id = input("Enter the assistant ID to list files: ")
    response = client.files.list(purpose="assistants")
    files = [file for file in response.data if file.metadata.get("assistant_id") == assistant_id]
    if len(response.data) == 0:
        print("No files found.")
        return
    for file in response.data:
        created_date = datetime.datetime.utcfromtimestamp(file.created_at).strftime('%Y-%m-%d')
        print(f"{file.filename} [{file.id}], Created: {created_date}")

def list_and_delete_file():
    assistant_id = input("Enter the assistant ID to list and delete files: ")
    while True:
        response = client.files.list(purpose="assistants")
        files = [file for file in response.data if file.metadata.get("assistant_id") == assistant_id]
        files = list(response.data)
        if len(files) == 0:
            print("No files found.")
            return
        for i, file in enumerate(files, start=1):
            created_date = datetime.datetime.utcfromtimestamp(file.created_at).strftime('%Y-%m-%d')
            print(f"[{i}] {file.filename} [{file.id}], Created: {created_date}")
        choice = input("Enter a file number to delete, or any other input to return to menu: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(files):
            return
        selected_file = files[int(choice) - 1]
        client.files.delete(selected_file.id)
        print(f"File deleted: {selected_file.filename}")

def delete_all_files():
    assistant_id = input("Enter the assistant ID to delete all files: ")
    confirmation = input(f"This will delete all OpenAI files with purpose 'assistants' for assistant ID '{assistant_id}'.\nType 'YES' to confirm: ")
    if confirmation == "YES":
        response = client.files.list(purpose="assistants")
        files = [file for file in response.data if file.metadata.get("assistant_id") == assistant_id]
        for file in files:
            client.files.delete(file.id)
        print(f"All files with purpose 'assistants' for assistant ID '{assistant_id}' have been deleted.")
    else:
        print("Operation cancelled.")

def main():
    while True:
        print("\n== Assistants file utility ==")
        print("[1] Upload file")
        print("[2] List all files")
        print("[3] List all and delete one of your choice")
        print("[4] Delete all assistant files (confirmation required)")
        print("[9] Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            upload_file()
        elif choice == "2":
            list_files()
        elif choice == "3":
            list_and_delete_file()
        elif choice == "4":
            delete_all_files()
        elif choice == "9":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()