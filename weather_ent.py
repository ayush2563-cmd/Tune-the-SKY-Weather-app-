import customtkinter as ctk
from tkinter import messagebox, Canvas
import requests
from PIL import Image, ImageTk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
import random
from datetime import datetime
import pytz

# Spotify API setup
SPOTIFY_CLIENT_ID = "13d79674e85c47bf9a4f313985b18225"
SPOTIFY_CLIENT_SECRET = "617f1bb273a243cfbf76e1ad68c94be5"

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
))

# TMDb API setup
TMDB_API_KEY = "752adf2558133218c7b61da08f95b4ce"

# API Ninjas Quotes API setup
API_NINJAS_KEY = "hi0bUbnHPSpJ3LohClYGEQ==vizndbvaH59Ptjpj"
API_NINJAS_URL = "https://api.api-ninjas.com/v1/quotes"

# Global variables
current_song_url = None
current_movies = []

# Function to toggle dark/light mode
def toggle_mode():
    current_mode = ctk.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    ctk.set_appearance_mode(new_mode)

# Function to open the song in a web browser
def play_song():
    if current_song_url:
        webbrowser.open(current_song_url)
    else:
        messagebox.showinfo("Info", "No song available to play.")

# Function to get current location
def get_location():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        city = data.get("city")
        country = data.get("country")
        if not city or not country:
            raise ValueError("City or country not found in location data.")
        return city, country
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch location: {e}")
        return None, None

