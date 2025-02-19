# 📜 WallQuote: Quote Wallpaper Generator

## 📝 Overview

The **WallQuote: Quote Wallpaper Generator** is a Python-based CLI tool that allows users to generate quote wallpapers with custom or random backgrounds. It also provides functionalities for managing quotes, setting wallpapers automatically, and maintaining a collection of background templates.

## 🚀 Features

- Generate wallpapers with **custom quotes and backgrounds**.
- Fetch a **random quote** and create a wallpaper.
- **List, insert, and delete** quotes from a local JSON file.
- **Set the generated wallpaper** as the current desktop background.
- Save and manage **background templates**.

## 🛠️ Installation

### **Prerequisites**

Ensure you have Python 3.6+ installed on your system.

### **Install Dependencies**

```bash
pip install -r requirements.txt
```

## 📌 Usage

Run the script with the following command:

```bash
wallquote [OPTIONS]
```

### 🎨 **Generate Wallpapers**

#### **Create a wallpaper with a custom quote:**

```bash
wallquote --create -q "Your inspiring quote here" -a "Author Name" --show
```

#### **Generate a random wallpaper:**

```bash
wallquote --random --show
```

#### **Set daily quote wallpaper:**

```bash
wallquote --daily
```

### 📖 **Quote Management**

#### **List all quotes:**

```bash
wallquote --quotes --list
```

#### **Insert a new quote:**

```bash
wallquote --quotes --insert "Life is what happens when you're busy making other plans." -a "John Lennon"
```

#### **Delete a quote by ID:**

```bash
wallquote --quotes --delete 2
```

### 🖼️ **Wallpaper Management**

#### **Set the generated wallpaper as desktop wallpaper:**

```bash
wallquote --random --set
```

#### **Save the wallpaper to a specific path:**

```bash
wallquote --create -q "Believe in yourself" --save_path "./my_wallpaper.jpg"
```

### 🌄 **Background Management**

#### **Add a new background template:**

```bash
wallquote --bg_template "./path/to/background.jpg"
```


