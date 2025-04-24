import streamlit as st
from typing import Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

class RealEstateAssistant:
    def __init__(self):
        # Initialize MCP client and agent
        self.model = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3
        )

        self.client = MultiServerMCPClient({
            "realestate": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        })

        self.memory = MemorySaver()

        # Create prompt template with system message
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an Islamic Real Estate AI Assistant:
            - Provide personalized property recommendations
            - Focus on family-friendly and halal-considerate properties
            - Understand nuanced user requirements
            - Give concise, helpful property insights
            - Prioritize mosque proximity and community amenities
            """),
            MessagesPlaceholder(variable_name="messages"),
        ])

        self.agent = self.create_agent()

    def create_agent(self):
        """Create React agent with enhanced capabilities"""
        return create_react_agent(
            self.model,
            self.client.get_tools(),
            checkpointer=self.memory,
            prompt=self.prompt
        )

    def process_query(self, query: str, search_params: Dict = None):
        """Process user query with intelligent filtering"""
        # Include the conversation history in the query
        conversation_history = st.session_state.messages

        if search_params and search_params.get('use_filters', False):
            # Construct enhanced query with filters
            full_query = f"""
            Property Search Details:
            Location: {search_params.get('location', 'Not Specified')}
            Max Budget: ${search_params.get('max_price', 'Unlimited')}
            Min Bedrooms: {search_params.get('min_beds', '1')}
            Min Bathrooms: {search_params.get('min_baths', '1')}
            Mosque Proximity: {'Required' if search_params.get('near_mosque', False) else 'Optional'}
            Halal Financing: {'Required' if search_params.get('halal_finance', False) else 'Optional'}
            Property Type: {search_params.get('property_type', 'Any')}

            User Query: {query}
            """
        else:
            # Just use the original query without filters
            full_query = f"User Query: {query}"

        try:
            response = self.agent.invoke(
                {
                    "messages": [
                        SystemMessage(content=full_query),
                        *[HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"]) for msg in conversation_history],
                        HumanMessage(content=query)
                    ]
                },
                config={
                    "configurable": {"thread_id": "intelligent_search"},
                    "recursion_limit": 5
                }
            )

            # Extract and process response
            processed_response = self.process_agent_response(response)
            return processed_response

        except Exception as e:
            return f"🏠 Oops! Search encountered an issue: {str(e)}"

    def process_agent_response(self, response):
        """Advanced response processing"""
        if isinstance(response, dict) and 'messages' in response:
            messages = response['messages']
            ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]

            if ai_messages:
                return ai_messages[-1]

        return str(response)

def main():
    # Set page configuration with default Streamlit styling
    st.set_page_config(
        page_title="Islamic Real Estate Assistant",
        page_icon="🕌",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Page title
    st.title("🕌 Islamic Real Estate Assistant")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "ai", "content": "As-salamu alaykum! I'm your Islamic Real Estate Assistant. How can I help you find your perfect halal home today?"}
        ]

    # Initialize filters state
    if 'use_filters' not in st.session_state:
        st.session_state.use_filters = False

    # Initialize the assistant
    assistant = RealEstateAssistant()

    # Sidebar - Property filters
    with st.sidebar:
        st.header("Property Search Filters")

        # Toggle for filter usage
        st.session_state.use_filters = st.checkbox("Use Sidebar Filters", st.session_state.use_filters)

        if st.session_state.use_filters:
            st.info("Filters will be applied to your search")
        else:
            st.info("Agent will extract details from chat")

        # Divider
        st.divider()

        # Filter inputs
        location = st.text_input("Location", "Sacramento")

        col1, col2 = st.columns(2)
        with col1:
            min_beds = st.number_input("Min Bedrooms", 1, 10, 3, step=1)
        with col2:
            min_baths = st.number_input("Min Baths", 1, 6, 2, step=1)

        max_price = st.slider("Budget", 100000, 2000000, 500000, 50000, format="$%d")

        col1, col2 = st.columns(2)
        with col1:
            near_mosque = st.checkbox("Near Mosque", True)
        with col2:
            halal_finance = st.checkbox("Halal Financing", True)

        property_type = st.selectbox("Property Type",
                                    ["Any", "Single Family", "Townhouse", "Condo", "Multi-Family"])

        # Show filter status
        if st.session_state.use_filters:
            st.success("✅ Filters will be applied to your search")

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = [
                {"role": "ai", "content": "As-salamu alaykum! I'm your Islamic Real Estate Assistant. How can I help you find your perfect halal home today?"}
            ]

    # Chat display area - using standard Streamlit components
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])

    # Create a form for user input
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input(
            label="Message the assistant",
            key="user_input"
        )
        submit_button = st.form_submit_button("Send")

        # Process the message when form is submitted
        if submit_button and user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Prepare search parameters
            search_params = {
                'use_filters': st.session_state.use_filters,
                'max_price': max_price,
                'min_beds': min_beds,
                'min_baths': min_baths,
                'location': location,
                'near_mosque': near_mosque,
                'property_type': property_type if property_type != "Any" else None,
                'halal_finance': halal_finance
            }

            # Get AI response - pass search params only if using filters
            with st.spinner("Searching for properties..."):
                ai_response = assistant.process_query(user_input, search_params)

            # Add AI response to chat
            st.session_state.messages.append({"role": "ai", "content": ai_response})

            # Rerun to update the UI
            st.rerun()

if __name__ == "__main__":
    main()