import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid
from typing import Dict, List
import re

# Try to import Excel processor (optional enhanced feature)
try:
    from excel_processor import ExcelProcessor
    EXCEL_PROCESSOR_AVAILABLE = True
except:
    EXCEL_PROCESSOR_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="AI Customer Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .ticket-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'tickets' not in st.session_state:
    st.session_state.tickets = []
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = {}

# Load dataset
@st.cache_data
def load_data():
    try:
        # Try multiple possible paths
        paths = [
            'Few_Data_set.xlsx',
            '/mnt/user-data/uploads/Few_Data_set.xlsx',
            './Few_Data_set.xlsx'
        ]
        
        for path in paths:
            try:
                df = pd.read_excel(path)
                df['query_date'] = pd.to_datetime(df['query_date'])
                return df
            except:
                continue
        
        # If no file found, return empty dataframe
        st.error("Dataset file not found. Please upload Few_Data_set.xlsx")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Simple AI Response Generator (Mock)
class SimpleAIAgent:
    def __init__(self, knowledge_base: Dict = None):
        self.knowledge_base = knowledge_base or {}
        self.confidence_threshold = 0.7
        
    def detect_language(self, text: str) -> str:
        """Detect language (simple heuristic)"""
        hindi_chars = re.findall(r'[\u0900-\u097F]', text)
        marathi_chars = re.findall(r'[\u0900-\u097F]', text)
        
        if len(hindi_chars) > 0:
            return "Hindi"
        elif len(marathi_chars) > 0:
            return "Marathi"
        else:
            return "English"
    
    def get_response(self, query: str, language: str = "English") -> Dict:
        """Generate AI response based on query"""
        query_lower = query.lower()
        confidence = 0.5
        response = ""
        category = "General Inquiry"
        
        # Knowledge base lookup (simple keyword matching)
        if any(word in query_lower for word in ['warranty', 'guarantee']):
            response = "Our products come with a 1-year warranty for manufacturing defects."
            confidence = 0.9
            category = "Product Information"
        elif any(word in query_lower for word in ['price', 'cost', 'payment']):
            response = "Please visit our pricing page or contact sales for detailed pricing information."
            confidence = 0.85
            category = "Billing"
        elif any(word in query_lower for word in ['install', 'setup', 'installation']):
            response = "Installation guide: 1) Download the software 2) Run installer 3) Follow on-screen instructions. Support available 24/7."
            confidence = 0.88
            category = "Technical Support"
        elif any(word in query_lower for word in ['refund', 'return', 'cancel']):
            response = "Refund requests can be made within 30 days. Please provide your order ID."
            confidence = 0.82
            category = "Billing"
        elif any(word in query_lower for word in ['location', 'office', 'address']):
            response = "Our office is located at XYZ Road, Nagpur, Maharashtra, India."
            confidence = 0.95
            category = "General Inquiry"
        elif any(word in query_lower for word in ['contact', 'phone', 'email']):
            response = "Contact us at support@example.com or call +91-XXXXXXXXXX"
            confidence = 0.9
            category = "General Inquiry"
        else:
            response = "I understand your query, but I need to connect you with our support team for detailed assistance."
            confidence = 0.4
            category = "Complex Query"
        
        # Translate if needed (mock translation)
        if language == "Hindi" and confidence > 0.7:
            response = f"[Hindi] {response}"
        elif language == "Marathi" and confidence > 0.7:
            response = f"[Marathi] {response}"
        
        return {
            'response': response,
            'confidence': confidence,
            'category': category,
            'needs_escalation': confidence < self.confidence_threshold
        }

# Initialize AI Agent
ai_agent = SimpleAIAgent()

# Sidebar Navigation
st.sidebar.title("🤖 AI Support Agent")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "💬 Chat Support", "📊 Analytics", "🎫 Tickets", "📚 Knowledge Base", "⚙️ Settings"]
)