# Function to fetch a weather-based quote
def get_quote(weather):
    weather_keywords = {
        "clear": "happiness",
        "cloud": "thoughtful",
        "rain": "love",
        "drizzle": "hope",
        "snow": "peace",
        "storm": "courage",
        "thunder": "strength",
        "mist": "mystery",
        "fog": "dream",
    }
    keyword = weather_keywords.get(weather.split()[0].lower(), "inspiration")

    try:
        headers = {"X-Api-Key": API_NINJAS_KEY}
        params = {"category": keyword}
        response = requests.get(API_NINJAS_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data:
            quote = random.choice(data)
            return f"\"{quote['quote']}\"\n- {quote['author']}"
        else:
            return f"No quotes found for '{keyword}'. Here's an inspirational fallback:\n\n\"The best way to predict the future is to create it.\" - Peter Drucker"
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch quote: {e}"

# Function to recommend Bollywood movies
def recommend_movies(weather):
    global current_movies
    weather = weather.lower()
    genre_mapping = {
        "clear": "35",  # Comedy
        "cloud": "18",  # Drama
        "rain": "10749",  # Romance
        "drizzle": "10749", # Romance
        "snow": "16",  # Animation
        "storm": "28",  # Action
        "thunder": "53",  # Thriller
        "mist": "14",  # Fantasy
        "fog": "878",  # Sci-Fi
    }

    genre = genre_mapping.get(weather.split()[0], "18")  # Default to Drama

    try:
        url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": genre,
            "language": "en",
            "region": "IN",
            "sort_by": "popularity.desc",
            "with_original_language": "hi",  # Ensure the movies are originally in Hindi
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("results"):
            movies = data["results"]
            random.shuffle(movies)
            current_movies = movies[:5]
            movie_recommendations = "Movies to watch:\n" + "\n".join(
                f"{movie['title']} ({movie['release_date'][:4]})" for movie in current_movies
            )
            movie_label.configure(text=movie_recommendations)
        else:
            movie_label.configure(text="No Bollywood movie recommendations found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch movie recommendations: {e}")
        movie_label.configure(text="No Bollywood movie recommendations found.")

# Function to recommend songs
def recommend_song(weather):
    global current_song_url
    weather = weather.lower()
    mood = ""

    if "clear" in weather:
        mood = "happy"
    elif "cloud" in weather:
        mood = "calm"
    elif "rain" in weather or "drizzle" in weather:
        mood = "romantic"
    elif "snow" in weather:
        mood = "cozy"
    elif "storm" in weather or "thunder" in weather:
        mood = "intense"
    elif "mist" in weather or "fog" in weather:
        mood = "ambient"
    else:
        mood = "chill"

    query = f"{mood} Bollywood"

    try:
        results = spotify.search(q=query, type="track", limit=10)
        if results["tracks"]["items"]:
            track = random.choice(results["tracks"]["items"])
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            current_song_url = track["external_urls"]["spotify"]
            song_label.configure(
                text=f"Recommended Song: {track_name}\nArtist: {artist_name}"
            )
            play_button.place(relx=0.65, rely=0.31, anchor="center")
        else:
            song_label.configure(text="No Bollywood song recommendations found.")
            play_button.place_forget()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch Bollywood song recommendation: {e}")
        play_button.place_forget()

# Function to load weather icons
def load_weather_icon(weather):
    weather_icons = {
        "clear": "icons/sunny.png",
        "cloud": "icons/cloudy.png",
        "rain": "icons/rainy.png",
        "drizzle": "icons/drizzle.png",
        "snow": "icons/snowy.png",
        "storm": "icons/storm.png",
        "thunder": "icons/thunder.png",
        "mist": "icons/mist.png",
        "fog": "icons/foggy.png",
        "haze": "icons/haze.png",
    }
    for key in weather_icons:
        if key in weather.lower():
            return weather_icons[key]
    return "icons/default.png"  # Default icon for unrecognized weather

# Function to update the background gradient based on weather
def update_background_gradient(weather):
    # Define gradient colors for each weather condition
    weather_gradients = {
        "clear": ("#FFD700", "#FF8C00"),  # Sunny (gold to orange)
        "cloud": ("#D3D3D3", "#A9A9A9"),  # Cloudy (light gray to dark gray)
        "rain": ("#87CEFA", "#4682B4"),   # Rainy (light blue to steel blue)
        "drizzle": ("#B0E0E6", "#4682B4"),  # Drizzle (powder blue to steel blue)
        "snow": ("#FFFFFF", "#ADD8E6"),   # Snow (white to light blue)
        "storm": ("#696969", "#000000"),  # Storm (dim gray to black)
        "thunder": ("#4B0082", "#000000"),  # Thunderstorm (indigo to black)
        "mist": ("#F5F5DC", "#D2B48C"),   # Mist (beige to tan)
        "fog": ("#DCDCDC", "#A9A9A9"),    # Fog (gainsboro to dark gray)
        "haze": ("#FFE4B5", "#FFDEAD"),   # Haze (moccasin to navajo white)
    }

    # Determine the gradient based on the weather
    for key, gradient in weather_gradients.items():
        if key in weather.lower():
            start_color, end_color = gradient
            break
    else:
        # Default gradient for unrecognized weather
        start_color, end_color = "#FFFFFF", "#87CEEB"  # White to sky blue

    # Convert hex color to RGB
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    # Blend colors linearly
    def blend_color(color1, color2, t):
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

    # Convert colors to RGB
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)

    # Clear the existing gradient
    gradient_canvas.delete("all")

    # Draw the new gradient
    steps = 150  # Number of gradient steps
    for i in range(steps):
        t = i / steps
        blended_rgb = blend_color(start_rgb, end_rgb, t)
        blended_hex = f"#{blended_rgb[0]:02x}{blended_rgb[1]:02x}{blended_rgb[2]:02x}"
        gradient_canvas.create_rectangle(
            0, i * (1100// steps), 2200, (i + 1) * (1100// steps),
            fill=blended_hex, outline=""
        )

# Integrate the gradient update into the `get_weather` function

# Function to fetch and display 5-day weather forecast
def get_forecast(city):
    try:
        api_key = "83420c11e3e148fedf79547f9c946676"
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("cod") != "200":
            messagebox.showerror("Error", f"City not found: {city}")
            return

        # Process forecast data
        forecast_data = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            temp = entry["main"]["temp"]
            weather = entry["weather"][0]["description"]

            if date not in forecast_data:
                forecast_data[date] = {"temps": [], "descriptions": []}

            forecast_data[date]["temps"].append(temp)
            forecast_data[date]["descriptions"].append(weather)

        # Create a summary for each day
        forecast_summary = []
        for date, details in forecast_data.items():
            avg_temp = sum(details["temps"]) / len(details["temps"])
            common_weather = max(set(details["descriptions"]), key=details["descriptions"].count)
            forecast_summary.append(f"{date}: {avg_temp:.1f}°C, {common_weather.capitalize()}")

        # Update the forecast label
        forecast_label.configure(text="\n".join(forecast_summary[:5]))  # Show only 5 days
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve forecast data: {e}")


# Function to get weather and forecast
def get_weather(city=None, icon_label=None):
    if city is None:
        city, country = get_location()
        if not city:
            return

    try:
        # Current weather API call
        api_key = "83420c11e3e148fedf79547f9c946676"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("cod") != 200:
            messagebox.showerror("Error", f"City not found: {city}")
            return

        city_name = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]

        # Load and display weather icon
        icon_path = load_weather_icon(weather)
        weather_icon = Image.open(icon_path)
        weather_icon = weather_icon.resize((100, 100), Image.Resampling.LANCZOS)
        weather_photo = ImageTk.PhotoImage(weather_icon)
        icon_label.configure(image=weather_photo)
        icon_label.image = weather_photo

        # Update text-based weather info
        result_label.configure(
            text=f"City: {city_name}, {country}\n"
                 f"Temperature: {temp}°C\n"
                 f"Weather: {weather.capitalize()}",
        )

        # Update the background gradient
        update_background_gradient(weather)

        recommend_movies(weather) # Recommends movie as per weather

        recommend_song(weather) # Recommends song as per weather

        quote = get_quote(weather)
        quote_label.configure(text=quote)

        # Fetch the 5-day forecast
        get_forecast(city)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve weather data: {e}")


