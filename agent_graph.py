from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
import os
from dotenv import load_dotenv

from tool import get_weather, web_search
from rag import query_vector_db
from database import engine

load_dotenv()

# 1. Setup LLM
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

# 2. Setup SQL Agent
try:
    db = SQLDatabase(engine)
    sql_agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=False)
except Exception as e:
    print(f"Warning: SQL Agent setup failed: {e}")
    sql_agent_executor = None

# 3. Define State
class AgentState(TypedDict):
    query: str
    context: str
    response: str

# 4. Define Nodes (The Agents)

def router_node(state: AgentState):
    """Decides which worker to call based on the user query."""
    prompt = f"""Analyze the user query: "{state['query']}"
Classify it into one of these categories:
1. WEATHER: Queries about temperature, rain, forecast, weather
2. DOC_QA: Queries about policies, resume, document content, information
3. MEETING_SCHEDULE: Requests to schedule meetings based on conditions
4. DB_QUERY: Questions about existing meetings, events, database

Return ONLY the category name (WEATHER, DOC_QA, MEETING_SCHEDULE, or DB_QUERY)."""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except Exception as e:
        print(f"Router error: {e}")
        response = "DB_QUERY"
    
    return {"context": response, "response": ""}

def weather_agent(state: AgentState):
    """Handles weather-related queries."""
    try:
        city_prompt = f"Extract the city name from this query: {state['query']}. Reply with only the city name."
        city_extraction = llm.invoke([HumanMessage(content=city_prompt)]).content.strip()
        weather = get_weather.invoke(city_extraction)
        return {"response": weather}
    except Exception as e:
        return {"response": f"Weather service unavailable: {str(e)}"}

def doc_qa_agent(state: AgentState):
    """Handles document Q&A and web search."""
    try:
        doc_result = query_vector_db(state['query'])
        
        if doc_result:
            check_prompt = f"Context: {doc_result}\n\nQuestion: {state['query']}\n\nDoes the context answer the question? Reply only Yes or No."
            check = llm.invoke([HumanMessage(content=check_prompt)]).content.lower()
            if "yes" in check:
                ans_prompt = f"Answer this question using the provided context:\n\nContext: {doc_result}\n\nQuestion: {state['query']}"
                ans = llm.invoke([HumanMessage(content=ans_prompt)])
                return {"response": ans.content}
        
        web_res = web_search.invoke(state['query'])
        return {"response": web_res}
    except Exception as e:
        return {"response": f"Document QA failed: {str(e)}"}

def scheduler_agent(state: AgentState):
    """Handles meeting scheduling logic."""
    try:
        # Extract city from query
        city_prompt = f"Extract the city name from this query: {state['query']}. Reply with only the city name."
        city = llm.invoke([HumanMessage(content=city_prompt)]).content.strip()
        
        weather_res = get_weather.invoke(city)
        
        decision_prompt = f"Weather is: {weather_res}. Is this good weather for an outdoor meeting? Reply only Yes or No."
        decision = llm.invoke([HumanMessage(content=decision_prompt)]).content.lower()
        
        if "yes" in decision:
            return {"response": f"Good weather ({weather_res}). Meeting can be scheduled!"}
        else:
            return {"response": f"Bad weather ({weather_res}). Meeting not recommended for outdoors."}
    except Exception as e:
        return {"response": f"Scheduling error: {str(e)}"}

def db_query_agent(state: AgentState):
    """Handles database queries with optimized formatting and error handling."""
    try:
        if not sql_agent_executor:
            return {"response": "Database service unavailable. Please try another query type."}
        
        query = state['query'].strip()
        
        # Validate query
        if not query or len(query) < 3:
            return {"response": "Please provide a valid query about meetings."}
        
        # Execute query with timeout
        try:
            res = sql_agent_executor.invoke(
                {"input": query},
                config={"timeout": 10}
            )
        except TimeoutError:
            return {"response": "Database query timed out. Please try a simpler query."}
        
        output = res.get('output', '')
        
        # Format response
        if not output or output.lower() in ['none', 'no results', '']:
            return {"response": "No meetings found matching your query."}
        
        # Clean and format output
        formatted_response = output.strip()
        
        # Add helpful context based on query type
        if any(word in query.lower() for word in ['list', 'show', 'all', 'get']):
            formatted_response = f"Meetings found:\n{formatted_response}"
        elif any(word in query.lower() for word in ['count', 'how many']):
            formatted_response = f"Meeting count:\n{formatted_response}"
        elif any(word in query.lower() for word in ['search', 'find']):
            formatted_response = f"Search results:\n{formatted_response}"
        
        return {"response": formatted_response}
        
    except ValueError as e:
        return {"response": f"Invalid query format: {str(e)}. Please rephrase your question."}
    except Exception as e:
        error_msg = str(e).lower()
        if 'syntax' in error_msg:
            return {"response": "Query syntax error. Try asking: 'List all meetings' or 'Show meetings tomorrow'"}
        elif 'connection' in error_msg:
            return {"response": "Database connection failed. Please try again later."}
        else:
            return {"response": f"Query processing error. Please rephrase: {str(e)[:100]}"}

# 5. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("weather_worker", weather_agent)
workflow.add_node("doc_worker", doc_qa_agent)
workflow.add_node("scheduler_worker", scheduler_agent)
workflow.add_node("db_worker", db_query_agent)

# Conditional Edges
def route_logic(state):
    category = state.get('context', 'DB_QUERY').upper()
    if "WEATHER" in category:
        return "weather_worker"
    elif "DOC_QA" in category or "DOC" in category:
        return "doc_worker"
    elif "MEETING_SCHEDULE" in category or "MEETING" in category:
        return "scheduler_worker"
    else:
        return "db_worker"

workflow.set_entry_point("router")
workflow.add_conditional_edges("router", route_logic)
workflow.add_edge("weather_worker", END)
workflow.add_edge("doc_worker", END)
workflow.add_edge("scheduler_worker", END)
workflow.add_edge("db_worker", END)

app_graph = workflow.compile()