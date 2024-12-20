{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "f1e00710-eb8f-4679-a14f-bc2d98683055",
   "metadata": {},
   "source": [
    "# A Guide for Early Adoptors & Contributors"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "43fd27a1-7873-41ac-b66b-125900adbc39",
   "metadata": {},
   "source": [
    "![cloud_project](images/cloud_project_logo.svg) "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0481a017-bc97-49ec-9ee4-be3bcdd429ff",
   "metadata": {},
   "source": [
    "# 1. Introduction"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1024dc2a-4c18-4c76-aa78-f330b81c3dd5",
   "metadata": {},
   "source": [
    "Welcome to our new JupyterHub! We're thrilled to have you as an early adopter and contributor. Your efforts in uploading and sharing your courses will help us build a robust and dynamic educational platform. This notebook is designed to guide you through your questions in running/managing your courses in GeoLab. By following these guidelines, you can ensure that your materials are well-organized, accessible, and easy to navigate for all users.\n",
    "\n",
    "**Expectations:** \n",
    "We expect our early adopters to follow the guidelines outlined in this document to maintain consistency and quality across all courses. In return, you can expect a supportive environment and the necessary resources to succeed.\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0945e0e6-7053-4d5e-b45b-478e99810ef8",
   "metadata": {},
   "source": [
    "# 2. Previous Course Takeaways "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0468ad99-5107-48b6-bbba-e0d19dc71bc7",
   "metadata": {},
   "source": [
    "The July 8-12 Massive Parallel Analysis System for Seismologists (MsPASS) short course was the first to run in our GeoLab JupyterHub environment and was a resounding success. Here are some key takeaways from the course:\n",
    "\n",
    "**Pre-configured Environments:** One of the most significant benefits was the pre-configured environment tailored to the course content. This setup allowed every student to log in and start working immediately without needing to troubleshoot individual setups.\n",
    "\n",
    "**Scalability and Performance:** The GeoLab JupyterHub environment performed well, dynamically scaling resources to handle increased traffic. The environment adjusted the number of available nodes based on student logins, ensuring efficient use of resources.\n",
    "\n",
    "**Technical Smoothness:** There were no major technical issues throughout the course. The system's ability to efficiently scale and manage resources contributed to a seamless experience for instructors and students.\n",
    "\n",
    "**Areas for Improvement:** Despite the overall success, we identified some areas for improvement:\n",
    "\n",
    "- Simplifying the user registration process.\n",
    "- Streamlining access to the short course image in GeoLab.\n",
    "- Enhancing tutorial instructions to reduce potential confusion.\n",
    "- Addressing minor slowdowns during data-intensive workflows.\n",
    "\n",
    "\n",
    "These takeaways will support the success of future courses and have helped shape this blueprint for setting up future short courses. We have refined our processes for collecting information from instructors, deploying software images, and ensuring participants have all the necessary resources.\n",
    "\n",
    "\n",
    "For more information: [MsPass Recap](https://www.earthscope.org/news/a-successful-run-for-the-first-short-course-in-the-geolab-notebook-hub/) \n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2a8f44a8-ed5d-4ea7-a621-2b2858bdee56",
   "metadata": {},
   "source": [
    "# 3. Contributor Checklist for Uploading Courses and Notebooks"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5fb9fb4d-af9c-4185-8b0d-aa5d97ef5db6",
   "metadata": {},
   "source": [
    "## Setting Up Your Workspace\n",
    "\n",
    "### Creating Folders\n",
    "- **Navigate to the File Browser**: On the JupyterHub dashboard, click on the \"File Browser\" tab.\n",
    "- **Create a New Folder**: Click on the \"New\" button and select \"Folder\". Name your folder appropriately (e.g., \"CourseName_2024\").\n",
    "\n",
    "### Naming Conventions\n",
    "- **Folders**: Use clear and descriptive names (e.g., \"Introduction_to_Python\", \"Data_Science_Fall_2024\").\n",
    "- **Files**: Use consistent and descriptive file names (e.g., \"Lesson1_Introduction.ipynb\", \"Assignment1_DataAnalysis.ipynb\").\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a53a6c9f-0123-4907-83a0-f3c62c3e999b",
   "metadata": {},
   "source": [
    "## Uploading Course Material\n",
    "\n",
    "### Uploading Files\n",
    "- **Navigate to the Desired Folder**: Use the file browser to navigate to the folder where you want to upload your files.\n",
    "- **Upload Files**: Click on the \"Upload\" button and select the files from your computer. You can upload multiple files at once.\n",
    "\n",
    "### Organizing Course Material\n",
    "- **Course Outline**: Create a main folder for your course and subfolders for each module or week.\n",
    "- **Subfolders**: Within each module folder, organize files by type (e.g., \"Lectures\", \"Assignments\", \"Readings\").\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "52ebf5b4-88b2-4a2e-a867-794416216946",
   "metadata": {},
   "source": [
    "## Creating and Managing Notebooks\n",
    "\n",
    "### Creating a New Notebook\n",
    "- **Navigate to the Desired Folder**: In the file browser, navigate to the folder where you want to create the notebook.\n",
    "- **Create a Notebook**: Click on the \"New\" button and select \"Python 3\" (or your preferred kernel). A new notebook will open in a new tab.\n",
    "\n",
    "### Notebook Structure and Features\n",
    "- **Cell Types**: Understand the different cell types (Code, Markdown, Raw NBConvert).\n",
    "- **Using Markdown**: Learn to use Markdown for adding headings, lists, links, and formatting text.\n",
    "- **Adding Headings**: Use `#` for headings (e.g., `# Heading 1`, `## Heading 2`).\n",
    "\n",
    "### Saving and Versioning\n",
    "- **Save Regularly**: Click on the \"Save\" icon or use `Ctrl + S` to save your work frequently.\n",
    "- **Naming Your Notebook**: Give your notebook a descriptive name (e.g., \"Lecture1_Introduction_to_Python.ipynb\").\n",
    "- **Version Control**: Use Git to manage versions of your notebooks (covered in a later section).\n",
    "\n",
    "**For more detailed documentation, please visit How_to_Notebook in the /shared drive**"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e04f63a2-8568-4082-a5e9-b9a231957f02",
   "metadata": {},
   "source": [
    " # 4. Best Practices for Course Development\n",
    "\n",
    "### Course Structure\n",
    "- **Outline Clearly**: Start each course with a clear outline that includes the course objectives, prerequisites, and a logical progression of topics.\n",
    "- **Organize Content**: Use subfolders for each module or week to keep content organized. For example:\n",
    "\n",
    "### Engagement Strategies\n",
    "- **Interactive Elements**: To engage students, include quizzes, polls, and discussion prompts within your notebooks.\n",
    "- **Visual Aids**: Incorporate charts, graphs, and images to help explain complex concepts. Use libraries like Matplotlib, Seaborn, or Plotly for data visualization.\n",
    "\n",
    "### Feedback Mechanisms\n",
    "- **Surveys**: Provide opportunities for student feedback through surveys. Platforms like Google Forms or embed simple surveys within the notebooks can be used.\n",
    "- **Discussion Forums**: Create a space for discussion, such as a dedicated Slack channel or a forum on your course platform.\n",
    "\n",
    "### Peer Review Process\n",
    "- **Encourage Peer Review**: Set up a system where contributors can review each other's work. This could be a simple checklist or a more formal review process.\n",
    "- **Constructive Feedback**: Ensure feedback is constructive and aimed at improving the quality of the content.\n",
    "\n",
    "### Self-Assessment Checklists\n",
    "- **Completeness**: Ensure all topics are covered as outlined in the course objectives.\n",
    "- **Accuracy**: Verify that the information is accurate and up-to-date.\n",
    "- **Clarity**: Ensure that explanations are clear and understandable and that visual aids are used effectively.\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c34abf71-ae66-496c-8a7e-bfbba92356c1",
   "metadata": {},
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e52d65ad-37e6-4dff-b5ee-994654029710",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
