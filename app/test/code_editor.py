# import asyncio
# from datetime import datetime
# from typing import List
#
#
# from app.container import container
# from app.llms.models import ChatLLM, StreamChatLLM
# from app.pipelines.pipeline import StreamPipeline
# from app.task_manager.models.task import Task
# from app.test.chat_editor_output import extract_all_code, extract_non_code_text, extract_file_paths, rewrite_file
#
#
# class CodeEditor(StreamPipeline):
#     def template(
#             self,
#             task: str,
#     ) -> str:
#         return f"""{task}
#
# Return the generated code by first writing which file needs to be changed (File:) and then the code.
# """
#
#
# async def create_tasks(
#         task: str
# ):
#     """
#     Creates and stores tasks based on a text input and context.
#
#     :param text: Input text used for generating tasks. The function processes
#         this text to identify and create actionable tasks.
#     :type text: str
#     :return: A list of tasks created and stored in the database as per the input
#         text and context.
#     :rtype: List[Task]
#     """
#     mdb = container.mdb()
#     chat_service = container.chat_service()
#     chat_model = await chat_service.get_model(model_name="claude-3-7-sonnet-20250219", class_type=StreamChatLLM)
#     retriever_pipeline = CodeEditor(chat_model)
#
#     response = ""
#
#     async for elem in retriever_pipeline.execute(
#         task=task,
#     ):
#         response+=elem
#
#     codes = extract_all_code(response)
#     non_code = extract_non_code_text(response)
#     file_paths = extract_file_paths(non_code)
#
#     for file_path, code in zip(file_paths, codes):
#         rewrite_file(file_path, code)
#
#
# asyncio.run(create_tasks("""Create a panel for displaying tasks in a list/table and create a panel for displaying Goals.
#
# class Task(MongoEntry):
#     title: Optional[str] = None
#     subtasks: Optional[list[str]] = None
#     description: Optional[str] = None
#     finished: bool = False
#     collaborators: Optional[list[str]] = []
#     due_date: Optional[datetime] = None
#     email: Optional[EmailStr] = None
#
#
# class Goal(MongoEntry):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     due_date: Optional[datetime] = None
#
# write html and css. Make the panels look good
# write the html in the file /home/nnikolovskii/WebstormProjects/dina-ui/src/app/global-features/components/tasks-goals/tasks-goals.component.html
# write the css in the file /home/nnikolovskii/WebstormProjects/dina-ui/src/app/global-features/components/tasks-goals/tasks-goals.component.css
# """))
