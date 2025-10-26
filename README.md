# 🔍 DeepGrep

> **Lightning-fast regex meets AI-powered semantic search**  
> Find exact patterns and contextually relevant matches with intelligent history tracking and REST API integration.

---

## 🛠️ Tech Stack

### Core Development & Language
[![Language](https://img.shields.io/badge/Language-Python-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Caching](https://img.shields.io/badge/Caching-functools.lru__cache-blue)](https://docs.python.org/3/library/functools.html)
[![Data Modeling](https://img.shields.io/badge/Data_Model-Dataclasses-informational)](https://docs.python.org/3/library/dataclasses.html)

### Web Application Stack
[![Backend Framework](https://img.shields.io/badge/Backend-Flask-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![CORS Management](https://img.shields.io/badge/CORS-Flask--CORS-5A2C85.svg?logo=flask&logoColor=white)](https://flask-cors.readthedocs.io/en/latest/)
[![Frontend](https://img.shields.io/badge/Frontend-HTML5%2FCSS3-E34F26.svg?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/Client_Script-JavaScript-F7DF1E.svg?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Database](https://img.shields.io/badge/Database-SQLite-073159.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)

### Search Engines & NLP
[![Custom Regex Engine](https://img.shields.io/badge/Engine-Custom_Matcher-CC3333.svg?style=flat&logo=regex&logoColor=white)](https://github.com/YourUsername/DeepGrep)
[![NLP Library](https://img.shields.io/badge/NLP-spaCy-09A3D5.svg?logo=spacy&logoColor=white)](https://spacy.io/)
[![SpaCy Model](https://img.shields.io/badge/SpaCy_Model-en__core__web__sd-09A3D5.svg)](https://spacy.io/models)
[![Lexical Data](https://img.shields.io/badge/Lexical_Data-NLTK_WordNet-9B2F2A.svg?logo=nativenscript&logoColor=white)](https://www.nltk.org/howto/wordnet.html)

### Quality & Tools
[![Code Quality](https://img.shields.io/badge/Code_Quality-Qodana-orange.svg?logo=jetbrains&logoColor=white)](https://www.jetbrains.com/qodana/)
[![API Testing](https://img.shields.io/badge/API_Testing-Postman-FF6C37.svg?logo=postman&logoColor=white)](https://www.postman.com/)
 
### License
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Quick Start](#-quick-start)
- [API Usage](#-api-usage)
- [Web Interface](#-web-interface)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Dual-Mode Search** | Regex pattern matching along with AI-powered semantic search |
| 🧠 **Semantic Intelligence** | Understands context, finds synonyms, and avoids antonyms |
| 📜 **History Tracking** | Maintains searchable history in SQLite with JSON export |
| 🔌 **REST API** | Full programmatic access via clean JSON endpoints |
| 🌐 **Web Interface** | Responsive UI for quick searches and file uploads |
| ⚡ **Optimized Performance** | Efficient line scanning with intelligent caching |

---

## 📸 Screenshots

> *Coming soon - Add your screenshots here!*

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/deepgrep.git
cd deepgrep

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Start the API server
python3 -m deepgrep.web.app
```

The web interface will be available at **http://localhost:8000**

---

## 🔌 API Usage

### Regex Search

**Endpoint:** `POST /search`

**Request:**
```json
{
  "pattern": "\\d+",
  "text": "User logged in at 14:32, error code 404"
}
```

**Response:**
```json
{
  "matches": ["14", "32", "404"],
  "history": [
    {
      "pattern": "\\d+",
      "timestamp": "2025-10-26T16:00:00",
      "matches_count": 3
    }
  ]
}
```

---

### Semantic Search

**Endpoint:** `POST /semantic`

**Request:**
```json
{
  "keyword": "happy",
  "text": "She felt joyful and delighted after the announcement"
}
```

**Response:**
```json
{
  "matches": [
    {"word": "joyful", "similarity": 0.88},
    {"word": "delighted", "similarity": 0.82}
  ],
  "history": [
    {
      "keyword": "happy",
      "timestamp": "2025-10-26T16:05:00",
      "matches_count": 2
    }
  ]
}
```

---

## 🌐 Web Interface

### How to Use

1. **Open** http://localhost:8000 in your browser
2. **Choose** search mode: Regex or Semantic
3. **Enter** your pattern/keyword and text (or upload a file)
4. **Click** Search
5. **View** results and search history in real-time

---

## 🏗️ Architecture

```
             ┌──────────────────────────┐
             │       Web Frontend       │
             │  (HTML + Tailwind + JS)  │
             │                          │
             │  • Input: Pattern/Keyword│
             │  • Output:               │
             │      - Search Results    │
             │      - Search History    │
             └─────────────┬────────────┘
                           │
                           │ HTTP/REST (JSON)
                           ▼
             ┌──────────────────────────┐
             │       Flask API          │
             │  (Endpoints: /search,    │
             │   /semantic)             │
             │  • Routes requests to    │
             │    Regex or Semantic     │
             │    Engine                │
             │  • Logs history          │
             └─────────────┬────────────┘
                           │
          ┌────────────────┴─────────────────┐
          │                                  │
          ▼                                  ▼
┌─────────────────────┐             ┌─────────────────────┐
│    Regex Engine     │             │  Semantic Engine    │
│  (Pattern Matching) │             │ (SpaCy + WordNet)   │
│  • Fast regex search│             │  • Contextual match │
│  • Backrefs, groups │             │  • Avoid antonyms   │
└─────────────┬───────┘             └─────────────┬───────┘
              │                                   │
              └──────────────┬────────────────────┘
                             ▼
                    ┌──────────────────┐
                    │  Search History  │
                    │   (SQLite DB)    │
                    │  • Logs patterns │
                    │  • Match counts  │
                    │  • Files/context │
                    └──────────────────┘
```

### Key Components

- **Frontend:** Displays search results and history with a responsive interface
- **API Layer:** Single gateway routing to both search engines
- **Regex Engine:** Fast exact pattern matching with support for groups and backreferences
- **Semantic Engine:** AI-powered contextual matching using spaCy and WordNet
- **History Database:** Persistent SQLite storage with full search history

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

[Report Bug](https://github.com/vivekkdagar/deepgrep/issues) · [Request Feature](https://github.com/vivekkdagar/deepgrep/issues)

</div>
