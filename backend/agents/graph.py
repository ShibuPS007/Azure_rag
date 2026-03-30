from langgraph.graph import StateGraph, END
from .state import AgentState
from .agent import (
    router_agent,
    rag_agent,
    web_agent,
    evaluator_agent,
    hybrid_agent
)


    
def build_graph():

    builder = StateGraph(AgentState)


    builder.add_node("router", router_agent)
    builder.add_node("rag", rag_agent )
    builder.add_node("web", web_agent)
    builder.add_node("evaluator", evaluator_agent)
    builder.add_node("hybrid", hybrid_agent)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        lambda state: state.source,
        {
            "rag": "rag",
            "web": "web",
        }
    )

    builder.add_edge("rag", "evaluator")
    builder.add_edge("web", "evaluator")

    # def route_fallback(state):
    #     if state.source == "rag":
    #         return "web"
    #     else:
    #         return END

    builder.add_conditional_edges(
        "evaluator",
        lambda state: state.decision,
        {
            "accept": END,
            "combine": "hybrid",
            "fallback": "web"
        }
    )


    
    builder.add_edge("hybrid", END)

    return builder.compile()