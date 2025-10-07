# Agent Design

The agents will rely on multiple models and tools to help KubeCon North America attendees plan their day and navigate the conference.

Tools needed:

- MCP servers for the following functions:

  - Parse the conference schedule and format for indexing into a vector database
  - Get the current time so that agents can reason about the schedule
  - Retrieve session details from document databases
  - Retrieve session details from KubeCon schedule website to validate information in the vector database

Workflow:

1. Once a day an agent will pull down the conference schedule (https://kccncna2025.sched.com/all.ics) and parse it from ics format into a structured JSON format. The agent will then prepare the data for indexing into a KAITO RAGEngine compatible format and send it to the KAITO RAGEngine indexing endpoint.
2. When a user interacts with the chat interface, it makes a call to the main agent which will act as the orchestrator. The main agent will determine the user's intent and decide which specialized agent to call (e.g., schedule agent, session details agent).
3. The specialized agent will call the appropriate MCP server to get the current time, query the RAGEngine inference endpoint with the user's question and the current time, and return the response to the main agent.
4. The main agent will then parse the response and verify the sessions returned by querying the KubeCon schedule website to ensure the information is accurate and up-to-date.
5. If accurate, the main agent can call the database agent to get additional details about the sessions if needed, and then return the final response to the user.