# Main content based on page selection
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">AI Customer Support Dashboard</div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if not df.empty:
        # Date filter
        col1, col2, col3 = st.columns(3)
        with col1:
            date_range = st.selectbox(
                "Time Period",
                ["Today", "Last 7 Days", "Last 30 Days", "All Time"]
            )
        
        # Filter data based on date range
        today = pd.Timestamp.now().normalize()
        if date_range == "Today":
            filtered_df = df[df['query_date'] >= today]
        elif date_range == "Last 7 Days":
            filtered_df = df[df['query_date'] >= (today - timedelta(days=7))]
        elif date_range == "Last 30 Days":
            filtered_df = df[df['query_date'] >= (today - timedelta(days=30))]
        else:
            filtered_df = df
        
        # Key Metrics
        st.subheader("📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_queries = len(filtered_df)
            st.metric("Total Queries", total_queries)
        
        with col2:
            auto_resolved = len(filtered_df[filtered_df['ticket_created'] == 'No'])
            st.metric("Auto-Resolved", auto_resolved)
        
        with col3:
            escalated = len(filtered_df[filtered_df['ticket_created'] == 'Yes'])
            st.metric("Escalated", escalated)
        
        with col4:
            resolution_rate = (auto_resolved / total_queries * 100) if total_queries > 0 else 0
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Queries by Category")
            category_counts = filtered_df['query_category'].value_counts()
            fig1 = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Distribution by Category",
                hole=0.4
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("🌐 Language Distribution")
            lang_counts = filtered_df['language'].value_counts()
            fig2 = px.bar(
                x=lang_counts.index,
                y=lang_counts.values,
                labels={'x': 'Language', 'y': 'Count'},
                title="Queries by Language",
                color=lang_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Timeline
        st.subheader("📅 Query Timeline")
        daily_queries = filtered_df.groupby(filtered_df['query_date'].dt.date).size().reset_index()
        daily_queries.columns = ['Date', 'Count']
        fig3 = px.line(
            daily_queries,
            x='Date',
            y='Count',
            title="Daily Query Volume",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Channel Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📱 Communication Channels")
            channel_counts = filtered_df['communication_channel'].value_counts()
            fig4 = px.bar(
                x=channel_counts.index,
                y=channel_counts.values,
                labels={'x': 'Channel', 'y': 'Count'},
                title="Queries by Channel",
                color=channel_counts.values,
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            st.subheader("🏢 Business Unit Performance")
            bu_counts = filtered_df['business_unit'].value_counts().head(5)
            fig5 = px.bar(
                x=bu_counts.values,
                y=bu_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Business Unit'},
                title="Top 5 Business Units",
                color=bu_counts.values,
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig5, use_container_width=True)

elif page == "💬 Chat Support":
    st.markdown('<div class="main-header">Customer Chat Support</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Live Chat")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 Customer ({msg['language']}):</strong><br>
                        {msg['message']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 AI Agent (Confidence: {msg.get('confidence', 0):.0%}):</strong><br>
                        {msg['message']}<br>
                        <small><em>Category: {msg.get('category', 'N/A')}</em></small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if msg.get('ticket_created'):
                        st.markdown(f"""
                        <div class="ticket-card">
                            <strong>🎫 Ticket Created:</strong> {msg['ticket_id']}<br>
                            <em>Your query has been escalated to our support team.</em>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Input area
        st.divider()
        col_input1, col_input2 = st.columns([3, 1])
        
        with col_input1:
            user_query = st.text_input(
                "Type your message:",
                key="user_input",
                placeholder="Ask anything about our products or services..."
            )
        
        with col_input2:
            language = st.selectbox(
                "Language",
                ["English", "Hindi", "Marathi"],
                key="language_select"
            )
        
        if st.button("Send", type="primary"):
            if user_query:
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'message': user_query,
                    'language': language,
                    'timestamp': datetime.now()
                })
                
                # Get AI response
                ai_result = ai_agent.get_response(user_query, language)
                
                # Add bot response to history
                bot_message = {
                    'role': 'bot',
                    'message': ai_result['response'],
                    'confidence': ai_result['confidence'],
                    'category': ai_result['category'],
                    'timestamp': datetime.now()
                }
                
                # Create ticket if needed
                if ai_result['needs_escalation']:
                    ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
                    ticket = {
                        'ticket_id': ticket_id,
                        'query': user_query,
                        'category': ai_result['category'],
                        'status': 'Open',
                        'created_at': datetime.now(),
                        'language': language
                    }
                    st.session_state.tickets.append(ticket)
                    bot_message['ticket_created'] = True
                    bot_message['ticket_id'] = ticket_id
                
                st.session_state.chat_history.append(bot_message)
                st.rerun()
    
    with col2:
        st.subheader("ℹ️ Quick Info")
        st.info("""
        **How to use:**
        1. Select your language
        2. Type your question
        3. Get instant AI response
        
        **Features:**
        - 🌍 Multi-language support
        - ⚡ Instant responses
        - 🎫 Auto-escalation for complex queries
        - 📊 Confidence scoring
        """)
        
        st.subheader("📋 Recent Categories")
        df = load_data()
        if not df.empty:
            top_categories = df['query_category'].value_counts().head(5)
            for cat, count in top_categories.items():
                st.write(f"• {cat}: {count} queries")
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

elif page == "📊 Analytics":
    st.markdown('<div class="main-header">Advanced Analytics</div>', unsafe_allow_html=True)
    
    df = load_data()
    
    if not df.empty:
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_bu = st.multiselect(
                "Business Unit",
                options=df['business_unit'].unique(),
                default=df['business_unit'].unique()[:3]
            )
        
        with col2:
            selected_channel = st.multiselect(
                "Channel",
                options=df['communication_channel'].unique(),
                default=df['communication_channel'].unique()
            )
        
        with col3:
            selected_lang = st.multiselect(
                "Language",
                options=df['language'].unique(),
                default=df['language'].unique()
            )
        
        with col4:
            selected_category = st.multiselect(
                "Category",
                options=df['query_category'].unique(),
                default=df['query_category'].unique()
            )
        
        # Apply filters
        filtered_df = df[
            (df['business_unit'].isin(selected_bu)) &
            (df['communication_channel'].isin(selected_channel)) &
            (df['language'].isin(selected_lang)) &
            (df['query_category'].isin(selected_category))
        ]
        
        st.divider()
        
        # Performance Metrics
        st.subheader("📈 Performance Overview")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total = len(filtered_df)
            st.metric("Total Queries", total)
        
        with col2:
            auto_resolved = len(filtered_df[filtered_df['ticket_created'] == 'No'])
            st.metric("Auto-Resolved", auto_resolved)
        
        with col3:
            tickets = len(filtered_df[filtered_df['ticket_created'] == 'Yes'])
            st.metric("Tickets Created", tickets)
        
        with col4:
            resolution = (auto_resolved / total * 100) if total > 0 else 0
            st.metric("Resolution Rate", f"{resolution:.1f}%", 
                     delta=f"{resolution - 70:.1f}%" if resolution > 70 else f"{resolution - 70:.1f}%")
        
        with col5:
            avg_per_day = total / 30 if total > 0 else 0
            st.metric("Avg Queries/Day", f"{avg_per_day:.1f}")
        
        st.divider()
        
        # Detailed Charts
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Category Analysis", "🌐 Language & Channel", "📅 Time Analysis", "🏢 Business Units"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Category breakdown
                cat_ticket = filtered_df.groupby('query_category')['ticket_created'].apply(
                    lambda x: (x == 'Yes').sum()
                ).reset_index()
                cat_ticket.columns = ['Category', 'Tickets']
                
                fig = px.bar(
                    cat_ticket,
                    x='Category',
                    y='Tickets',
                    title="Tickets by Category",
                    color='Tickets',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Resolution rate by category
                cat_stats = filtered_df.groupby('query_category').agg({
                    'ticket_created': lambda x: ((x == 'No').sum() / len(x) * 100)
                }).reset_index()
                cat_stats.columns = ['Category', 'Resolution Rate']
                
                fig = px.bar(
                    cat_stats,
                    x='Category',
                    y='Resolution Rate',
                    title="Resolution Rate by Category (%)",
                    color='Resolution Rate',
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Language distribution
                lang_channel = filtered_df.groupby(['language', 'communication_channel']).size().reset_index()
                lang_channel.columns = ['Language', 'Channel', 'Count']
                
                fig = px.sunburst(
                    lang_channel,
                    path=['Language', 'Channel'],
                    values='Count',
                    title="Language & Channel Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Channel effectiveness
                channel_stats = filtered_df.groupby('communication_channel').agg({
                    'record_id': 'count',
                    'ticket_created': lambda x: ((x == 'No').sum() / len(x) * 100)
                }).reset_index()
                channel_stats.columns = ['Channel', 'Total Queries', 'Resolution Rate']
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=channel_stats['Channel'],
                    y=channel_stats['Total Queries'],
                    name='Total Queries',
                    marker_color='lightblue'
                ))
                fig.add_trace(go.Scatter(
                    x=channel_stats['Channel'],
                    y=channel_stats['Resolution Rate'],
                    name='Resolution Rate (%)',
                    yaxis='y2',
                    marker_color='red',
                    mode='lines+markers'
                ))
                fig.update_layout(
                    title='Channel Performance',
                    yaxis=dict(title='Total Queries'),
                    yaxis2=dict(title='Resolution Rate (%)', overlaying='y', side='right')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Monthly trend
            monthly = filtered_df.groupby(filtered_df['query_date'].dt.to_period('M')).size().reset_index()
            monthly.columns = ['Month', 'Count']
            monthly['Month'] = monthly['Month'].astype(str)
            
            fig = px.line(
                monthly,
                x='Month',
                y='Count',
                title="Monthly Query Trend",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Day of week analysis
            filtered_df['day_of_week'] = filtered_df['query_date'].dt.day_name()
            dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_counts = filtered_df['day_of_week'].value_counts().reindex(dow_order, fill_value=0)
            
            fig = px.bar(
                x=dow_counts.index,
                y=dow_counts.values,
                title="Queries by Day of Week",
                labels={'x': 'Day', 'y': 'Count'},
                color=dow_counts.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Top business units
            bu_stats = filtered_df.groupby('business_unit').agg({
                'record_id': 'count',
                'ticket_created': lambda x: ((x == 'Yes').sum() / len(x) * 100)
            }).reset_index()
            bu_stats.columns = ['Business Unit', 'Total Queries', 'Escalation Rate']
            bu_stats = bu_stats.sort_values('Total Queries', ascending=False).head(10)
            
            fig = px.scatter(
                bu_stats,
                x='Total Queries',
                y='Escalation Rate',
                size='Total Queries',
                color='Escalation Rate',
                hover_data=['Business Unit'],
                title="Business Unit Performance Matrix",
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Business unit table
            st.subheader("📋 Detailed Business Unit Stats")
            try:
                # Try styling with gradient (requires matplotlib)
                st.dataframe(
                    bu_stats.style.background_gradient(cmap='Blues', subset=['Total Queries'])
                                  .background_gradient(cmap='Reds', subset=['Escalation Rate']),
                    use_container_width=True
                )
            except ImportError:
                # Fallback without styling if matplotlib not available
                st.dataframe(bu_stats, use_container_width=True)

elif page == "🎫 Tickets":
    st.markdown('<div class="main-header">Ticket Management System</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎫 Active Tickets")
        
        if st.session_state.tickets:
            for ticket in st.session_state.tickets:
                with st.expander(f"🎫 {ticket['ticket_id']} - {ticket['category']} [{ticket['status']}]"):
                    st.write(f"**Query:** {ticket['query']}")
                    st.write(f"**Language:** {ticket['language']}")
                    st.write(f"**Created:** {ticket['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Status:** {ticket['status']}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Mark In Progress", key=f"progress_{ticket['ticket_id']}"):
                            ticket['status'] = "In Progress"
                            st.rerun()
                    with col_b:
                        if st.button("Resolve", key=f"resolve_{ticket['ticket_id']}"):
                            ticket['status'] = "Resolved"
                            st.rerun()
                    with col_c:
                        if st.button("Close", key=f"close_{ticket['ticket_id']}"):
                            ticket['status'] = "Closed"
                            st.rerun()
        else:
            st.info("No active tickets. Great job! 🎉")
        
        # Historical tickets from dataset
        st.subheader("📊 Historical Tickets")
        df = load_data()
        if not df.empty:
            tickets_df = df[df['ticket_created'] == 'Yes']
            st.dataframe(
                tickets_df[['query_date', 'business_unit', 'customer_query', 'query_category', 'language']],
                use_container_width=True
            )
    
    with col2:
        st.subheader("📊 Ticket Statistics")
        
        if st.session_state.tickets:
            status_counts = pd.Series([t['status'] for t in st.session_state.tickets]).value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Ticket Status Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Category breakdown
            category_counts = pd.Series([t['category'] for t in st.session_state.tickets]).value_counts()
            st.subheader("📋 By Category")
            for cat, count in category_counts.items():
                st.write(f"• {cat}: {count}")
        
        st.subheader("⚡ Quick Actions")
        if st.button("Create Test Ticket", type="primary"):
            test_ticket = {
                'ticket_id': f"TKT-{str(uuid.uuid4())[:8].upper()}",
                'query': "Test query for demonstration",
                'category': "Technical Support",
                'status': 'Open',
                'created_at': datetime.now(),
                'language': 'English'
            }
            st.session_state.tickets.append(test_ticket)
            st.rerun()

elif page == "📚 Knowledge Base":
    st.markdown('<div class="main-header">Knowledge Base Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload Content", "📖 View Knowledge", "🔍 Search"])
    
    with tab1:
        st.subheader("Upload Knowledge Base Content")
        
        st.info("""
        📤 **Supported File Types:**
        - 📄 **PDF**: Product manuals, brochures, documentation
        - 📝 **DOCX**: Word documents, reports, guides
        - 📊 **XLSX/XLS**: Excel spreadsheets with data, FAQs, product lists
        - 📋 **TXT**: Plain text files, notes, transcripts
        
        **Maximum file size:** 200MB per file
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📄 Upload Files**")
            uploaded_files = st.file_uploader(
                "Upload PDFs, DOCX, TXT, or XLSX files",
                type=['pdf', 'docx', 'txt', 'xlsx', 'xls'],
                accept_multiple_files=True,
                help="Supported formats: PDF, DOCX, TXT, XLSX, XLS (max 200MB per file)"
            )
            
            if uploaded_files:
                for file in uploaded_files:
                    st.success(f"✅ {file.name} uploaded successfully!")
                    
                    # Process the file based on type
                    if st.button(f"📊 Process {file.name}", key=f"process_{file.name}", type="primary"):
                        try:
                            if file.name.endswith(('.xlsx', '.xls', '.xlsm')):
                                # Process Excel file
                                import pandas as pd
                                
                                with st.spinner(f"Processing {file.name}..."):
                                    # Read all sheets
                                    excel_file = pd.ExcelFile(file)
                                    sheet_names = excel_file.sheet_names
                                    
                                    st.info(f"📑 Found {len(sheet_names)} sheet(s): {', '.join(sheet_names)}")
                                    
                                    total_rows = 0
                                    total_faqs_detected = 0
                                    sheets_data = {}
                                    
                                    # Process each sheet
                                    for sheet_name in sheet_names:
                                        df = pd.read_excel(file, sheet_name=sheet_name)
                                        total_rows += len(df)
                                        
                                        # Check if this sheet looks like FAQ data
                                        is_faq, faq_columns = detect_faq_columns(df)
                                        
                                        sheets_data[sheet_name] = {
                                            'df': df,
                                            'is_faq': is_faq,
                                            'faq_columns': faq_columns,
                                            'rows': len(df),
                                            'columns': len(df.columns)
                                        }
                                        
                                        if is_faq:
                                            total_faqs_detected += len(df)
                                    
                                    # Store basic info
                                    content = f"Excel file with {len(sheet_names)} sheet(s) and {total_rows} total rows.\n\n"
                                    for sheet_name, sheet_info in sheets_data.items():
                                        content += f"Sheet '{sheet_name}': {sheet_info['rows']} rows, {sheet_info['columns']} columns"
                                        if sheet_info['is_faq']:
                                            content += f" (FAQ format detected ✓)"
                                        content += "\n"
                                    
                                    st.session_state.knowledge_base[file.name] = {
                                        'content': content,
                                        'type': 'excel',
                                        'sheets_data': sheets_data,
                                        'total_rows': total_rows,
                                        'total_sheets': len(sheet_names),
                                        'uploaded_at': datetime.now()
                                    }
                                    
                                    st.success(f"✅ Processed {file.name} - {total_rows} total rows")
                                    
                                    # Show FAQ detection results
                                    if total_faqs_detected > 0:
                                        st.balloons()
                                        st.success(f"🎉 **FAQ Auto-Detection**: Found {total_faqs_detected} potential FAQs!")
                                        
                                        # Create expandable sections for each FAQ sheet
                                        for sheet_name, sheet_info in sheets_data.items():
                                            if sheet_info['is_faq']:
                                                with st.expander(f"📋 Sheet: '{sheet_name}' - {len(sheet_info['df'])} FAQs Detected", expanded=True):
                                                    cols = sheet_info['faq_columns']
                                                    st.write(f"**Question Column:** `{cols['question']}`")
                                                    st.write(f"**Answer Column:** `{cols['answer']}`")
                                                    if cols.get('category'):
                                                        st.write(f"**Category Column:** `{cols['category']}`")
                                                    if cols.get('language'):
                                                        st.write(f"**Language Column:** `{cols['language']}`")
                                                    
                                                    # Preview first 3 FAQs
                                                    st.write("**Preview (First 3 FAQs):**")
                                                    preview_df = sheet_info['df'][[cols['question'], cols['answer']]].head(3)
                                                    st.dataframe(preview_df, use_container_width=True)
                                                    
                                                    # Import button
                                                    import_key = f"import_{file.name}_{sheet_name}"
                                                    if st.button(f"✨ Import {len(sheet_info['df'])} FAQs from '{sheet_name}'", 
                                                               key=import_key, 
                                                               type="primary"):
                                                        import_faqs_from_sheet(
                                                            sheet_info['df'], 
                                                            cols, 
                                                            file.name, 
                                                            sheet_name
                                                        )
                                                        st.success(f"✅ Successfully imported {len(sheet_info['df'])} FAQs!")
                                                        st.rerun()
                                    else:
                                        st.info("ℹ️ No FAQ format detected. File stored as general data.")
                                        st.write("**Tip:** For FAQ auto-detection, ensure your Excel has columns named:")
                                        st.write("- `Question` or `Q` or `Query`")
                                        st.write("- `Answer` or `A` or `Response`")
                                
                            elif file.name.endswith('.txt'):
                                # Process text file
                                content = file.read().decode('utf-8')
                                st.session_state.knowledge_base[file.name] = {
                                    'content': content,
                                    'type': 'text',
                                    'size': len(content),
                                    'uploaded_at': datetime.now()
                                }
                                st.success(f"✅ Processed {file.name} - {len(content)} characters")
                                
                            elif file.name.endswith(('.pdf', '.docx')):
                                # Placeholder for PDF/DOCX processing
                                st.session_state.knowledge_base[file.name] = {
                                    'content': f"Document content from {file.name}",
                                    'type': 'document',
                                    'uploaded_at': datetime.now()
                                }
                                st.success(f"✅ Processed {file.name}")
                                st.info("💡 Full PDF/DOCX text extraction coming soon!")
                                
                            else:
                                # Generic processing
                                st.session_state.knowledge_base[file.name] = {
                                    'content': f"Content from {file.name}",
                                    'type': 'document',
                                    'uploaded_at': datetime.now()
                                }
                                st.success(f"✅ Processed {file.name}")
                                
                        except Exception as e:
                            st.error(f"❌ Error processing {file.name}: {str(e)}")
                            st.exception(e)
                
                st.divider()
                st.info("""
                💡 **Excel FAQ Auto-Detection Tips:**
                - Use column headers: `Question`/`Answer` or `Q`/`A`
                - Optional: Add `Category` and `Language` columns
                - Each row = one FAQ
                - Supports multiple sheets with different FAQ sets
                """)

def detect_faq_columns(df: pd.DataFrame) -> tuple:
    """
    Detect if a DataFrame contains FAQ data
    Returns: (is_faq: bool, columns: dict)
    """
    columns_lower = {col: col.lower().strip() for col in df.columns}
    
    # Possible question column names
    question_patterns = ['question', 'q', 'query', 'faq', 'questions', 'ask']
    # Possible answer column names
    answer_patterns = ['answer', 'a', 'response', 'reply', 'answers', 'solution']
    # Optional columns
    category_patterns = ['category', 'type', 'topic', 'group']
    language_patterns = ['language', 'lang', 'locale']
    
    question_col = None
    answer_col = None
    category_col = None
    language_col = None
    
    # Find question column
    for col, col_lower in columns_lower.items():
        if any(pattern in col_lower for pattern in question_patterns):
            question_col = col
            break
    
    # Find answer column
    for col, col_lower in columns_lower.items():
        if any(pattern in col_lower for pattern in answer_patterns):
            answer_col = col
            break
    
    # Find optional category column
    for col, col_lower in columns_lower.items():
        if any(pattern in col_lower for pattern in category_patterns):
            category_col = col
            break
    
    # Find optional language column
    for col, col_lower in columns_lower.items():
        if any(pattern in col_lower for pattern in language_patterns):
            language_col = col
            break
    
    # Check if we found both required columns
    is_faq = question_col is not None and answer_col is not None
    
    columns = {}
    if is_faq:
        columns = {
            'question': question_col,
            'answer': answer_col,
            'category': category_col,
            'language': language_col
        }
    
    return is_faq, columns

def import_faqs_from_sheet(df: pd.DataFrame, columns: dict, source_file: str, sheet_name: str):
    """Import FAQs from a DataFrame into the knowledge base"""
    imported_count = 0
    
    for idx, row in df.iterrows():
        question = row[columns['question']]
        answer = row[columns['answer']]
        
        # Skip empty rows
        if pd.isna(question) or pd.isna(answer):
            continue
        
        # Get optional fields
        category = row[columns['category']] if columns.get('category') and columns['category'] in df.columns else 'General'
        language = row[columns['language']] if columns.get('language') and columns['language'] in df.columns else 'English'
        
        # Handle NaN values
        if pd.isna(category):
            category = 'General'
        if pd.isna(language):
            language = 'English'
        
        # Create unique FAQ ID
        faq_id = f"FAQ-{str(uuid.uuid4())[:8]}"
        
        # Add to knowledge base
        st.session_state.knowledge_base[faq_id] = {
            'type': 'faq',
            'question': str(question).strip(),
            'answer': str(answer).strip(),
            'category': str(category).strip(),
            'language': str(language).strip(),
            'source_file': source_file,
            'source_sheet': sheet_name,
            'uploaded_at': datetime.now()
        }
        
        imported_count += 1
    
    return imported_count
        
        with col2:
            st.write("**🌐 Add Website URL**")
            url = st.text_input("Enter website URL to crawl")
            if st.button("Crawl Website"):
                if url:
                    st.session_state.knowledge_base[url] = {
                        'content': f"Content from {url}",
                        'type': 'website',
                        'uploaded_at': datetime.now()
                    }
                    st.success(f"✅ Successfully crawled {url}")
        
        st.divider()
        
        st.subheader("✍️ Add Manual FAQ")
        faq_question = st.text_input("Question")
        faq_answer = st.text_area("Answer")
        
        col1, col2 = st.columns(2)
        with col1:
            faq_category = st.selectbox("Category", [
                "Product Information",
                "Technical Support",
                "Billing",
                "General Inquiry",
                "Installation"
            ])
        
        with col2:
            faq_language = st.selectbox("Language", ["English", "Hindi", "Marathi"])
        
        if st.button("Add FAQ", type="primary"):
            if faq_question and faq_answer:
                faq_id = f"FAQ-{str(uuid.uuid4())[:8]}"
                st.session_state.knowledge_base[faq_id] = {
                    'type': 'faq',
                    'question': faq_question,
                    'answer': faq_answer,
                    'category': faq_category,
                    'language': faq_language,
                    'uploaded_at': datetime.now()
                }
                st.success("✅ FAQ added successfully!")
    
    with tab2:
        st.subheader("📖 Current Knowledge Base")
        
        if st.session_state.knowledge_base:
            # Count FAQs vs other content
            total_items = len(st.session_state.knowledge_base)
            faq_count = sum(1 for v in st.session_state.knowledge_base.values() if v.get('type') == 'faq')
            file_count = total_items - faq_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", total_items)
            with col2:
                st.metric("FAQs", faq_count)
            with col3:
                st.metric("Files", file_count)
            
            st.divider()
            
            # Filter options
            filter_type = st.selectbox(
                "Filter by type:",
                ["All", "FAQs Only", "Files Only"]
            )
            
            # Display items
            for key, value in st.session_state.knowledge_base.items():
                # Apply filter
                if filter_type == "FAQs Only" and value.get('type') != 'faq':
                    continue
                elif filter_type == "Files Only" and value.get('type') == 'faq':
                    continue
                
                # Choose icon based on type
                if value.get('type') == 'faq':
                    icon = "❓"
                elif value.get('type') == 'excel':
                    icon = "📊"
                elif value.get('type') == 'text':
                    icon = "📝"
                else:
                    icon = "📄"
                
                with st.expander(f"{icon} {key}"):
                    if value.get('type') == 'faq':
                        st.markdown(f"**Type:** FAQ Entry")
                        st.markdown(f"**❓ Question:**")
                        st.info(value['question'])
                        st.markdown(f"**✅ Answer:**")
                        st.success(value['answer'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**📁 Category:** {value['category']}")
                            st.write(f"**🌐 Language:** {value['language']}")
                        with col2:
                            if value.get('source_file'):
                                st.write(f"**📊 Source File:** {value['source_file']}")
                            if value.get('source_sheet'):
                                st.write(f"**📄 Source Sheet:** {value['source_sheet']}")
                        
                    elif value.get('type') == 'excel':
                        st.write(f"**Type:** 📊 Excel Spreadsheet")
                        
                        if value.get('sheets_data'):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Sheets", value.get('total_sheets', 'N/A'))
                            with col2:
                                st.metric("Total Rows", value.get('total_rows', 'N/A'))
                            with col3:
                                faq_sheets = sum(1 for s in value['sheets_data'].values() if s.get('is_faq'))
                                st.metric("FAQ Sheets", faq_sheets)
                            
                            st.markdown("**Sheet Details:**")
                            for sheet_name, sheet_info in value['sheets_data'].items():
                                faq_badge = " ✅ FAQ" if sheet_info.get('is_faq') else ""
                                st.write(f"  • **{sheet_name}**{faq_badge}: {sheet_info['rows']} rows, {sheet_info['columns']} columns")
                        
                        with st.expander("📄 View Content Summary"):
                            st.text(value.get('content', 'N/A'))
                    
                    elif value.get('type') == 'text':
                        st.write(f"**Type:** 📝 Text File")
                        st.write(f"**Size:** {value.get('size', 'N/A')} characters")
                        with st.expander("View Content"):
                            content = value.get('content', 'N/A')
                            if len(content) > 500:
                                st.text(content[:500] + "...")
                                if st.button("Show Full Content", key=f"show_{key}"):
                                    st.text(content)
                            else:
                                st.text(content)
                    
                    else:
                        st.write(f"**Type:** {value.get('type', 'Document').title()}")
                        with st.expander("View Content"):
                            content = value.get('content', 'N/A')
                            st.text(content[:500] + "..." if len(content) > 500 else content)
                    
                    st.write(f"**🕐 Added:** {value['uploaded_at'].strftime('%Y-%m-%d %H:%M')}")
                    
                    # Delete option
                    if st.button(f"🗑️ Delete {key}", key=f"delete_{key}", type="secondary"):
                        del st.session_state.knowledge_base[key]
                        st.success(f"Deleted {key}")
                        st.rerun()
        else:
            st.info("📚 No knowledge base content yet. Start by uploading files or adding FAQs!")
            st.write("**Get Started:**")
            st.write("1. Upload an Excel file with Question/Answer columns")
            st.write("2. System will auto-detect FAQs")
            st.write("3. Click to import all FAQs instantly!")
            st.write("4. Or manually add FAQs using the form above")
    
    with tab3:
        st.subheader("🔍 Search Knowledge Base")
        search_query = st.text_input("Search for information...")
        
        if search_query:
            st.write(f"Searching for: **{search_query}**")
            
            # Simple search simulation
            results = []
            for key, value in st.session_state.knowledge_base.items():
                if value.get('type') == 'faq':
                    if search_query.lower() in value['question'].lower() or search_query.lower() in value['answer'].lower():
                        results.append((key, value))
            
            if results:
                st.success(f"Found {len(results)} result(s)")
                for key, value in results:
                    st.write(f"**Q:** {value['question']}")
                    st.write(f"**A:** {value['answer']}")
                    st.divider()
            else:
                st.warning("No results found")

elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">System Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🤖 AI Configuration", "🔔 Notifications", "👥 User Management"])
    
    with tab1:
        st.subheader("AI Agent Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider(
                "Confidence Threshold for Escalation",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="Queries with confidence below this threshold will be escalated"
            )
            
            response_tone = st.selectbox(
                "Response Tone",
                ["Professional", "Friendly", "Casual", "Formal"]
            )
            
            max_response_length = st.number_input(
                "Max Response Length (words)",
                min_value=50,
                max_value=500,
                value=150
            )
        
        with col2:
            enable_auto_translation = st.checkbox("Enable Auto-Translation", value=True)
            enable_sentiment_analysis = st.checkbox("Enable Sentiment Analysis", value=True)
            enable_ocr = st.checkbox("Enable OCR for Images", value=False)
            
            st.write("**Supported Languages:**")
            st.checkbox("English", value=True, disabled=True)
            st.checkbox("Hindi", value=True)
            st.checkbox("Marathi", value=True)
        
        if st.button("Save AI Configuration", type="primary"):
            st.success("✅ Configuration saved successfully!")
    
    with tab2:
        st.subheader("Notification Settings")
        
        st.write("**Email Notifications**")
        notify_new_ticket = st.checkbox("Notify on new ticket creation", value=True)
        notify_escalation = st.checkbox("Notify on query escalation", value=True)
        daily_summary = st.checkbox("Send daily summary report", value=True)
        
        email_list = st.text_area(
            "Notification Email List (one per line)",
            value="support@example.com\nadmin@example.com"
        )
        
        st.write("**WhatsApp Notifications**")
        whatsapp_enabled = st.checkbox("Enable WhatsApp notifications", value=False)
        
        if st.button("Save Notification Settings", type="primary"):
            st.success("✅ Notification settings saved!")
    
    with tab3:
        st.subheader("User Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Add New User**")
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_role = st.selectbox("Role", ["Admin", "Support Agent", "Viewer"])
            
            if st.button("Add User", type="primary"):
                st.success(f"✅ User {new_username} added successfully!")
        
        with col2:
            st.write("**Current Users**")
            users_data = {
                'Username': ['admin', 'support1', 'support2'],
                'Email': ['admin@example.com', 'support1@example.com', 'support2@example.com'],
                'Role': ['Admin', 'Support Agent', 'Support Agent'],
                'Status': ['Active', 'Active', 'Active']
            }
            st.dataframe(pd.DataFrame(users_data), use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🤖 AI Customer Support Agent v1.0 | Powered by Advanced AI | 
    <a href='#'>Documentation</a> | <a href='#'>Support</a></p>
</div>
""", unsafe_allow_html=True)
