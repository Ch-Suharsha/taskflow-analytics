import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import SerperDevTool

# Initialize the tool
search_tool = SerperDevTool()

# Check for API keys
if not os.environ.get("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")
if not os.environ.get("SERPER_API_KEY"):
    print("WARNING: SERPER_API_KEY not found in environment variables.")

# Initialize Gemini LLM
# You can use 'gemini-pro' or other available models.
gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", verbose=True, temperature=0.5)

# Define the Agents
class ProductAnalysts:
    def market_researcher(self):
        return Agent(
            role='Market Researcher',
            goal='Gather comprehensive data about the product and its market.',
            backstory="""You are an expert market researcher with a knack for finding 
            hidden gems of information. You are detailed-oriented and leave no stone unturned.""",
            tools=[search_tool],
            verbose=True,
            memory=True,
            llm=gemini_llm
        )

    def data_analyst(self):
        return Agent(
            role='Data Analyst',
            goal='Analyze gathered data to identify trends and insights.',
            backstory="""You are a seasoned data analyst. You can look at raw data 
            and see the story behind the numbers. You provide clear, data-driven insights.""",
            tools=[], # Can add specific data analysis tools if needed
            verbose=True,
            memory=True,
            llm=gemini_llm
        )

    def content_writer(self):
        return Agent(
            role='Content Writer',
            goal='Synthesize all findings into a comprehensive report.',
            backstory="""You are a skilled content writer. You take complex information 
            and turn it into engaging, easy-to-read reports for stakeholders.""",
            tools=[],
            verbose=True,
            memory=True,
            llm=gemini_llm
        )
