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

# Added a comment
#LLM = 'gpt-4o'
# Initialize Ollama LLM
#llm=LLM(model="ollama/llama3", base_url="http://localhost:11434")
#llm=LLM(model="ollama/qwen2.5", base_url="http://localhost:11434")
#llm=LLM(model="ollama/mistral-nemo", base_url="http://localhost:11434")
llm=LLM(model="ollama/falcon", base_url="http://localhost:11434")


#llm='gpt-4o'
#llm ='gpt-3.5-turbo'
#llm="o1-preview"
#llm ="o1-mini"




# llm = LLM(
#     model="gpt-4",
#     temperature=0.7,
#     base_url="https://api.openai.com/v1",
#     api_key="your-api-key-here"
# )

@CrewBase
class CollegeEssayVersion2Crew():
	"""CollegeEssayVersion2 crew"""
	@agent
	def essay_generator(self) -> Agent:
		return Agent(
			config=self.agents_config['essay_generator'],
			llm=llm,
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
		return Agent(
			config=self.agents_config['critic_reviewer'],
			llm=llm,
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
			#agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
			#process=Process.sequential,
			manager_agent=self.critic_reviewer(),
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
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