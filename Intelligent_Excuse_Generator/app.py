import os
import sys
import json
import random
import threading
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
import google.generativeai as genai
from deep_translator import GoogleTranslator
import speech_recognition as sr
import pyttsx3


ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

# Configure Gemini API
API_KEY = "Your_Gemini_API_Key"
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Path for excuse history
history_file = data_dir / "excuse_history.json"
favorites_file = data_dir / "favorites.json"

# Initialize history and favorites if they don't exist
if not history_file.exists():
    with open(history_file, "w") as f:
        json.dump([], f)

if not favorites_file.exists():
    with open(favorites_file, "w") as f:
        json.dump([], f)


class ExcuseGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.translator = GoogleTranslator()
        # Updated language codes dictionary with all supported languages from GoogleTranslator
        self.language_codes = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Arabic": "ar",
            "Chinese (Simplified)": "zh-CN",
            "Chinese (Traditional)": "zh-TW",
            "Dutch": "nl",
            "Greek": "el",
            "Hindi": "hi",
            "Japanese": "ja",
            "Korean": "ko",
            "Russian": "ru",
            "Swedish": "sv",
            "Turkish": "tr",
            "Ukrainian": "uk",
            "Vietnamese": "vi",
            "Polish": "pl",
            "Romanian": "ro",
            "Danish": "da",
            "Finnish": "fi",
            "Norwegian": "no",
            "Czech": "cs",
            "Hungarian": "hu",
            "Thai": "th"
        }
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.history = self.load_history()
        self.favorites = self.load_favorites()
        
    def load_history(self):
        try:
            with open(history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return []
    
    def load_favorites(self):
        try:
            with open(favorites_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading favorites: {e}")
            return []
    
    def save_history(self):
        try:
            with open(history_file, "w") as f:
                json.dump(self.history, f)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def save_favorites(self):
        try:
            with open(favorites_file, "w") as f:
                json.dump(self.favorites, f)
        except Exception as e:
            print(f"Error saving favorites: {e}")
    
    def generate_excuse(self, context, audience, formality, urgency):
        prompt = f"Generate a believable excuse for {context}. The audience is {audience}. "
        prompt += f"The tone should be {formality} and the urgency is {urgency}."
        
        try:
            response = self.model.generate_content(prompt)
            excuse = response.text
            
            # Save to history
            self.history.append({
                "excuse": excuse,
                "context": context,
                "audience": audience,
                "timestamp": datetime.datetime.now().isoformat(),
                "effectiveness": None  # To be rated later
            })
            self.save_history()
            
            return excuse
        except Exception as e:
            return f"Error generating excuse: {e}"
    
    def generate_proof(self, excuse_type, details):
        prompt = f"Generate a convincing proof for this excuse: {details}. "
        prompt += f"The type of proof needed is: {excuse_type}."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating proof: {e}"
    
    def generate_emergency_message(self, emergency_type, recipient):
        prompt = f"Generate an emergency message about {emergency_type} for {recipient}."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating emergency message: {e}"
    
    def generate_apology(self, situation, formality):
        prompt = f"Generate a {formality} apology for this situation: {situation}."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating apology: {e}"
    
    def translate_excuse(self, excuse, target_language):
        try:
            # Get the language code from the language_codes dictionary
            # If not found, use the target_language directly
            language_code = self.language_codes.get(target_language, target_language)
            
            # Initialize a new translator with source language as English and target as the specified language
            translator = GoogleTranslator(source='en', target=language_code)
            
            # Translate the text
            translation = translator.translate(excuse)
            return translation
        except Exception as e:
            return f"Error translating: {e}"
    
    def voice_to_text(self):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except Exception as e:
            return f"Error in speech recognition: {e}"
            
    def text_to_speech(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            return False
    
    def predict_excuse_needs(self):
        """Predict when excuses might be needed based on past patterns"""
        try:
            # Group excuses by day of week and time of day
            day_counts = {}
            hour_counts = {}
            context_counts = {}
            
            for entry in self.history:
                # Extract timestamp
                timestamp = datetime.datetime.fromisoformat(entry["timestamp"])
                day = timestamp.strftime("%A")  # Day of week
                hour = timestamp.hour
                context = entry["context"]
                
                # Count occurrences
                day_counts[day] = day_counts.get(day, 0) + 1
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
                context_counts[context] = context_counts.get(context, 0) + 1
            
            # Find most common day, time, and context
            most_common_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else "Monday"
            most_common_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 9
            most_common_context = max(context_counts.items(), key=lambda x: x[1])[0] if context_counts else "Work"
            
            # Calculate next occurrence of the most common day
            today = datetime.datetime.now()
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            today_day = today.strftime("%A")
            today_index = days_of_week.index(today_day)
            target_index = days_of_week.index(most_common_day)
            days_until = (target_index - today_index) % 7
            
            if days_until == 0 and today.hour > most_common_hour:
                days_until = 7  # Next week
                
            next_date = today + datetime.timedelta(days=days_until)
            next_date = next_date.replace(hour=most_common_hour, minute=0, second=0, microsecond=0)
            
            return {
                "next_predicted_date": next_date.isoformat(),
                "common_day": most_common_day,
                "common_hour": most_common_hour,
                "common_context": most_common_context
            }
        except Exception as e:
            print(f"Error predicting excuse needs: {e}")
            return None
    
    def rank_excuses(self, context, audience):
        # Filter history by similar context and audience
        relevant_excuses = [h for h in self.history if h["context"] == context and h["audience"] == audience]
        
        # Sort by effectiveness and recency
        rated_excuses = [e for e in relevant_excuses if e["effectiveness"] is not None]
        if rated_excuses:
            # Calculate a score based on effectiveness (70%) and recency (30%)
            now = datetime.datetime.now()
            for excuse in rated_excuses:
                # Calculate recency score (higher for more recent excuses)
                excuse_time = datetime.datetime.fromisoformat(excuse["timestamp"])
                days_old = (now - excuse_time).days + 1  # Add 1 to avoid division by zero
                recency_score = 10 / days_old  # Higher for more recent excuses
                
                # Calculate combined score (effectiveness + recency)
                excuse["score"] = (excuse["effectiveness"] * 0.7) + (recency_score * 0.3)
            
            # Sort by combined score
            sorted_excuses = sorted(rated_excuses, key=lambda x: x["score"], reverse=True)
            return sorted_excuses
        else:
            return []
    
    def add_to_favorites(self, excuse_data):
        self.favorites.append(excuse_data)
        self.save_favorites()
    
    def remove_from_favorites(self, excuse_index):
        if 0 <= excuse_index < len(self.favorites):
            del self.favorites[excuse_index]
            self.save_favorites()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Intelligent Excuse Generator")
        self.geometry("1100x700")
        
        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Initialize excuse generator
        self.excuse_generator = ExcuseGenerator()
        
        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(7, weight=1)
        
        # App logo/title
        self.logo_label = ctk.CTkLabel(
            self.navigation_frame, text="Excuse Generator", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.nav_btn_1 = ctk.CTkButton(
            self.navigation_frame, text="Generate Excuse",
            command=self.nav_to_generate_excuse
        )
        self.nav_btn_1.grid(row=1, column=0, padx=20, pady=10)
        
        self.nav_btn_2 = ctk.CTkButton(
            self.navigation_frame, text="Proof Generator",
            command=self.nav_to_proof_generator
        )
        self.nav_btn_2.grid(row=2, column=0, padx=20, pady=10)
        
        self.nav_btn_3 = ctk.CTkButton(
            self.navigation_frame, text="Emergency System",
            command=self.nav_to_emergency_system
        )
        self.nav_btn_3.grid(row=3, column=0, padx=20, pady=10)
        
        self.nav_btn_4 = ctk.CTkButton(
            self.navigation_frame, text="Apology Generator",
            command=self.nav_to_apology_generator
        )
        self.nav_btn_4.grid(row=4, column=0, padx=20, pady=10)
        
        self.nav_btn_5 = ctk.CTkButton(
            self.navigation_frame, text="History & Favorites",
            command=self.nav_to_history
        )
        self.nav_btn_5.grid(row=5, column=0, padx=20, pady=10)
        
        self.nav_btn_6 = ctk.CTkButton(
            self.navigation_frame, text="Settings",
            command=self.nav_to_settings
        )
        self.nav_btn_6.grid(row=6, column=0, padx=20, pady=10)
        
        # Appearance mode toggle
        self.appearance_mode_label = ctk.CTkLabel(self.navigation_frame, text="Appearance Mode:")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.navigation_frame, values=["System", "Light", "Dark"],
            command=self.change_appearance_mode
        )
        self.appearance_mode_menu.grid(row=9, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_menu.set("System")
        
        # Create frames for each section with scrollable content
        self.generate_excuse_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.proof_generator_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.emergency_system_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.apology_generator_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.history_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.settings_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        # Configure all main frames to expand properly
        for frame in [self.generate_excuse_frame, self.proof_generator_frame, self.emergency_system_frame, 
                      self.apology_generator_frame, self.history_frame, self.settings_frame]:
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
        
        # Initialize all frames
        self.init_generate_excuse_frame()
        self.init_proof_generator_frame()
        self.init_emergency_system_frame()
        self.init_apology_generator_frame()
        self.init_history_frame()
        self.init_settings_frame()
        
        # Default to generate excuse frame
        self.select_frame_by_name("generate_excuse")
    
    def select_frame_by_name(self, name):
        # Hide all frames
        self.generate_excuse_frame.grid_forget()
        self.proof_generator_frame.grid_forget()
        self.emergency_system_frame.grid_forget()
        self.apology_generator_frame.grid_forget()
        self.history_frame.grid_forget()
        self.settings_frame.grid_forget()
        
        # Show selected frame
        if name == "generate_excuse":
            self.generate_excuse_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "proof_generator":
            self.proof_generator_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "emergency_system":
            self.emergency_system_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "apology_generator":
            self.apology_generator_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "history":
            self.history_frame.grid(row=0, column=1, sticky="nsew")
            self.refresh_history()
        elif name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
    
    def nav_to_generate_excuse(self):
        self.select_frame_by_name("generate_excuse")
    
    def nav_to_proof_generator(self):
        self.select_frame_by_name("proof_generator")
    
    def nav_to_emergency_system(self):
        self.select_frame_by_name("emergency_system")
    
    def nav_to_apology_generator(self):
        self.select_frame_by_name("apology_generator")
    
    def nav_to_history(self):
        self.select_frame_by_name("history")
    
    def nav_to_settings(self):
        self.select_frame_by_name("settings")
    
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
    
    def init_generate_excuse_frame(self):
        # Create scrollable container for content
        self.generate_excuse_scrollable = ctk.CTkScrollableFrame(self.generate_excuse_frame)
        self.generate_excuse_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.generate_excuse_scrollable.grid_columnconfigure(0, weight=1)
        
        # Title with improved styling
        self.generate_excuse_title = ctk.CTkLabel(
            self.generate_excuse_scrollable, text="Generate Excuse",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.generate_excuse_title.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Context frame with improved styling
        self.context_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.context_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.context_frame.grid_columnconfigure(0, weight=1)
        
        # Context label
        self.context_label = ctk.CTkLabel(self.context_frame, text="Context:")
        self.context_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Context options
        self.context_var = ctk.StringVar(value="Work")
        self.context_options = ctk.CTkSegmentedButton(
            self.context_frame,
            values=["Work", "School", "Social", "Family", "Other"],
            variable=self.context_var
        )
        self.context_options.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Context details
        self.context_details_label = ctk.CTkLabel(self.context_frame, text="Details:")
        self.context_details_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.context_details = ctk.CTkTextbox(self.context_frame, height=100)
        self.context_details.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Audience frame with improved styling
        self.audience_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.audience_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.audience_frame.grid_columnconfigure(0, weight=1)
        
        # Audience label
        self.audience_label = ctk.CTkLabel(self.audience_frame, text="Audience:")
        self.audience_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Audience options
        self.audience_var = ctk.StringVar(value="Boss")
        self.audience_options = ctk.CTkSegmentedButton(
            self.audience_frame,
            values=["Boss", "Teacher", "Friend", "Family", "Other"],
            variable=self.audience_var
        )
        self.audience_options.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Formality and urgency frame with improved styling
        self.formality_urgency_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.formality_urgency_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.formality_urgency_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Formality
        self.formality_label = ctk.CTkLabel(self.formality_urgency_frame, text="Formality:")
        self.formality_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.formality_var = ctk.StringVar(value="Formal")
        self.formality_options = ctk.CTkSegmentedButton(
            self.formality_urgency_frame,
            values=["Formal", "Casual", "Professional"],
            variable=self.formality_var
        )
        self.formality_options.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Urgency
        self.urgency_label = ctk.CTkLabel(self.formality_urgency_frame, text="Urgency:")
        self.urgency_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.urgency_var = ctk.StringVar(value="Normal")
        self.urgency_options = ctk.CTkSegmentedButton(
            self.formality_urgency_frame,
            values=["Low", "Normal", "High", "Emergency"],
            variable=self.urgency_var
        )
        self.urgency_options.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Language frame with improved styling
        self.language_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.language_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.language_frame.grid_columnconfigure(1, weight=1)
        
        # Language label
        self.language_label = ctk.CTkLabel(self.language_frame, text="Language:")
        self.language_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Language dropdown with all supported languages
        self.language_var = ctk.StringVar(value="English")
        
        # Get all language names from the language_codes dictionary
        language_options = list(self.excuse_generator.language_codes.keys())
        language_options.sort()  # Sort alphabetically for easier searching
        
        # Create a combobox instead of option menu to allow searching
        self.language_dropdown = ctk.CTkComboBox(
            self.language_frame,
            values=language_options,
            variable=self.language_var,
            width=200
        )
        self.language_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Voice input button
        self.voice_input_button = ctk.CTkButton(
            self.language_frame, text="Voice Input",
            command=self.voice_input
        )
        self.voice_input_button.grid(row=0, column=2, padx=10, pady=5)
        
        # Generate button with improved styling
        self.generate_button = ctk.CTkButton(
            self.generate_excuse_scrollable, text="Generate Excuse",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=40,
            corner_radius=8,
            command=self.generate_excuse_thread
        )
        self.generate_button.grid(row=5, column=0, padx=20, pady=20)
        
        # Result frame with improved styling
        self.result_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.result_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        
        # Result label
        self.result_label = ctk.CTkLabel(
            self.result_frame, text="Generated Excuse (Original):",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.result_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Result text
        self.result_text = ctk.CTkTextbox(self.result_frame, height=150)
        self.result_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Translation result frame
        self.translation_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.translation_frame.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        self.translation_frame.grid_columnconfigure(0, weight=1)
        
        # Translation label
        self.translation_label = ctk.CTkLabel(
            self.translation_frame, text="Translated Excuse:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.translation_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Translation text
        self.translation_text = ctk.CTkTextbox(self.translation_frame, height=150)
        self.translation_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Action buttons frame - moved outside of result frame to be below both text areas
        self.action_frame = ctk.CTkFrame(self.generate_excuse_scrollable, corner_radius=10, border_width=1)
        self.action_frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # Original text actions
        self.original_label = ctk.CTkLabel(self.action_frame, text="Original:")
        self.original_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Copy original button
        self.copy_original_button = ctk.CTkButton(
            self.action_frame, text="Copy Original",
            command=lambda: self.copy_to_clipboard(self.result_text)
        )
        self.copy_original_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Speak original button
        self.speak_original_button = ctk.CTkButton(
            self.action_frame, text="Speak Original",
            command=lambda: self.speak_excuse(self.result_text)
        )
        self.speak_original_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Translation text actions
        self.translation_action_label = ctk.CTkLabel(self.action_frame, text="Translation:")
        self.translation_action_label.grid(row=1, column=0, padx=5, pady=5)
        
        # Copy translation button
        self.copy_translation_button = ctk.CTkButton(
            self.action_frame, text="Copy Translation",
            command=lambda: self.copy_to_clipboard(self.translation_text)
        )
        self.copy_translation_button.grid(row=1, column=1, padx=5, pady=5)
        
        # Speak translation button
        self.speak_translation_button = ctk.CTkButton(
            self.action_frame, text="Speak Translation",
            command=lambda: self.speak_excuse(self.translation_text)
        )
        self.speak_translation_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Save to favorites button
        self.save_button = ctk.CTkButton(
            self.action_frame, text="Save to Favorites",
            command=self.save_to_favorites
        )
        self.save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # Rate effectiveness frame
        self.rate_frame = ctk.CTkFrame(self.action_frame)
        self.rate_frame.grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        
        # Rate label
        self.rate_label = ctk.CTkLabel(self.rate_frame, text="Rate:")
        self.rate_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Rate stars
        self.rate_var = ctk.IntVar(value=0)
        self.rate_stars = ctk.CTkSegmentedButton(
            self.rate_frame,
            values=["1", "2", "3", "4", "5"],
            variable=self.rate_var,
            command=self.rate_excuse
        )
        self.rate_stars.grid(row=0, column=1, padx=5, pady=5)
    
    def init_proof_generator_frame(self):
        # Create scrollable container for content
        self.proof_generator_scrollable = ctk.CTkScrollableFrame(self.proof_generator_frame)
        self.proof_generator_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.proof_generator_scrollable.grid_columnconfigure(0, weight=1)
        
        # Title with improved styling
        self.proof_generator_title = ctk.CTkLabel(
            self.proof_generator_scrollable, text="Proof Generator",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.proof_generator_title.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Proof type frame with improved styling
        self.proof_type_frame = ctk.CTkFrame(self.proof_generator_scrollable, corner_radius=10, border_width=1)
        self.proof_type_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.proof_type_frame.grid_columnconfigure(0, weight=1)
        
        # Proof type label
        self.proof_type_label = ctk.CTkLabel(self.proof_type_frame, text="Proof Type:")
        self.proof_type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Proof type options
        self.proof_type_var = ctk.StringVar(value="Doctor's Note")
        self.proof_type_options = ctk.CTkSegmentedButton(
            self.proof_type_frame,
            values=["Doctor's Note", "Email Screenshot", "Receipt", "Ticket", "Other"],
            variable=self.proof_type_var
        )
        self.proof_type_options.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Proof details
        self.proof_details_label = ctk.CTkLabel(self.proof_type_frame, text="Details:")
        self.proof_details_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.proof_details = ctk.CTkTextbox(self.proof_type_frame, height=100)
        self.proof_details.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Generate button with improved styling
        self.generate_proof_button = ctk.CTkButton(
            self.proof_generator_scrollable, text="Generate Proof",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=40,
            corner_radius=8,
            command=self.generate_proof_thread
        )
        self.generate_proof_button.grid(row=2, column=0, padx=20, pady=20)
        
        # Result frame with improved styling
        self.proof_result_frame = ctk.CTkFrame(self.proof_generator_scrollable, corner_radius=10, border_width=1)
        self.proof_result_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.proof_result_frame.grid_columnconfigure(0, weight=1)
        
        # Result label
        self.proof_result_label = ctk.CTkLabel(
            self.proof_result_frame, text="Generated Proof:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.proof_result_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Result text
        self.proof_result_text = ctk.CTkTextbox(self.proof_result_frame, height=200)
        self.proof_result_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Copy button with improved styling
        self.copy_proof_button = ctk.CTkButton(
            self.proof_result_frame, text="Copy to Clipboard",
            corner_radius=8,
            command=lambda: self.copy_to_clipboard(self.proof_result_text)
        )
        self.copy_proof_button.grid(row=2, column=0, padx=10, pady=10)
    
    def init_emergency_system_frame(self):
        # Create scrollable container for content
        self.emergency_system_scrollable = ctk.CTkScrollableFrame(self.emergency_system_frame)
        self.emergency_system_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.emergency_system_scrollable.grid_columnconfigure(0, weight=1)
        
        # Title with improved styling
        self.emergency_system_title = ctk.CTkLabel(
            self.emergency_system_scrollable, text="Emergency System",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.emergency_system_title.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Emergency type frame with improved styling
        self.emergency_type_frame = ctk.CTkFrame(self.emergency_system_scrollable, corner_radius=10, border_width=1)
        self.emergency_type_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.emergency_type_frame.grid_columnconfigure(0, weight=1)
        
        # Emergency type label
        self.emergency_type_label = ctk.CTkLabel(self.emergency_type_frame, text="Emergency Type:")
        self.emergency_type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Emergency type options
        self.emergency_type_var = ctk.StringVar(value="Family Emergency")
        self.emergency_type_options = ctk.CTkSegmentedButton(
            self.emergency_type_frame,
            values=["Family Emergency", "Medical Issue", "Car Trouble", "Power Outage", "Other"],
            variable=self.emergency_type_var
        )
        self.emergency_type_options.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Recipient frame with improved styling
        self.recipient_frame = ctk.CTkFrame(self.emergency_system_scrollable, corner_radius=10, border_width=1)
        self.recipient_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.recipient_frame.grid_columnconfigure(1, weight=1)
        
        # Recipient label
        self.recipient_label = ctk.CTkLabel(self.recipient_frame, text="Recipient:")
        self.recipient_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Recipient entry
        self.recipient_entry = ctk.CTkEntry(self.recipient_frame, placeholder_text="Enter recipient name")
        self.recipient_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Generate button with improved styling
        self.generate_emergency_button = ctk.CTkButton(
            self.emergency_system_scrollable, text="Generate Emergency Message",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=40,
            corner_radius=8,
            command=self.generate_emergency_thread
        )
        self.generate_emergency_button.grid(row=3, column=0, padx=20, pady=20)
        
        # Result frame with improved styling
        self.emergency_result_frame = ctk.CTkFrame(self.emergency_system_scrollable, corner_radius=10, border_width=1)
        self.emergency_result_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.emergency_result_frame.grid_columnconfigure(0, weight=1)
        
        # Result label
        self.emergency_result_label = ctk.CTkLabel(
            self.emergency_result_frame, text="Emergency Message:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.emergency_result_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Result text
        self.emergency_result_text = ctk.CTkTextbox(self.emergency_result_frame, height=200)
        self.emergency_result_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Action buttons frame
        self.emergency_action_frame = ctk.CTkFrame(self.emergency_result_frame)
        self.emergency_action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.emergency_action_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Copy button
        self.copy_emergency_button = ctk.CTkButton(
            self.emergency_action_frame, text="Copy to Clipboard",
            command=lambda: self.copy_to_clipboard(self.emergency_result_text)
        )
        self.copy_emergency_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Send button (simulated)
        self.send_emergency_button = ctk.CTkButton(
            self.emergency_action_frame, text="Simulate Send",
            command=self.simulate_send
        )
        self.send_emergency_button.grid(row=0, column=1, padx=5, pady=5)
    
    def init_apology_generator_frame(self):
        # Create scrollable container for content
        self.apology_generator_scrollable = ctk.CTkScrollableFrame(self.apology_generator_frame)
        self.apology_generator_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.apology_generator_scrollable.grid_columnconfigure(0, weight=1)
        
        # Title with improved styling
        self.apology_generator_title = ctk.CTkLabel(
            self.apology_generator_scrollable, text="Apology Generator",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.apology_generator_title.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Situation frame with improved styling
        self.situation_frame = ctk.CTkFrame(self.apology_generator_scrollable, corner_radius=10, border_width=1)
        self.situation_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.situation_frame.grid_columnconfigure(0, weight=1)
        
        # Situation label
        self.situation_label = ctk.CTkLabel(self.situation_frame, text="Situation:")
        self.situation_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Situation textbox
        self.situation_text = ctk.CTkTextbox(self.situation_frame, height=100)
        self.situation_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Formality frame with improved styling
        self.apology_formality_frame = ctk.CTkFrame(self.apology_generator_scrollable, corner_radius=10, border_width=1)
        self.apology_formality_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.apology_formality_frame.grid_columnconfigure(0, weight=1)
        
        # Formality label
        self.apology_formality_label = ctk.CTkLabel(self.apology_formality_frame, text="Formality:")
        self.apology_formality_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Formality options
        self.apology_formality_var = ctk.StringVar(value="Professional")
        self.apology_formality_options = ctk.CTkSegmentedButton(
            self.apology_formality_frame,
            values=["Professional", "Formal", "Casual", "Emotional"],
            variable=self.apology_formality_var
        )
        self.apology_formality_options.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Generate button with improved styling
        self.generate_apology_button = ctk.CTkButton(
            self.apology_generator_scrollable, text="Generate Apology",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=40,
            corner_radius=8,
            command=self.generate_apology_thread
        )
        self.generate_apology_button.grid(row=3, column=0, padx=20, pady=20)
        
        # Result frame with improved styling
        self.apology_result_frame = ctk.CTkFrame(self.apology_generator_scrollable, corner_radius=10, border_width=1)
        self.apology_result_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.apology_result_frame.grid_columnconfigure(0, weight=1)
        
        # Result label
        self.apology_result_label = ctk.CTkLabel(
            self.apology_result_frame, text="Generated Apology:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.apology_result_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Result text
        self.apology_result_text = ctk.CTkTextbox(self.apology_result_frame, height=200)
        self.apology_result_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Copy button with improved styling
        self.copy_apology_button = ctk.CTkButton(
            self.apology_result_frame, text="Copy to Clipboard",
            corner_radius=8,
            command=lambda: self.copy_to_clipboard(self.apology_result_text)
        )
        self.copy_apology_button.grid(row=2, column=0, padx=10, pady=10)
    
    def init_history_frame(self):
        # Create scrollable container for content
        self.history_scrollable = ctk.CTkScrollableFrame(self.history_frame)
        self.history_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.history_scrollable.grid_columnconfigure(0, weight=1)
        
        # Title with improved styling
        self.history_title = ctk.CTkLabel(
            self.history_scrollable, text="History & Favorites",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.history_title.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Tab view with improved styling
        self.history_tabview = ctk.CTkTabview(self.history_scrollable, corner_radius=10)
        self.history_tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.history_tabview.add("History")
        self.history_tabview.add("Favorites")
        
        # History tab
        self.history_tab = self.history_tabview.tab("History")
        self.history_tab.grid_columnconfigure(0, weight=1)
        
        # History list frame
        self.history_list_frame = ctk.CTkScrollableFrame(self.history_tab)
        self.history_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.history_list_frame.grid_columnconfigure(0, weight=1)
        
        # Favorites tab
        self.favorites_tab = self.history_tabview.tab("Favorites")
        self.favorites_tab.grid_columnconfigure(0, weight=1)
        
        # Favorites list frame
        self.favorites_list_frame = ctk.CTkScrollableFrame(self.favorites_tab)
        self.favorites_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.favorites_list_frame.grid_columnconfigure(0, weight=1)
    
    def init_settings_frame(self):
        # Create scrollable container for content
        self.settings_scrollable = ctk.CTkScrollableFrame(self.settings_frame)
        self.settings_scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.settings_scrollable.grid_columnconfigure(0, weight=1)
        
        # Title with improved styling
        self.settings_title = ctk.CTkLabel(
            self.settings_scrollable, text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.settings_title.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Auto-scheduling frame with improved styling
        self.auto_scheduling_frame = ctk.CTkFrame(self.settings_scrollable, corner_radius=10, border_width=1)
        self.auto_scheduling_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.auto_scheduling_frame.grid_columnconfigure(0, weight=1)
        
        # Auto-scheduling title
        self.auto_scheduling_title = ctk.CTkLabel(
            self.auto_scheduling_frame, text="Auto-Scheduling",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.auto_scheduling_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Auto-scheduling description
        self.auto_scheduling_desc = ctk.CTkLabel(
            self.auto_scheduling_frame, 
            text="Predict when you might need excuses based on your usage patterns.",
            wraplength=500
        )
        self.auto_scheduling_desc.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Prediction button
        self.predict_button = ctk.CTkButton(
            self.auto_scheduling_frame, text="Predict Next Excuse Need",
            command=self.show_excuse_prediction
        )
        self.predict_button.grid(row=2, column=0, padx=10, pady=10)
        
        # Prediction result
        self.prediction_result = ctk.CTkLabel(
            self.auto_scheduling_frame, text="No prediction available yet.",
            wraplength=500
        )
        self.prediction_result.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        # API settings frame with improved styling
        self.api_settings_frame = ctk.CTkFrame(self.settings_scrollable, corner_radius=10, border_width=1)
        self.api_settings_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.api_settings_frame.grid_columnconfigure(1, weight=1)
        
        # API key label
        self.api_key_label = ctk.CTkLabel(self.api_settings_frame, text="Gemini API Key:")
        self.api_key_label.grid(row=0, column=0, padx=10, pady=10)
        
        # API key entry
        self.api_key_entry = ctk.CTkEntry(self.api_settings_frame, width=400)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.api_key_entry.insert(0, API_KEY)
        
        # Model name label
        self.model_name_label = ctk.CTkLabel(self.api_settings_frame, text="Model Name:")
        self.model_name_label.grid(row=1, column=0, padx=10, pady=10)
        
        # Model name entry
        self.model_name_entry = ctk.CTkEntry(self.api_settings_frame, width=400)
        self.model_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.model_name_entry.insert(0, MODEL_NAME)
        
        # Save settings button with improved styling
        self.save_settings_button = ctk.CTkButton(
            self.api_settings_frame, text="Save Settings",
            font=ctk.CTkFont(weight="bold"),
            height=36,
            corner_radius=8,
            command=self.save_settings
        )
        self.save_settings_button.grid(row=2, column=1, padx=15, pady=15, sticky="e")
        
        # UI settings frame with improved styling
        self.ui_settings_frame = ctk.CTkFrame(self.settings_scrollable, corner_radius=10, border_width=1)
        self.ui_settings_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.ui_settings_frame.grid_columnconfigure(1, weight=1)
        
        # UI scaling label
        self.ui_scaling_label = ctk.CTkLabel(self.ui_settings_frame, text="UI Scaling:")
        self.ui_scaling_label.grid(row=0, column=0, padx=10, pady=10)
        
        # UI scaling option menu with improved styling
        self.ui_scaling_optionemenu = ctk.CTkOptionMenu(
            self.ui_settings_frame, values=["80%", "90%", "100%", "110%", "120%"],
            corner_radius=8,
            command=self.change_scaling_event
        )
        self.ui_scaling_optionemenu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.ui_scaling_optionemenu.set("100%")
        
        # About frame with improved styling
        self.about_frame = ctk.CTkFrame(self.settings_scrollable, corner_radius=10, border_width=1)
        self.about_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.about_frame.grid_columnconfigure(0, weight=1)
        
        # About label with improved styling
        self.about_label = ctk.CTkLabel(
            self.about_frame, text="Intelligent Excuse Generator v1.0",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.about_label.grid(row=0, column=0, padx=15, pady=10)
        
        # Description label with improved styling
        self.description_label = ctk.CTkLabel(
            self.about_frame,
            text="An AI-powered application for generating context-aware, customizable excuses.",
            font=ctk.CTkFont(size=14),
            wraplength=500
        )
        self.description_label.grid(row=1, column=0, padx=15, pady=10)
        
        # Credits label
        self.credits_label = ctk.CTkLabel(
            self.about_frame,
            text="Powered by Google Gemini API\n© 2023 All Rights Reserved",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.credits_label.grid(row=2, column=0, padx=15, pady=10)
    
    # Functionality methods
    def generate_excuse_thread(self):
        # Disable generate button
        self.generate_button.configure(state="disabled")
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", "Generating excuse...")
        
        # Get input values
        context = self.context_var.get()
        context_details = self.context_details.get("0.0", "end-1c")
        audience = self.audience_var.get()
        formality = self.formality_var.get()
        urgency = self.urgency_var.get()
        language = self.language_var.get()
        
        # Start thread
        thread = threading.Thread(
            target=self.generate_excuse_task,
            args=(context, context_details, audience, formality, urgency, language)
        )
        thread.daemon = True
        thread.start()
    
    def generate_excuse_task(self, context, context_details, audience, formality, urgency, language):
        try:
            # Generate excuse in English
            original_excuse = self.excuse_generator.generate_excuse(f"{context}: {context_details}", audience, formality, urgency)
            
            # Store the original excuse
            translated_excuse = ""
            
            # Translate if needed
            if language != "English":
                translated_excuse = self.excuse_generator.translate_excuse(original_excuse, language)
            else:
                translated_excuse = "No translation needed for English"
            
            # Update UI in main thread
            self.after(0, lambda: self.update_excuse_result(original_excuse, translated_excuse, language))
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.after(0, lambda: self.update_excuse_result(error_message, error_message, language))
    
    def update_excuse_result(self, original_excuse, translated_excuse, language):
        # Update original excuse text
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", original_excuse)
        
        # Update translation text
        self.translation_text.delete("0.0", "end")
        if language != "English":
            self.translation_text.insert("0.0", translated_excuse)
            self.translation_label.configure(text=f"Translated Excuse ({language}):")
        else:
            self.translation_text.insert("0.0", translated_excuse)
            self.translation_label.configure(text="Translated Excuse:")
        
        # Re-enable generate button
        self.generate_button.configure(state="normal")
    
    def generate_proof_thread(self):
        # Disable generate button
        self.generate_proof_button.configure(state="disabled")
        self.proof_result_text.delete("0.0", "end")
        self.proof_result_text.insert("0.0", "Generating proof...")
        
        # Get input values
        proof_type = self.proof_type_var.get()
        proof_details = self.proof_details.get("0.0", "end-1c")
        
        # Start thread
        thread = threading.Thread(
            target=self.generate_proof_task,
            args=(proof_type, proof_details)
        )
        thread.daemon = True
        thread.start()
    
    def generate_proof_task(self, proof_type, proof_details):
        try:
            # Generate proof
            proof = self.excuse_generator.generate_proof(proof_type, proof_details)
            
            # Update UI in main thread
            self.after(0, lambda: self.update_proof_result(proof))
        except Exception as e:
            self.after(0, lambda: self.update_proof_result(f"Error: {str(e)}"))
    
    def update_proof_result(self, proof):
        self.proof_result_text.delete("0.0", "end")
        self.proof_result_text.insert("0.0", proof)
        self.generate_proof_button.configure(state="normal")
    
    def generate_emergency_thread(self):
        # Disable generate button
        self.generate_emergency_button.configure(state="disabled")
        self.emergency_result_text.delete("0.0", "end")
        self.emergency_result_text.insert("0.0", "Generating emergency message...")
        
        # Get input values
        emergency_type = self.emergency_type_var.get()
        recipient = self.recipient_entry.get()
        
        # Start thread
        thread = threading.Thread(
            target=self.generate_emergency_task,
            args=(emergency_type, recipient)
        )
        thread.daemon = True
        thread.start()
    
    def generate_emergency_task(self, emergency_type, recipient):
        try:
            # Generate emergency message
            message = self.excuse_generator.generate_emergency_message(emergency_type, recipient)
            
            # Update UI in main thread
            self.after(0, lambda: self.update_emergency_result(message))
        except Exception as e:
            self.after(0, lambda: self.update_emergency_result(f"Error: {str(e)}"))
    
    def update_emergency_result(self, message):
        self.emergency_result_text.delete("0.0", "end")
        self.emergency_result_text.insert("0.0", message)
        self.generate_emergency_button.configure(state="normal")
    
    def generate_apology_thread(self):
        # Disable generate button
        self.generate_apology_button.configure(state="disabled")
        self.apology_result_text.delete("0.0", "end")
        self.apology_result_text.insert("0.0", "Generating apology...")
        
        # Get input values
        situation = self.situation_text.get("0.0", "end-1c")
        formality = self.apology_formality_var.get()
        
        # Start thread
        thread = threading.Thread(
            target=self.generate_apology_task,
            args=(situation, formality)
        )
        thread.daemon = True
        thread.start()
    
    def generate_apology_task(self, situation, formality):
        try:
            # Generate apology
            apology = self.excuse_generator.generate_apology(situation, formality)
            
            # Update UI in main thread
            self.after(0, lambda: self.update_apology_result(apology))
        except Exception as e:
            self.after(0, lambda: self.update_apology_result(f"Error: {str(e)}"))
    
    def update_apology_result(self, apology):
        self.apology_result_text.delete("0.0", "end")
        self.apology_result_text.insert("0.0", apology)
        self.generate_apology_button.configure(state="normal")
    
    def voice_input(self):
        # Start thread for voice input
        thread = threading.Thread(target=self.voice_input_task)
        thread.daemon = True
        thread.start()
    
    def voice_input_task(self):
        try:
            # Get voice input
            text = self.excuse_generator.voice_to_text()
            
            # Update UI in main thread
            self.after(0, lambda: self.context_details.insert("end", text))
        except Exception as e:
            print(f"Error in voice input: {e}")
    
    def copy_to_clipboard(self, textbox=None):
        if textbox is None:
            textbox = self.result_text
        
        text = textbox.get("0.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        
    def speak_excuse(self, textbox=None):
        # Get the excuse text from the specified textbox or default to result_text
        if textbox is None:
            textbox = self.result_text
            
        text = textbox.get("0.0", "end-1c")
        if text and text != "Generating excuse..." and text != "No translation needed for English":
            # Start thread for speech synthesis
            thread = threading.Thread(target=self.speak_excuse_task, args=(text,))
            thread.daemon = True
            thread.start()
            
    def speak_excuse_task(self, text):
        try:
            # Use text-to-speech to speak the excuse
            self.excuse_generator.text_to_speech(text)
        except Exception as e:
            print(f"Error in speak excuse: {e}")
    
    def save_to_favorites(self):
        original_excuse = self.result_text.get("0.0", "end-1c")
        translated_excuse = self.translation_text.get("0.0", "end-1c")
        language = self.language_var.get()
        context = self.context_var.get()
        audience = self.audience_var.get()
        
        if original_excuse and original_excuse != "Generating excuse...":
            # Add to favorites
            self.excuse_generator.add_to_favorites({
                "excuse": original_excuse,
                "translation": translated_excuse if translated_excuse != "No translation needed for English" else "",
                "language": language,
                "context": context,
                "audience": audience,
                "timestamp": datetime.datetime.now().isoformat()
            })
    
    def rate_excuse(self, value):
        # Get the current excuse from history (most recent)
        if self.excuse_generator.history:
            latest_excuse = self.excuse_generator.history[-1]
            latest_excuse["effectiveness"] = int(value)
            self.excuse_generator.save_history()
    
    def refresh_history(self):
        # Clear existing items
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
        
        for widget in self.favorites_list_frame.winfo_children():
            widget.destroy()
        
        # Reload data
        self.excuse_generator.history = self.excuse_generator.load_history()
        self.excuse_generator.favorites = self.excuse_generator.load_favorites()
        
        # Populate history
        for i, item in enumerate(reversed(self.excuse_generator.history)):
            self.add_history_item(i, item)
        
        # Populate favorites
        for i, item in enumerate(reversed(self.excuse_generator.favorites)):
            self.add_favorite_item(i, item)
    
    def add_history_item(self, index, item):
        frame = ctk.CTkFrame(self.history_list_frame)
        frame.grid(row=index, column=0, padx=5, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        # Context and audience
        header = f"{item.get('context', 'Unknown')} - {item.get('audience', 'Unknown')}"
        header_label = ctk.CTkLabel(frame, text=header, font=ctk.CTkFont(weight="bold"))
        header_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Timestamp
        timestamp = item.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        time_label = ctk.CTkLabel(frame, text=timestamp)
        time_label.grid(row=0, column=1, padx=5, pady=2, sticky="e")
        
        # Excuse text
        excuse_text = ctk.CTkTextbox(frame, height=60, wrap="word")
        excuse_text.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        excuse_text.insert("0.0", item.get('excuse', ''))
        excuse_text.configure(state="disabled")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Copy button
        copy_btn = ctk.CTkButton(
            buttons_frame, text="Copy",
            command=lambda t=excuse_text: self.copy_to_clipboard(t)
        )
        copy_btn.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Add to favorites button
        fav_btn = ctk.CTkButton(
            buttons_frame, text="Add to Favorites",
            command=lambda i=item: self.excuse_generator.add_to_favorites(i)
        )
        fav_btn.grid(row=0, column=1, padx=5, pady=2, sticky="e")
    
    def add_favorite_item(self, index, item):
        frame = ctk.CTkFrame(self.favorites_list_frame)
        frame.grid(row=index, column=0, padx=5, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        # Context and audience
        header = f"{item.get('context', 'Unknown')} - {item.get('audience', 'Unknown')}"
        header_label = ctk.CTkLabel(frame, text=header, font=ctk.CTkFont(weight="bold"))
        header_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Excuse text
        excuse_text = ctk.CTkTextbox(frame, height=60, wrap="word")
        excuse_text.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        excuse_text.insert("0.0", item.get('excuse', ''))
        excuse_text.configure(state="disabled")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Copy button
        copy_btn = ctk.CTkButton(
            buttons_frame, text="Copy",
            command=lambda t=excuse_text: self.copy_to_clipboard(t)
        )
        copy_btn.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        # Remove from favorites button
        remove_btn = ctk.CTkButton(
            buttons_frame, text="Remove",
            command=lambda i=index: self.remove_favorite(i)
        )
        remove_btn.grid(row=0, column=1, padx=5, pady=2, sticky="e")
    
    def remove_favorite(self, index):
        self.excuse_generator.remove_from_favorites(index)
        self.refresh_history()
    
    def save_settings(self):
        global API_KEY, MODEL_NAME
        
        # Update API key and model name
        API_KEY = self.api_key_entry.get()
        MODEL_NAME = self.model_name_entry.get()
        
        # Reconfigure Gemini API
        genai.configure(api_key=API_KEY)
        
        # Reinitialize the excuse generator
        self.excuse_generator = ExcuseGenerator()
    
    def change_scaling_event(self, new_scaling):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def simulate_send(self):
        # Simulate sending the emergency message
        message = self.emergency_result_text.get("0.0", "end-1c")
        if message and message != "Generating emergency message...":
            # Show a success message
            self.emergency_result_text.delete("0.0", "end")
            self.emergency_result_text.insert("0.0", message + "\n\n[Message sent successfully - Simulation]")
            
    def show_excuse_prediction(self):
        # Get prediction
        prediction = self.excuse_generator.predict_excuse_needs()
        
        if prediction:
            # Format the prediction date
            next_date = datetime.datetime.fromisoformat(prediction["next_predicted_date"])
            formatted_date = next_date.strftime("%A, %B %d at %I:%M %p")
            
            # Update the prediction result label
            prediction_text = f"Next predicted excuse need:\n{formatted_date}\n\n"
            prediction_text += f"Based on your history, you typically need excuses on {prediction['common_day']}s "
            prediction_text += f"around {next_date.strftime('%I:%M %p')} for {prediction['common_context']} situations."
            
            self.prediction_result.configure(text=prediction_text)
        else:
            self.prediction_result.configure(text="Not enough history data to make a prediction.\nTry generating more excuses first.")


if __name__ == "__main__":
    app = App()
    app.mainloop()