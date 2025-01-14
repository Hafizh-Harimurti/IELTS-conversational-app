import os
import tkinter as tk
from tkinter import messagebox
import requests
import threading
from urllib.parse import urlencode

from .api_handler import APIHandler
from .audio_player import AudioPlayer
from .audio_recorder import AudioRecorder
from .uploader import FileUploader

from dotenv import load_dotenv

load_dotenv()

# from api_conversation_prototype import compo_marking_ielts_conversation_examiner_first_question_api, compo_marking_ielts_conversation_examiner_response_api

# Initialize API handler, recorder, and file uploader

## Initialize API
api_handler = APIHandler(base_url="https://ielts-prototype.azurewebsites.net/api", params=urlencode({"code":os.getenv("AZURE_FUNCTION_AUTH_KEY")}))

player = AudioPlayer()
recorder = AudioRecorder()
uploader = FileUploader()

question_statement = "Part 1 - Introduction and Interview"
question_topics = ["Your town/village", "Accommodation"]
questions = [
    [
      "What kind of place is your town/village?",
      "What's the most interesting part of your town/village?",
      "What kind of jobs do the people in your town/village do?",
      "Would you say it's a good place to live? (Why?)"
    ],
    [
      "Tell me about the kind of accommodation you live in?",
      "How long have you lived there?",
      "What do you like about living there?",
      "What sort of accommodation would you most like to live in?"
    ]
]
current_topic_index = 0
current_question_index = 0

answer_urls = [[],[]]

def app_startup():
    def startup_thread():
        try:
            # Update status label
            status_label.config(text="Retrieving initial audio... Please wait.")

            # Retrieve the initial audio
            data = {
                "question_topic": question_topics[0],
                "question": questions[0][0]
            }
            response = api_handler.submit_data("get-first-audio", data)
            # response = compo_marking_ielts_conversation_examiner_first_question_api(**data)
            
            # Retrieve audio from the URL
            player.retrieve_audio_from_url(response["next_question_audio"], on_audio_player_retrieve)

            # Enable all buttons after retrieval
            question_buttons[0].config(state="normal",command=player.play_audio)
            speak_btn.config(state="normal")
            submit_btn.config(state="normal")
            status_label.config(text="Retrieving audio...")
            topic_label.config(text=f"Topic: {question_topics[0]}")
        except Exception as e:
            # Handle errors
            status_label.config(text="Failed to retrieve initial audio. Please restart the app.")
            print(f"Error during initial audio retrieval: {e}")
    thread = threading.Thread(target=startup_thread)
    thread.start()


def toggle_recording():
    """Toggle between starting and stopping the recording."""
    if recorder.is_recording:
        recorder.stop_recording()
        speak_btn.config(text="Speak", bg="SystemButtonFace")
        submit_btn.config(state="normal")
        question_buttons[current_question_index].config(state="normal")
        status_label.config(text="Recording stopped.")
    else:
        recorder.start_recording()
        speak_btn.config(text="Stop", bg="red")
        submit_btn.config(state="disabled")
        question_buttons[current_question_index].config(state="disabled")
        status_label.config(text="Recording started...")

def on_audio_player_retrieve(status):
    """
    Updates the UI based on the status callback.
    :param status: Current status of audio retrieval
    """
    global current_topic_index, current_question_index
    if status == "retrieving":
        status_label.config(text="Retrieving response...")
        speak_btn.config(state="disabled")  # Disable the button during upload
        submit_btn.config(state="disabled")  # Disable the button during upload
        question_buttons[current_question_index].config(state="disabled")
    elif status == "success":
        status_label.config(text="Response retrieval finished!")
        if current_topic_index == -1:
            player.play_audio()
        else:
            speak_btn.config(state="normal")  # Disable the button during upload
            submit_btn.config(state="normal")  # Disable the button during upload
            question_buttons[current_question_index].config(state="normal")
    else:
        status_label.config(text="Response retrieval failed. Try again.")
        speak_btn.config(state="normal")  # Disable the button during upload
        submit_btn.config(state="normal")  # Disable the button during upload
        question_buttons[current_question_index].config(state="normal")

