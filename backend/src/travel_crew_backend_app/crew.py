# src/travel_crew_backend/crew.py

import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

@CrewBase
class TravelCrew():
	"""TravelCrew para planificar viajes personalizados."""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def __init__(self) -> None:
		load_dotenv()
		#self.search_tool = DuckDuckGoSearchRun()
		self.llm = ChatOpenAI(model=os.getenv("MODEL"))

	@agent
	def agente_experto_cultural(self) -> Agent:
		return Agent(
			config=self.agents_config['agente_experto_cultural'],
			tools=[],
			verbose=True
		)

	@agent
	def agente_gourmet_local(self) -> Agent:
		return Agent(
			config=self.agents_config['agente_gourmet_local'],
			tools=[],
			verbose=True
		)
	
	@agent
	def agente_logistica(self) -> Agent:
		return Agent(
			config=self.agents_config['agente_logistica'],
			tools=[],
			verbose=True
		)

	@agent
	def agente_planificador_itinerario(self) -> Agent:
		return Agent(
			config=self.agents_config['agente_planificador_itinerario'],
			verbose=True
		)
	
	@agent
	def agente_redactor_viajes(self) -> Agent:
		return Agent(
			config=self.agents_config['agente_redactor_viajes'],
			verbose=True
		)



	@task
	def task_cultura(self) -> Task:
		return Task(
			config=self.tasks_config['task_cultura'],
		)

	@task
	def task_gastronomia(self) -> Task:
		return Task(
			config=self.tasks_config['task_gastronomia'],
		)
	
	@task
	def task_logistica(self) -> Task:
		return Task(
			config=self.tasks_config['task_logistica'],
		)
	
	@task
	def task_itinerario(self) -> Task:
		return Task(
			config=self.tasks_config['task_itinerario'],
			context=[self.task_cultura(), self.task_gastronomia(), self.task_logistica()]
		)
	
	@task
	def task_redaccion_final(self) -> Task:
		return Task(
			config=self.tasks_config['task_redaccion_final'],
			context=[self.task_itinerario()],
			output_file='itinerary.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Crea y configura el TravelCrew."""

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)