from crewai import Task

class ProductTasks:
    def product_analysis_task(self, agent, product_name):
        return Task(
            description=f"""Conduct a comprehensive market research and analysis for the product: {product_name}.
            Identify key competitors, market trends, customer sentiment, and potential opportunities.
            Your final answer must be a detailed report summary.""",
            agent=agent,
            expected_output="A comprehensive market research report summary."
        )

    def data_analysis_task(self, agent, context):
        return Task(
            description=f"""Analyze the data collected from the market research. 
            Identify patterns, trends, and key insights. 
            Highlight any significant findings that would be valuable for the product strategy.
            The context for analysis is: {context}""",
            agent=agent,
            expected_output="A detailed analysis of the market research data."
        )

    def report_writing_task(self, agent, context):
        return Task(
            description=f"""Synthesize all findings into a high-quality product analysis report.
            The report should be well-structured, easy to read, and actionable.
            Include an executive summary, key findings, and recommendations.
            The context for the report is: {context}""",
            agent=agent,
            expected_output="A final product analysis report in markdown format."
        )