def on_upload_status_update(status):
    """
    Updates the UI based on the status callback.
    :param status: Dictionary containing upload status and URL of uploaded file
                   {"is_uploading": boolean, "upload_success": boolean, "file_url": string}
    """
    global answer_urls
    is_uploading = status["is_uploading"]
    upload_success = status["upload_success"]
    file_url = status["file_url"]

    if is_uploading:
        status_label.config(text="Uploading... Please wait.")
        speak_btn.config(state="disabled")  # Disable the button during upload
        submit_btn.config(state="disabled")  # Disable the button during upload
        question_buttons[current_question_index].config(state="disabled")
    elif upload_success:
        status_label.config(text="Upload completed successfully! Generating and retrieving response...")
        answer_urls[current_topic_index].append(file_url)
        submit_data()
    else:
        status_label.config(text="Upload failed. Try again.")
        speak_btn.config(state="normal")  # Re-enable the button
        submit_btn.config(state="normal")  # Re-enable the button
        question_buttons[current_question_index].config(state="normal")

def submit_data():
    global question_statement, question_topics, questions, current_topic_index, current_question_index, answer_urls
    global question_buttons
    data = {
        "question_statement": question_statement,
        "question_topics": question_topics,
        "questions": questions,
        "question_topic_index": current_topic_index,
        "question_index": current_question_index,
        "audio": answer_urls[current_topic_index][current_question_index]
    }
    try:
        response = api_handler.submit_data("get-examiner-response", data)
        # response = compo_marking_ielts_conversation_examiner_response_api(**data)
        player.retrieve_audio_from_url(response["next_question_audio"],on_audio_player_retrieve)
        if response["next_question_topic_index"] != -1:
            next_btn = question_buttons[response["next_question_index"]]

            # Enable the next button, if any
            next_btn.config(state="normal", command=lambda: player.play_audio())
            current_question_index = response["next_question_index"]
            current_topic_index = response["next_question_topic_index"]
            topic_label.config(text=f"Topic: {question_topics[current_topic_index]}")
            speak_btn.config(state="normal")  # Re-enable the button
            submit_btn.config(state="normal")  # Re-enable the button
        else:
            current_question_index = response["next_question_index"]
            current_topic_index = response["next_question_topic_index"]
    except Exception as e:
        print(str(e))
        question_buttons[current_question_index].config(state="normal")
        speak_btn.config(state="normal")  # Re-enable the button
        submit_btn.config(state="normal")  # Re-enable the button
        status_label.config(text="Response generation failed. Try again.")

def submit_question():
    """Submit the question data and enable the next question button."""
    global current_question_index, answer_urls

    speak_btn.config(state="disabled")  # Re-enable the button
    submit_btn.config(state="disabled")  # Re-enable the button

    if len(answer_urls[current_topic_index]) == current_question_index:
        uploader.upload_fileobj(recorder.audio_buffer,on_upload_status_update)
    
    else:
        submit_data()

# Create the main window
app = tk.Tk()
app.title("IELTS Conversational Prototype")

# Configure a scalable grid
app.grid_rowconfigure(0, weight=1)  # Row for Question 1
app.grid_rowconfigure(1, weight=1)  # Row for Question 2
app.grid_rowconfigure(2, weight=1)  # Row for Question 3
app.grid_rowconfigure(3, weight=1)  # Row for Question 4
app.grid_rowconfigure(4, weight=1)  # Row for Submit Button
app.grid_rowconfigure(5, weight=1)  # Row for Status Label

app.grid_columnconfigure(0, weight=1)  # Column for Question Buttons
app.grid_columnconfigure(1, weight=1)  # Column for Speak and Submit Buttons

# Create buttons for speak and submit
speak_btn = tk.Button(app, text="Speak", width=10, state="disabled", command=toggle_recording)
submit_btn = tk.Button(app, text="Submit", width=10, state="disabled", command=submit_question)

# Create question buttons
question1_btn = tk.Button(app, text="Question 1", width=15, state="disabled")
question2_btn = tk.Button(app, text="Question 2", width=15, state="disabled")
question3_btn = tk.Button(app, text="Question 3", width=15, state="disabled")
question4_btn = tk.Button(app, text="Question 4", width=15, state="disabled")

question_buttons = [question1_btn, question2_btn, question3_btn, question4_btn]

# Layout all the widgets
question1_btn.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
question2_btn.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
question3_btn.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
question4_btn.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

speak_btn.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
submit_btn.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

# Add a topic label
topic_label = tk.Label(app, text="Topic:", anchor="center", fg="black")
topic_label.grid(row=4, column=0, columnspan=2, sticky="nsew")

# Add a status label at the bottom
status_label = tk.Label(app, text="Generating first audio...", anchor="center", fg="blue")
status_label.grid(row=5, column=0, columnspan=2, sticky="nsew")

# Generate the first question audio

app_startup()

# Run the application
app.mainloop()
