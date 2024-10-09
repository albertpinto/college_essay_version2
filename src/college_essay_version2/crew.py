from crewai import Agent, Crew, Process, Task, LLM 
from crewai.project import CrewBase, agent, crew, task


# Uncomment the following line to use an example of a custom tool
# from college_essay_version2.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
from crewai_tools import FileReadTool
import os
# Example usage in a LangChain agent
from langchain.agents import initialize_agent, Tool
from college_essay_version2.tools.txt_PDF_tool import PDFConversionTool

# Uncomment this to use openAI models.
#OpenAI models
#llm='gpt-4o','gpt-3.5-turbo',"o1-preview"
llm ="o1-mini"

# Initialize Ollama LLM
# Use this for non openAI models

#llm=LLM(model="ollama/llama3.1", base_url="http://localhost:11434")

@CrewBase
class CollegeEssayVersion2Crew():
	"""This is the optimal crew for generating a college essay version 2 and can use
	any openAI and other models to generate the essay"""

	def __init__(self, model):
		self.model = model
		self.llm = self._set_llm()

	def _set_llm(self):
		if self.model in ['gpt-4o', 'gpt-3.5-turbo', 'claude-2.5', 'o1-preview','o1-mini']:
			return self.model
		else:
			return LLM(model=self.model, base_url="http://localhost:11434")
	
	@agent
	def essay_generator(self) -> Agent:
		#print("The LLm used:" + self.llm)
		return Agent(
			config=self.agents_config['essay_generator'],
			llm=self.llm,
			verbose=True
		)

	@task
	def essay_task(self) -> Task:
		"""Answer college questions using activity information"""
		return Task(
			config=self.tasks_config['essay_task'],
			output_file="essay.md",
			allow_delegation=True,
			verbose=True
		)	
	@agent
	def critic_reviewer(self) -> Agent:
		#print("The LLm used:" + self.llm)
		return Agent(
			config=self.agents_config['critic_reviewer'],
			llm=self.llm,
			allow_delegation=True,
			verbose=True
		)
	@task
	def critic_task(self) -> Task:
		"""You will critique the essay and make sure it's original and not from a bot"""
		return Task(
			config=self.tasks_config['critic_task'],
			output_file="critic.md",
			verbose=True
		)
	@crew
	def crew(self) -> Crew:
		"""Creates the CollegeEssayVersion2 crew"""
		return Crew(
			agents=[self.essay_generator()], # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.hierarchical, 
			manager_agent=self.critic_reviewer(),
			verbose=True,
		)

	def get_file_content(self):
		file_reader_tool = FileReadTool(file_path="/home/albert/Downloads/rika-pinto-resume.md")
		return file_reader_tool.run()
	

	def convert_to_pdf(self,input_file, output_file):
		pdf_tool = PDFConversionTool(input_file_path=input_file, output_file_path=output_file)
		#return pdf_tool.run()
		return pdf_tool._run()

	# # You can use it like this:
	# result = convert_to_pdf("/path/to/input.txt", "/path/to/output.pdf")
	# print(result)