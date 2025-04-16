# 🕌 Islamic Real Estate Assistant

A specialized AI-powered real estate assistant built with Streamlit that caters to the Islamic community's specific housing needs, focusing on family-friendly environments, proximity to mosques, and halal financing options.

![Islamic Real Estate Assistant](https://placehold.co/600x400/e6f7ff/0066cc?text=Islamic+Real+Estate+Assistant&font=OpenSans)

## ✨ Features

- **Personalized Property Recommendations** - AI-powered search tailored to Islamic requirements
- **Mosque Proximity Focus** - Find homes near Islamic centers and mosques
- **Halal Financing Consideration** - Filter properties suitable for Shariah-compliant financing
- **Family-Friendly Properties** - Prioritize neighborhoods ideal for Muslim families
- **Smart Filtering** - Apply detailed search parameters or let the AI interpret your needs
- **Interactive Chat Interface** - Natural language interaction with the AI assistant

## 🛠️ Requirements

### Software Requirements
- Python 3.10+
- SQLite3
- Internet connection (for Groq API access)

### Dependencies
```
streamlit
langchain
langchain-mcp-adapters
langchain-groq
langgraph
pandas
sqlite3
mcp
```

### API Keys
- A Groq API key is required to power the LLM capabilities
- Set your API key as an environment variable:
  ```
  export GROQ_API_KEY=your_api_key_here
  ```

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/islamic-real-estate-assistant.git
   cd islamic-real-estate-assistant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   # Make sure you have SQLite installed
   # The database will be created automatically on first run
   ```

5. **Start the MCP server**
   ```bash
   # In a separate terminal window
   python mcp_server.py
   ```

6. **Launch the Streamlit app**
   ```bash
   streamlit run app.py
   ```

## 📋 How to Use

### Starting the Application
1. Make sure the MCP server is running in one terminal window
2. Run the Streamlit app in another terminal
3. Open your browser to the URL displayed in the terminal (typically http://localhost:8501)

### Using the Chat Interface
1. **Start the conversation** - The AI will greet you with "As-salamu alaykum!"
2. **Ask about properties** - Example queries:
   - "I'm looking for a 3-bedroom house near a mosque in Sacramento"
   - "Find me properties with halal financing options under $500,000"
   - "What's the average price of 4-bedroom homes in midtown?"

### Using the Sidebar Filters
1. **Toggle filters** - Check "Use Sidebar Filters" to apply detailed search constraints
2. **Set parameters**:
   - Location (default: Sacramento)
   - Minimum bedrooms and bathrooms
   - Budget (price slider)
   - Near Mosque option
   - Halal Financing preference
   - Property Type selection

3. **Apply filters** - Your next search will incorporate all selected filter parameters

### Tips for Best Results
- **Be specific about Islamic requirements** - Mention if mosque proximity or halal financing is important
- **Combine filters with chat** - Use filters for standard criteria and chat for nuanced preferences
- **Clear chat** - Use the "Clear Chat" button to start a fresh conversation
- **Mixed queries work well** - "I need a 4-bedroom house near a mosque with a large yard for under $600k"

## 🔧 System Architecture

The system consists of two main components:
1. **Streamlit Frontend** - User interface with chat and filters
2. **MCP Server Backend** - Database interface and AI reasoning capabilities

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  Streamlit UI   │◄─────►│  LangChain AI   │◄─────►│    MCP Server   │
│                 │       │     Agent       │       │                 │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   ▲                        ▲
                                   │                        │
                                   ▼                        ▼
                          ┌─────────────────┐      ┌─────────────────┐
                          │                 │      │                 │
                          │    Groq LLM     │      │  SQLite Database│
                          │                 │      │                 │
                          └─────────────────┘      └─────────────────┘
```

## 🔒 Data Privacy

This application:
- Stores conversation history only in the local session
- Does not persistently store user queries
- Uses SQLite for property data storage locally
- Does not share sensitive information with third parties

## 🤝 Contributing

Contributions to improve the Islamic Real Estate Assistant are welcome! Please:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
