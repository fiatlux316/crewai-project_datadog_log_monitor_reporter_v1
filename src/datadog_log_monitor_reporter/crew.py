import os

import json
from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.custom_tool import DatadogLogsSearchTool, DatadogAPMTracesSearchTool


from pydantic import BaseModel
from jambo import SchemaConverter

from .devx_llm_wrapper import llm

@CrewBase
class DatadogLogMonitorReporterCrew:
    """DatadogLogMonitorReporter crew"""

    
    @agent
    def datadog_log_retrieval_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["datadog_log_retrieval_specialist"],
            #tools=[DatadogLogsSearchTool()],
            tools=[DatadogAPMTracesSearchTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            # llm=LLM(
            #     model="bedrock/claude-sonnet-4-5-20250929-v1:0",    
            # ),
            llm=llm,
            response_format=self._load_response_format("datadog_log_retrieval_specialist"),
        )
        
    
    @agent
    def application_error_analysis_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["application_error_analysis_expert"],
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            # llm=LLM(
            #     model="bedrock/claude-sonnet-4-5-20250929-v1:0",    
            # ),
            llm=llm
        )
        
    
    @agent
    def technical_report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_report_writer"],
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            # llm=LLM(
            #     model="bedrock/claude-sonnet-4-5-20250929-v1:0",
            # ),
            llm=llm,    
        )
        
    
    @agent
    def notification_dispatcher(self) -> Agent:
        return Agent(
            config=self.agents_config["notification_dispatcher"],
            tools=[],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            apps=[
                    "microsoft_outlook/send_email",
                    ],
            max_execution_time=None,
            # llm=LLM(
            #     model="bedrock/claude-sonnet-4-5-20250929-v1:0",    
            # ),
            llm=llm,
        )
        
    

    
    @task
    def fetch_datadog_logs(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_datadog_logs"],
            markdown=False,
        )
    
    @task
    def analyze_application_logs(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_application_logs"],
            markdown=False,    
        )
    
    @task
    def generate_log_report(self) -> Task:
        return Task(
            config=self.tasks_config["generate_log_report"],
            markdown=False,
        )
    
    @task
    def send_report_via_email(self) -> Task:
        return Task(
            config=self.tasks_config["send_report_via_email"],
            markdown=False,    
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the DatadogLogMonitorReporter crew"""

        # Custom manager agent for hierarchical process
        manager_agent = Agent(
            role="Crew Manager",
            goal="Coordinate the team to achieve the objective efficiently",
            backstory="An experienced manager skilled in delegation and coordination",
            # llm=LLM(model="bedrock/claude-sonnet-4-5-20250929-v1:0"),
            llm=llm,
            allow_delegation=True,
        )

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,


            manager_agent=manager_agent,


            #chat_llm=LLM(model="openai/gpt-4o-mini"),
            chat_llm=llm,
        )


    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)

