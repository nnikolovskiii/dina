# output = """I'll create a beautiful tasks and goals panel for you. Let me design the HTML and CSS files.
#
# ### File: home/nnikolovskii/public/index.html
# ```html
# <!DOCTYPE html>
# <html lang="en">
# <head>
#   <meta charset="UTF-8">
#   <meta name="viewport" content="width=device-width, initial-scale=1.0">
#   <title>Task & Goal Management</title>
#   <link rel="stylesheet" href="index.css">
#   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
# </head>
# <body>
#   <div class="container">
#     <header>
#       <h1>My Dashboard</h1>
#       <p class="subtitle">Manage your tasks and goals efficiently</p>
#     </header>
#
#     <main>
#       <section class="panel tasks-panel">
#         <div class="panel-header">
#           <h2><i class="fas fa-tasks"></i> Tasks</h2>
#           <button class="add-btn"><i class="fas fa-plus"></i> New Task</button>
#         </div>
#
#         <div class="panel-content">
#           <table class="task-table">
#             <thead>
#               <tr>
#                 <th style="width: 5%"><input type="checkbox" class="select-all"></th>
#                 <th style="width: 30%">Title</th>
#                 <th style="width: 30%">Description</th>
#                 <th style="width: 15%">Due Date</th>
#                 <th style="width: 10%">Collaborators</th>
#                 <th style="width: 10%">Actions</th>
#               </tr>
#             </thead>
#             <tbody>
#               <tr>
#                 <td><input type="checkbox"></td>
#                 <td>Complete Project Presentation</td>
#                 <td>Finalize slides and rehearse timing</td>
#                 <td>Jun 15, 2023</td>
#                 <td>
#                   <div class="collaborator-avatars">
#                     <span class="avatar" title="John Doe">JD</span>
#                     <span class="avatar" title="Jane Smith">JS</span>
#                   </div>
#                 </td>
#                 <td>
#                   <div class="action-buttons">
#                     <button class="icon-btn edit-btn"><i class="fas fa-edit"></i></button>
#                     <button class="icon-btn delete-btn"><i class="fas fa-trash"></i></button>
#                   </div>
#                 </td>
#               </tr>
#               <tr class="completed">
#                 <td><input type="checkbox" checked></td>
#                 <td>Research market trends</td>
#                 <td>Analyze competitor strategies and market growth</td>
#                 <td>Jun 10, 2023</td>
#                 <td>
#                   <div class="collaborator-avatars">
#                     <span class="avatar" title="Alex Johnson">AJ</span>
#                   </div>
#                 </td>
#                 <td>
#                   <div class="action-buttons">
#                     <button class="icon-btn edit-btn"><i class="fas fa-edit"></i></button>
#                     <button class="icon-btn delete-btn"><i class="fas fa-trash"></i></button>
#                   </div>
#                 </td>
#               </tr>
#               <tr>
#                 <td><input type="checkbox"></td>
#                 <td>Client meeting preparation</td>
#                 <td>Prepare agenda and supporting documents</td>
#                 <td>Jun 20, 2023</td>
#                 <td>
#                   <div class="collaborator-avatars">
#                     <span class="avatar" title="Sarah Parker">SP</span>
#                     <span class="avatar" title="Tom Wilson">TW</span>
#                     <span class="avatar" title="More">+2</span>
#                   </div>
#                 </td>
#                 <td>
#                   <div class="action-buttons">
#                     <button class="icon-btn edit-btn"><i class="fas fa-edit"></i></button>
#                     <button class="icon-btn delete-btn"><i class="fas fa-trash"></i></button>
#                   </div>
#                 </td>
#               </tr>
#             </tbody>
#           </table>
#         </div>
#       </section>
#
#       <section class="panel goals-panel">
#         <div class="panel-header">
#           <h2><i class="fas fa-bullseye"></i> Goals</h2>
#           <button class="add-btn"><i class="fas fa-plus"></i> New Goal</button>
#         </div>
#
#         <div class="panel-content">
#           <div class="goals-container">
#             <div class="goal-card">
#               <div class="goal-header">
#                 <h3>Increase customer satisfaction</h3>
#                 <span class="due-date">Due: Jul 31, 2023</span>
#               </div>
#               <p class="goal-description">Improve customer satisfaction scores by 15% through enhanced service delivery and response time optimization.</p>
#               <div class="goal-footer">
#                 <div class="progress-container">
#                   <div class="progress-bar" style="width: 65%"></div>
#                 </div>
#                 <span class="progress-text">65% complete</span>
#                 <div class="goal-actions">
#                   <button class="icon-btn edit-btn"><i class="fas fa-edit"></i></button>
#                   <button class="icon-btn delete-btn"><i class="fas fa-trash"></i></button>
#                 </div>
#               </div>
#             </div>
#
#             <div class="goal-card">
#               <div class="goal-header">
#                 <h3>Launch new product line</h3>
#                 <span class="due-date">Due: Sep 15, 2023</span>
#               </div>
#               <p class="goal-description">Complete development and launch marketing campaign for the new eco-friendly product line.</p>
#               <div class="goal-footer">
#                 <div class="progress-container">
#                   <div class="progress-bar" style="width: 30%"></div>
#                 </div>
#                 <span class="progress-text">30% complete</span>
#                 <div class="goal-actions">
#                   <button class="icon-btn edit-btn"><i class="fas fa-edit"></i></button>
#                   <button class="icon-btn delete-btn"><i class="fas fa-trash"></i></button>
#                 </div>
#               </div>
#             </div>
#
#             <div class="goal-card">
#               <div class="goal-header">
#                 <h3>Expand to new markets</h3>
#                 <span class="due-date">Due: Dec 1, 2023</span>
#               </div>
#               <p class="goal-description">Research and develop strategy for expansion into three new regional markets.</p>
#               <div class="goal-footer">
#                 <div class="progress-container">
#                   <div class="progress-bar" style="width: 10%"></div>
#                 </div>
#                 <span class="progress-text">10% complete</span>
#                 <div class="goal-actions">
#                   <button class="icon-btn edit-btn"><i class="fas fa-edit"></i></button>
#                   <button class="icon-btn delete-btn"><i class="fas fa-trash"></i></button>
#                 </div>
#               </div>
#             </div>
#           </div>
#         </div>
#       </section>
#     </main>
#   </div>
# </body>
# </html>
# ```
#
# ### File: home/nnikolovskii/public/index.css
# ```css
# /* Root variables for consistent design */
# :root {
#   --primary-color: #4a6cf7;
#   --primary-hover: #3a5de6;
#   --secondary-color: #6c757d;
#   --success-color: #28a745;
#   --danger-color: #dc3545;
#   --warning-color: #ffc107;
#   --light-color: #f8f9fa;
#   --dark-color: #343a40;
#   --body-bg: #f5f7fb;
#   --card-bg: #ffffff;
#   --text-primary: #333;
#   --text-secondary: #6c757d;
#   --border-color: #e9ecef;
#   --shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08);
#   --border-radius: 8px;
#   --transition: all 0.3s ease;
# }
#
# /* Base styles */
# * {
#   margin: 0;
#   padding: 0;
#   box-sizing: border-box;
# }
#
# body {
#   font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#   background-color: var(--body-bg);
#   color: var(--text-primary);
#   line-height: 1.6;
# }
#
# .container {
#   max-width: 1200px;
#   margin: 0 auto;
#   padding: 2rem;
# }
#
# /* Header */
# header {
#   margin-bottom: 2rem;
#   text-align: center;
# }
#
# h1 {
#   font-size: 2.5rem;
#   color: var(--primary-color);
#   margin-bottom: 0.5rem;
# }
#
# .subtitle {
#   color: var(--text-secondary);
#   font-size: 1.1rem;
# }
#
# /* Panel styling */
# .panel {
#   background: var(--card-bg);
#   border-radius: var(--border-radius);
#   box-shadow: var(--shadow);
#   margin-bottom: 2rem;
#   overflow: hidden;
# }
#
# .panel-header {
#   display: flex;
#   justify-content: space-between;
#   align-items: center;
#   padding: 1.5rem;
#   border-bottom: 1px solid var(--border-color);
# }
#
# .panel-header h2 {
#   font-size: 1.5rem;
#   color: var(--dark-color);
#   display: flex;
#   align-items: center;
#   gap: 0.5rem;
# }
#
# .panel-header h2 i {
#   color: var(--primary-color);
# }
#
# .panel-content {
#   padding: 1.5rem;
# }
#
# /* Button styling */
# .add-btn {
#   background-color: var(--primary-color);
#   color: white;
#   border: none;
#   padding: 0.5rem 1rem;
#   border-radius: 4px;
#   cursor: pointer;
#   display: flex;
#   align-items: center;
#   gap: 0.5rem;
#   transition: var(--transition);
# }
#
# .add-btn:hover {
#   background-color: var(--primary-hover);
# }
#
# .icon-btn {
#   background: none;
#   border: none;
#   font-size: 1rem;
#   cursor: pointer;
#   padding: 0.25rem;
#   color: var(--text-secondary);
#   transition: var(--transition);
# }
#
# .edit-btn:hover {
#   color: var(--primary-color);
# }
#
# .delete-btn:hover {
#   color: var(--danger-color);
# }
#
# /* Task table styling */
# .task-table {
#   width: 100%;
#   border-collapse: collapse;
# }
#
# .task-table th {
#   text-align: left;
#   padding: 0.75rem;
#   background-color: var(--light-color);
#   color: var(--dark-color);
#   font-weight: 600;
#   border-bottom: 2px solid var(--border-color);
# }
#
# .task-table td {
#   padding: 0.75rem;
#   border-bottom: 1px solid var(--border-color);
#   vertical-align: middle;
# }
#
# .task-table tbody tr {
#   transition: var(--transition);
# }
#
# .task-table tbody tr:hover {
#   background-color: rgba(74, 108, 247, 0.05);
# }
#
# .task-table .completed {
#   background-color: rgba(40, 167, 69, 0.1);
# }
#
# .task-table .completed td {
#   text-decoration: line-through;
#   color: var(--text-secondary);
# }
#
# /* Collaborator avatars */
# .collaborator-avatars {
#   display: flex;
#   flex-wrap: nowrap;
# }
#
# .avatar {
#   display: inline-flex;
#   align-items: center;
#   justify-content: center;
#   width: 28px;
#   height: 28px;
#   background-color: var(--primary-color);
#   color: white;
#   font-size: 0.75rem;
#   font-weight: bold;
#   border-radius: 50%;
#   margin-right: -8px;
#   border: 2px solid white;
# }
#
# .avatar:last-child {
#   margin-right: 0;
# }
#
# /* Action buttons */
# .action-buttons {
#   display: flex;
#   gap: 0.5rem;
#   justify-content: center;
# }
#
# /* Goals styling */
# .goals-container {
#   display: grid;
#   grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
#   gap: 1.5rem;
# }
#
# .goal-card {
#   background-color: var(--card-bg);
#   border-radius: var(--border-radius);
#   border: 1px solid var(--border-color);
#   padding: 1.5rem;
#   transition: var(--transition);
#   display: flex;
#   flex-direction: column;
# }
#
# .goal-card:hover {
#   box-shadow: var(--shadow);
#   transform: translateY(-3px);
# }
#
# .goal-header {
#   display: flex;
#   justify-content: space-between;
#   align-items: flex-start;
#   margin-bottom: 1rem;
# }
#
# .goal-header h3 {
#   color: var(--dark-color);
#   font-size: 1.25rem;
#   margin-right: 1rem;
# }
#
# .due-date {
#   font-size: 0.85rem;
#   color: var(--text-secondary);
#   white-space: nowrap;
# }
#
# .goal-description {
#   color: var(--text-secondary);
#   margin-bottom: 1.5rem;
#   flex-grow: 1;
# }
#
# .goal-footer {
#   margin-top: auto;
# }
#
# .progress-container {
#   width: 100%;
#   height: 6px;
#   background-color: var(--border-color);
#   border-radius: 3px;
#   overflow: hidden;
#   margin-bottom: 0.5rem;
# }
#
# .progress-bar {
#   height: 100%;
#   background-color: var(--primary-color);
#   border-radius: 3px;
# }
#
# .progress-text {
#   font-size: 0.85rem;
#   color: var(--text-secondary);
# }
#
# .goal-actions {
#   display: flex;
#   justify-content: flex-end;
#   gap: 0.5rem;
#   margin-top: 0.5rem;
# }
#
# /* Responsive adjustments */
# @media (max-width: 768px) {
#   .task-table {
#     display: block;
#     overflow-x: auto;
#   }
#
#   .goals-container {
#     grid-template-columns: 1fr;
#   }
#
#   .panel-header {
#     flex-direction: column;
#     gap: 1rem;
#     align-items: flex-start;
#   }
#
#   .container {
#     padding: 1rem;
#   }
# }
# ```
#
# These files provide you with a responsive, modern design for your task and goal management panels. The tasks are displayed in a table format with checkboxes for completion status, while goals are displayed as cards with progress bars. Both panels include action buttons for editing and deleting items, as well as an "add new" button.
#
# The design uses a clean blue color scheme with proper spacing and transitions for a professional look. It's fully responsive and will look good on both desktop and mobile devices.
# """
#
# import re
#
#
# def extract_all_code(text):
#     # Pattern to match all code blocks (including those with optional language specifiers)
#     pattern = r'```.*?\n(.*?)```'
#     matches = re.findall(pattern, text, re.DOTALL)
#     return [match.strip() for match in matches]
#
# def extract_non_code_text(text):
#     # This pattern matches code blocks between ``` or ~~~ (common markdown syntax)
#     pattern = r'```.*?```|~~~.*?~~~'
#     # Remove all code blocks
#     non_code_text = re.sub(pattern, '', text, flags=re.DOTALL)
#     return non_code_text.strip()
#
# def extract_file_paths(text):
#     return re.findall(r'File:\s*(.*?)\n', text)
#
#
#
# # print(extract_file_paths(extract_non_code_text(output)))
#
# def rewrite_file(file_path: str, content: str) -> None:
#     """
#     Rewrites the file at the given path with the specified content.
#
#     Args:
#         file_path: Path to the file to be rewritten
#         content: String content to write to the file
#     """
#     try:
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(content)
#         print(f"File at {file_path} has been successfully rewritten.")
#     except IOError as e:
#         print(f"Error rewriting file: {e}")
#
# # rewrite_file("/home/nnikolovskii/index.html", "<html></html>")
#
