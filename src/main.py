import os
from crewai import Crew, Process
from agents import ProductAnalysts
from tasks import ProductTasks

def main():
    print("Welcome to the Product Data Analyst Crew!")
    print("---------------------------------------")
    product_name = input("Enter the product or market you want to analyze: ")

    if not product_name:
        print("Product name is required to start the analysis.")
        return

    agents = ProductAnalysts()
    tasks = ProductTasks()

    # Create Agents
    researcher = agents.market_researcher()
    analyst = agents.data_analyst()
    writer = agents.content_writer()

    # Create Tasks
    # Note: Sequential process, so tasks are executed in order.
    # We pass the output of previous tasks as context implicitly or explicitly if needed.
    
    task1 = tasks.product_analysis_task(researcher, product_name)
    task2 = tasks.data_analysis_task(analyst, [task1]) # context from task1
    task3 = tasks.report_writing_task(writer, [task2]) # context from task2

    # Instantiate Crew
    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[task1, task2, task3],
        verbose=2, # You can set validation_level to 1, 2, etc. (check crewai docs, verbose=True is standard)
        process=Process.sequential
    )

    # Begin the task execution
    result = crew.kickoff()

    print("######################")
    print("## Final Result ##")
    print("######################")
    print(result)

if __name__ == "__main__":
    main()
