import argparse
import random
from PIL import Image, ImageDraw, ImageFont
import os
import json
import shutil
import ctypes
from datetime import datetime
import pathlib
import textwrap
import requests

QUOTE_FILE = "wallquote/quotes.json"
BACKGROUND_DIR = "wallquote/bg_templates/"
OUTPUT_DIR = "wallquote/saved_bg_pics/"


def load_quotes():
    """
    Loads quotes from a JSON file.

    This function reads quotes from a specified JSON file and returns them as
    a list. If the file does not exist or is empty, it returns an empty list.
    If there is an error decoding the JSON, it also returns an empty list.

    Returns:
        list: A list of quotes loaded from the JSON file.
    """
    if not os.path.exists(QUOTE_FILE):
        return []
    with open(QUOTE_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_quote(quote, author=None):
    """
    Saves a quote to the quotes.json file.

    Args:
        quote (str): The quote to be saved.
        author (str, optional): The author of the quote. Defaults to None.

    Returns:
        None
    """
    quotes = load_quotes()
    if author:
        quotes.append({"id": len(quotes) + 1, "quote": quote, "author": author})
    else:
        quotes.append({"id": len(quotes) + 1, "quote": quote})
    with open(QUOTE_FILE, "w") as file:
        json.dump(quotes, file, indent=4)

def delete_quote(quote_id):
    """
    Deletes a quote with the given id from the quotes.json file.

    Args:
        quote_id (int): The id of the quote to be deleted.

    Returns:
        None
    """
    quotes = load_quotes()
    out_quotes = []
    id_counter = 1
    for quote in quotes:
        if quote.get("id") != quote_id:
            quote["id"] = id_counter
            out_quotes.append(quote)
            id_counter += 1
    with open(QUOTE_FILE, "w") as file:
        json.dump(out_quotes, file, indent=4)

def save_bg_image(image_path, save_dir=BACKGROUND_DIR):
    """
    Saves a background image to the given directory.

    Args:
        image_path (str): The path to the background image file.
        save_dir (str, optional): The directory to save the background image in. Defaults to BACKGROUND_DIR (./saved_bg_pics).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    os.makedirs(save_dir, exist_ok=True)
    shutil.copy(image_path, save_dir)

def load_bg_image(image_path):
    """
    Loads a background image from the given file path.

    Args:
        image_path (str): The path to the background image file.

    Returns:
        PIL.Image.Image: The loaded background image.

    Raises:
        FileNotFoundError: If the image file does not exist at the given path.
        Exception: If there is an error loading the image.
    """
    if image_path is None or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    try:
        return Image.open(image_path)
    except Exception as e:
        raise Exception(f"Error loading image from {image_path}: {e}")
    


def create_wallpaper(quote, author=None, bg_image=None, out_image_path=None):
    """
    Creates a wallpaper image with a given quote and optionally an author.

    This function generates a wallpaper by overlaying a quote (and optionally an author) on a background image.
    If no background image is provided, a random solid color background is used. The text is wrapped and adjusted
    to fit within specified dimensions on the screen.

    Args:
        quote (str): The quote text to be displayed on the wallpaper.
        author (str, optional): The author of the quote. Defaults to None.
        bg_image (PIL.Image.Image, optional): The background image. If None, a random color is used. Defaults to None.
        out_image_path (str, optional): The path to save the generated wallpaper image. If None or invalid, it defaults
                                        to "saved_bg_pics/current_wallpaper.jpg".

    Returns:
        tuple: A tuple containing the path to the saved wallpaper image and the image object itself.
    """

    max_width=800
    max_height=500
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    if bg_image is None:
        random_bg_colors = [
            (234, 231, 226), (215, 226, 232), (185, 203, 217), 
            (252, 201, 197), (254, 221, 216), (207, 227, 226)
        ]
        bg_image = Image.new("RGB", (screen_width, screen_height), color=random.choice(random_bg_colors))
    else:   
        bg_image = bg_image.resize((screen_width, screen_height))
    draw = ImageDraw.Draw(bg_image)
    try:
        font = ImageFont.truetype("arial.ttf", size=80)  
    except IOError:
        font = ImageFont.load_default()
    max_chars_per_line = 30 
    wrapped_text = textwrap.fill(quote, width=max_chars_per_line)
    font_size = 80
    while True:
        font = ImageFont.truetype("arial.ttf", font_size)
        bbox = draw.textbbox((0, 0), wrapped_text, font=font) 
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_width <= max_width and text_height <= max_height:
            break
        font_size -= 5 
    author_font_size = font_size // 2
    author_font = ImageFont.truetype("arial.ttf", author_font_size) if author else None
    author_text = f"- {author}" if author else ""
    author_bbox = draw.textbbox((0, 0), author_text, font=author_font) if author else (0, 0, 0, 0)
    author_width, author_height = author_bbox[2] - author_bbox[0], author_bbox[3] - author_bbox[1]
    x = (screen_width - text_width) // 2
    y = (screen_height - (text_height + author_height + 40)) // 2  
    overlay = Image.new("RGBA", bg_image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    rect_margin = 40  
    rect_x1, rect_y1 = x - rect_margin, y - rect_margin
    rect_x2, rect_y2 = x + text_width + rect_margin, y + text_height + author_height + rect_margin + 20  
    overlay_draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill=(0, 0, 0, 120)) 
    bg_image = Image.alpha_composite(bg_image.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(bg_image)
    draw.text((x, y), wrapped_text, font=font, fill="white", align="center")
    if author:
        author_x = rect_x2 - author_width - 20 
        author_y = rect_y2 - author_height - 20 
        draw.text((author_x, author_y), author_text, font=author_font, fill="white", align="right")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if out_image_path is None or not os.path.exists(out_image_path):
        out_image_path = pathlib.Path(os.path.join(OUTPUT_DIR, "current_wallpaper.jpg")).absolute().__str__()
    else:
        out_image_path = pathlib.Path(os.path.join(out_image_path, "saved_wallpaper.jpg")).absolute().__str__()
    bg_image = bg_image.convert("RGB")
    bg_image.save(out_image_path)
    return out_image_path, bg_image

def set_wallpaper(image_path):
    """
    Sets the wallpaper to the given image file.

    Args:
        image_path (str): The path to the image file to be set as the wallpaper.

    Raises:
        FileNotFoundError: If the image file does not exist at the given path.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File {image_path} not found!")
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

def choose_random_bg_template():
    """
    Returns a random background template image path from the BACKGROUND_DIR.
    
    Returns:
        str: The path to the random background template image.
    """
    images = [img for img in os.listdir(BACKGROUND_DIR) if img.endswith((".png", ".jpg", ".jpeg"))]
    return os.path.join(BACKGROUND_DIR, random.choice(images)) if images else None

def get_random_quote(from_online=False, daily_quote=False):
    try:
        if not from_online:
            raise Exception
        data = requests.get("https://stoic.tekloon.net/stoic-quote").json()["data"]
        quote, author = data["quote"], data["author"]
    except Exception as e:
        if daily_quote:
            day_of_year = datetime.now().timetuple().tm_yday
            quotes = load_quotes()
            if not quotes:
                print("No quotes found! Add some first.")
                return "", ""
            today_quote = quotes[day_of_year % len(quotes)]
            quote, author = today_quote.get("quote"), today_quote.get("author")
        else:
            quotes = load_quotes()
            if not quotes:
                print("No quotes found! Add some first.")
                return "", ""
            random_quote = random.choice(quotes)
            quote, author = random_quote.get("quote"), random_quote.get("author")
    return quote, author

def set_daily_wallpaper(from_online=False):
    """
    Sets the desktop wallpaper to a daily quote wallpaper.

    This function selects a quote based on the current day of the year and
    creates a wallpaper with that quote. The wallpaper is then set as the
    desktop background.

    The function uses a predefined list of quotes loaded from a JSON file.
    If no quotes are available, it prints an error message and exits.

    The background image for the wallpaper is randomly chosen from the
    BACKGROUND_DIR directory.

    Raises:
        FileNotFoundError: If no background images are found or if the wallpaper
        image cannot be set.
    """
    quote, author = get_random_quote(from_online)
    path, _ = create_wallpaper(quote, author, bg_image=load_bg_image(choose_random_bg_template()))
    set_wallpaper(path)

def get_random_quote_wallpaper(out_image_path=None, from_online=False):
    """
    Returns a random quote wallpaper image path and the image object itself.

    If no quotes are available, it prints an error message and returns None.

    The background image for the wallpaper is randomly chosen from the
    BACKGROUND_DIR directory.

    Args:
        out_image_path (str, optional): The path to save the wallpaper image to.

    Returns:
        tuple: A tuple containing the path to the wallpaper image and the image object itself.
    """
    quote, author = get_random_quote(from_online=from_online, daily_quote=False)
    template = choose_random_bg_template()
    path, img = create_wallpaper(quote, author, bg_image=load_bg_image(template) if template else None, out_image_path=out_image_path)
    return path, img

def show_quotes_list(num):
    quotes = load_quotes()
    if len(quotes) == 0:
        print("No quotes found! Add some first.")
    for quote in quotes[-num:]:
        print(f"{quote.get('id')} - \"{quote.get('quote')}\" by \"{quote.get('author', 'Unknown')}\"")


def main():
    parser = argparse.ArgumentParser(
        prog="wallquote",
        description="📜 Quote Wallpaper Generator: Create and manage quote wallpapers.",
        epilog="Thanks for using %(prog)s! 😊"
    )

    # ------------------[ Main Actions ]------------------ #
    action_group = parser.add_argument_group("🟢 Main Actions (Choose One)")
    exclusive_actions = action_group.add_mutually_exclusive_group(required=True)
    exclusive_actions.add_argument("--daily", action="store_true", help="📆 Set the daily quote wallpaper.")
    exclusive_actions.add_argument("--random", action="store_true", help="🎲 Generate a random quote wallpaper.")
    exclusive_actions.add_argument("--create", action="store_true", help="🎨 Create a new wallpaper with a custom quote.")
    exclusive_actions.add_argument("--quotes", action="store_true", help="📝 Manage quotes: list, insert, or delete.")
    exclusive_actions.add_argument("--bg_template", metavar="PATH", type=str, help="🖼️ Save a new background template to ./bg_templates.")

    # ------------------[ Quote Management ]------------------ #
    quotes_group = parser.add_argument_group("📖 Quote Management (Use with --quotes)")
    quotes_exclusive = quotes_group.add_mutually_exclusive_group()
    quotes_exclusive.add_argument("-l", "--limit", metavar="NUMBER", default=50, type=int, help="📜 Lists the last limit NUMBER of quotes.")
    quotes_exclusive.add_argument("-d", "--delete", metavar="QUOTE_ID", type=int, help="❌ Delete a quote by its ID. If ID is negative, deletes all quotes.")
    quotes_exclusive.add_argument("-i", "--insert", metavar="QUOTE", type=str, help="➕ Insert a new quote (use -a for author).")

    # ------------------[ Wallpaper Settings ]------------------ #
    wallpaper_group = parser.add_argument_group("🖼️ Wallpaper Options (Use with --random or --create)")
    wallpaper_group.add_argument("--set", action="store_true", help="🏞️ Set the generated wallpaper as the current wallpaper.")
    wallpaper_group.add_argument("--save_path", metavar="SAVE_PATH", default=None, type=str, help="💾 Save wallpaper to a specific path.")
    wallpaper_group.add_argument("--show", action="store_true", help="👀 Show the generated wallpaper.")

    # ------------------[ Custom Wallpaper Creation ]------------------ #
    create_group = parser.add_argument_group("🎭 Custom Wallpaper Creation (Use with --create)")
    create_group.add_argument("-q", "--quote", type=str, help="🖋️ Quote text for wallpaper (Optional). If not specified, will generate random online or offline quote depending on --online.")
    create_group.add_argument("-b", "--background", metavar="PATH", type=str, help="🌄 Background image path (Optional).")
    create_group.add_argument("-a", "--author", metavar="AUTHOR", type=str, default=None, help="✍️ Author of the quote (Optional).")

    # ------------------[ Api Options ]------------------ #
    api_group = parser.add_argument_group("🌐 API Options")
    api_group.add_argument("--online", action="store_true", help="🌐 Fetch a random stoic quote from an API. If API doesn't work, defaults to quotes from quotes.json file.")

    args = parser.parse_args()

    # Handling different actions
    wallpaper_path = None
    wallpaper = None
    if args.daily:
        set_daily_wallpaper(args.online)
    elif args.random:
        wallpaper_path, wallpaper = get_random_quote_wallpaper(args.save_path, args.online)
    elif args.create:
        if args.quote:
            quote, author = args.quote, args.author
        else:
            quote, author = get_random_quote(args.online)
        wallpaper_path, wallpaper = create_wallpaper(quote, author, load_bg_image(args.background) if args.background else None, args.save_path)
    elif args.quotes:
        if args.delete is not None:
            if args.delete < 0:
                os.remove(QUOTE_FILE)
            else:
                delete_quote(args.delete)
                show_quotes_list(args.limit)
        elif args.insert:
            save_quote(args.insert, args.author)
            show_quotes_list(args.limit)
        elif args.limit:
            show_quotes_list(args.limit)
    elif args.bg_template:
        save_bg_image(args.bg_template, BACKGROUND_DIR)
    if wallpaper_path:
        if args.set:
            set_wallpaper(wallpaper_path)
        if args.show:
            if wallpaper is None:
                print("No wallpaper to show!")
            else:
                wallpaper.show("wallpaper")
    if wallpaper_path:
        print(f"✅ Wallpaper saved at: {wallpaper_path}")

if __name__ == "__main__":
    main()
