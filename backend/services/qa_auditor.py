import json
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser

# --- 1. Define the LangGraph State ---
# This is the memory object that gets passed around the loop
class AgentState(TypedDict):
    ad_context: dict
    variants: dict  # The output from the Copywriter
    feedback: str
    audit_passed: bool
    attempts: int

# --- 2. Define the Output Schema for the Evaluator ---
class AuditResult(BaseModel):
    passed: bool = Field(description="True if no hallucinations exist, False if there are fake claims or prices.")
    feedback: str = Field(description="If failed, specify exactly what was hallucinated so it can be fixed.")

# --- 3. The Node Functions ---

async def evaluate_variants(state: AgentState) -> AgentState:
    """Node 1: Checks the generated copy against the original ad for hallucinations."""
    print(f"[Auditor] Running audit attempt {state['attempts']}...")
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
    structured_llm = llm.with_structured_output(AuditResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a strict QA Compliance Officer. Your job is to prevent hallucinations.
        Compare the generated copy variants against the original Ad Context.
        
        CRITICAL RULES:
        1. If the copy mentions a price, discount, or specific metric that is NOT in the Ad Context, FAIL it.
        2. If it invents a fake feature, FAIL it.
        Otherwise, PASS it."""),
        ("human", "Ad Context: {ad_context}\n\nGenerated Variants: {variants}")
    ])
    
    chain = prompt | structured_llm
    result = await chain.ainvoke({
        "ad_context": json.dumps(state["ad_context"]),
        "variants": json.dumps(state["variants"])
    })
    
    return {
        "audit_passed": result.passed,
        "feedback": result.feedback,
        "attempts": state["attempts"] + 1
    }

async def fix_hallucinations(state: AgentState) -> AgentState:
    """Node 2: If the audit failed, this node forces the LLM to fix the specific errors."""
    print(f"[Auditor] Fixing hallucinations: {state['feedback']}")
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an editor. Fix the JSON copy variants based on the auditor's feedback. Return ONLY valid JSON matching the original structure."),
        ("human", "Original Variants: {variants}\n\nAuditor Feedback: {feedback}\n\nFix the errors and return the corrected JSON variants.")
    ])
    
    # We add StrOutputParser() to guarantee the result is a plain string, not a list
    chain = prompt | llm | StrOutputParser()
    
    result = await chain.ainvoke({
        "variants": json.dumps(state["variants"]),
        "feedback": state["feedback"]
    })
    
    # Because of the parser, 'result' is a string now, so we can clean it directly
    cleaned_json_str = result.replace("```json", "").replace("```", "").strip()
    corrected_variants = json.loads(cleaned_json_str)
    
    return {"variants": corrected_variants}

# --- 4. The Edge Logic ---
def route_audit(state: AgentState) -> str:
    """Determines whether to end the graph or route back for fixes."""
    if state["audit_passed"] or state["attempts"] >= 2:
        return END  # Exit the loop if it passes or if we tried too many times (prevents infinite loops)
    return "fix_hallucinations"

# --- 5. Build and Compile the Graph ---
def build_auditor_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("evaluate_variants", evaluate_variants)
    workflow.add_node("fix_hallucinations", fix_hallucinations)
    
    # Set entry point
    workflow.set_entry_point("evaluate_variants")
    
    # Add edges
    workflow.add_conditional_edges("evaluate_variants", route_audit)
    workflow.add_edge("fix_hallucinations", "evaluate_variants") # Loop back to audit after fixing
    
    return workflow.compile()

# --- The Main Callable Function ---
async def run_safety_audit(ad_context: dict, variants: dict) -> dict:
    """Entry point for main.py to call the LangGraph auditor."""
    app = build_auditor_graph()
    
    initial_state = {
        "ad_context": ad_context,
        "variants": variants,
        "feedback": "",
        "audit_passed": False,
        "attempts": 0
    }
    
    # Run the graph asynchronously
    final_state = await app.ainvoke(initial_state)
    return final_state["variants"]