# Function to update clock with date, time, and region
def update_clock():
    city, country = get_location()
    if not city or not country:
        city = "Unknown"
        country = "Unknown"

    tz = pytz.timezone("Asia/Kolkata")  # Set timezone for India
    current_time = datetime.now(tz).strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
    current_date = datetime.now(tz).strftime("%A, %d %B %Y")

    # Update text, font, and color
    clock_label.configure(
        text=f"{current_date}\n{current_time}\n{city}, {country}",
        font=("San Francisco", 16, "bold"),
        text_color="#3b8ed0",corner_radius=20)
    clock_label.after(1000, update_clock)


# Initialize customtkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Set up GUI
root = ctk.CTk()
root.iconbitmap()
root.title("Weather & Entertainment App")
root.geometry("1100x550")
root.resizable(True, True)

# Icon image for the application
image_icon = ImageTk.PhotoImage(Image.open("weather.png"))
root.iconphoto(False, image_icon)

gradient_canvas = Canvas(root, bg="#71C9CE", highlightthickness=0)
gradient_canvas.pack(fill="both", expand=True)

# UI elements
city_font = ctk.CTkFont(family="Roboto", size=15, weight="bold")
heading_font = ctk.CTkFont(family="Roboto", size=15, weight="bold")

# Clock label
clock_label = ctk.CTkLabel(root, font=("Roboto", 14), text_color="black", corner_radius=10)
clock_label.place(relx=0.25, rely=0.365, anchor="center")
update_clock()

# Initialize customtkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Heading for weather
weather_heading = ctk.CTkLabel(root, text="Current Weather", font=heading_font, text_color="#3b8ed0", corner_radius=20)
weather_heading.place(relx=0.25, rely=0.455, anchor="center")

# Heading for recommended movies
movie_heading = ctk.CTkLabel(root, text="Movies to Watch", font=heading_font, text_color="#3b8ed0", corner_radius=20)
movie_heading.place(relx=0.65, rely=0.39, anchor="center")

# Heading for recommended song
song_heading = ctk.CTkLabel(root, text="Recommended Song for This Weather", font=heading_font, text_color="#3b8ed0", corner_radius=20)
song_heading.place(relx=0.65, rely=0.11, anchor="center")

# Heading for inspirational quote
quote_heading = ctk.CTkLabel(root, text="Inspirational Quote for This Weather", font=heading_font, text_color="#3b8ed0", corner_radius=20)
quote_heading.place(relx=0.65, rely=0.735, anchor="center")

# Heading for 5-Day Weather Forecast
forecast_heading = ctk.CTkLabel(root, text="5-Day Weather Forecast", font=heading_font, text_color="#3b8ed0", corner_radius=20)
forecast_heading.place(relx=0.25, rely=0.735, anchor="center")

forecast_label = ctk.CTkLabel(root, text="", width=400, height=120, wraplength=380, anchor="center", justify="center")
forecast_label.place(relx=0.25, rely=0.87, anchor="center")

city_label = ctk.CTkLabel(root, text="Enter Your City", text_color="#3b8ed0", font=city_font, corner_radius=20)
city_label.place(relx=0.25, rely=0.07, anchor="center")

city_entry = ctk.CTkEntry(root, font=("Roboto", 15), text_color="#3b8ed0", width=300)
city_entry.place(relx=0.25, rely=0.14, anchor="center")

search_button = ctk.CTkButton(root, text="Get Weather by City", command=lambda: get_weather(city_entry.get(), icon_label))
search_button.place(relx=0.25, rely=0.21, anchor="center")

location_button = ctk.CTkButton(root, text="Get Weather by Current Location", command=lambda: get_weather(icon_label=icon_label))
location_button.place(relx=0.25, rely=0.28, anchor="center")

mode_button = ctk.CTkButton(root, text="Toggle Dark/Light Mode", command=toggle_mode)
mode_button.place(relx=0.9, rely=0.05, anchor="center")

result_label = ctk.CTkLabel(root, text="", width=400, height=120, corner_radius=20)
result_label.place(relx=0.25, rely=0.58, anchor="center")

song_label = ctk.CTkLabel(root, text="", width=400, height=120,wraplength=380,anchor="center",justify="center")
song_label.place(relx=0.65, rely=0.25, anchor="center")

movie_label = ctk.CTkLabel(root, text="", width=400, height=150)
movie_label.place(relx=0.65, rely=0.55, anchor="center")

quote_label = ctk.CTkLabel(root,text="",width=400,height=120,wraplength=380,anchor="center",justify="center")
quote_label.place(relx=0.65, rely=0.87, anchor="center")

icon_label = ctk.CTkLabel(root, text="")
icon_label.place(relx=0.127, rely=0.54, anchor="center")

play_button = ctk.CTkButton(root, text="Play Song", command=play_song)
play_button.place_forget()

root.mainloop()