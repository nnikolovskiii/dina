import asyncio
from typing import List, Optional

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline
from app.task_manager.models.company_info import CompanyModel
from app.task_manager.models.task import Task


class InitCompany(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            user_text: str,
            company_model: CompanyModel
    ):
        return f"""Given the below text from the user your job is to fill in as much as the attributes for the company object. Also you can change, update and delete some of the existing attribute values.
        
User text: 
{user_text}        

The company object looks like this:
{str(company_model)}
    
Return the values in json format with key "company_model"
"""


async def init_company(
        user_text: str,
        company_model: Optional[CompanyModel] = None
):
    mdb = container.mdb()
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="deepseek-chat", class_type=ChatLLM)
    pipeline = InitCompany(chat_model)

    response = await pipeline.execute(
        user_text=user_text,
        company_model=company_model if company_model else CompanyModel()
    )

    print(response)

asyncio.run(init_company("""Remora: AI-Powered Automation for Enterprise Workflows

Technical Overview
1. Introduction

Remora is an AI-driven automation platform designed to optimize business processes through intelligent workflow management, real-time data retrieval, and task automation. Its core functionality revolves around an advanced chatbot interface that serves as a unified gateway for both customers and employees to interact with organizational systems.

Built with enterprise scalability in mind, Remora integrates AI-powered decision-making, automated task execution, and deep analytical capabilities to enhance operational efficiency. Additionally, it provides robust technical support for software development, including terminal access, collaborative coding, and IT alert management.
2. Core Features & Capabilities
2.1 Intelligent Chatbot Interface

    Unified Information Access: Retrieves and synthesizes data from internal systems (databases, APIs, CRMs).

    Automated Document Handling: Generates PDFs, schedules appointments, processes payments, and filters insights on demand.

    Smart Task Delegation: Assigns and prioritizes tasks based on organizational objectives.

    Real-Time Monitoring: Tracks employee activity and generates progress reports.

2.2 Business Process Automation

    Workflow Optimization: Analyzes and automates repetitive processes to reduce manual intervention.

    Strategic Decision Support: Provides financial analysis, goal alignment, and performance insights.

    Expert Consultations: AI-driven advisory for business strategy, risk assessment, and operational improvements.

2.3 Technical & Development Support

    Integrated Terminal Access: Allows direct command-line interaction for debugging and system management.

    Collaborative Coding Environment: Facilitates real-time code sharing and version control for development teams.

    Automated IT Support:

        Monitors system alerts and performs initial triage.

        Generates incident reports and suggests remediation steps.

    AI-Assisted Programming:

        Code generation (boilerplate, functions, scripts).

        Debugging assistance with contextual error analysis.

        Documentation auto-generation.

3. System Architecture

Remora is built on a modular microservices architecture, ensuring scalability and flexibility across different enterprise environments.
3.1 Key Components
Component	Function
AI Orchestrator	Central decision-making engine that processes NLP queries and triggers workflows.
Data Integration Layer	Connects to databases, APIs, and third-party services for real-time data retrieval.
Task Automation Engine	Executes predefined workflows (document generation, scheduling, payments).
Developer Toolkit	Provides terminal emulation, code analysis, and alert management for IT/DevOps.
Analytics & Reporting	Generates insights on workflow efficiency, employee performance, and business KPIs.
3.2 Deployment Options

    Cloud-Based (SaaS): Fully hosted solution with multi-tenant support.

    On-Premises/Hybrid: Self-hosted deployment for enterprises with strict compliance requirements.

4. Security & Compliance

    Data Encryption: End-to-end encryption (TLS 1.3+) for all communications.

    Access Control: Role-based permissions (RBAC) and multi-factor authentication (MFA).

    Audit Logging: Immutable logs for all interactions and automated actions.

    GDPR & SOC 2 Compliance: Enterprise-grade data protection and privacy controls.

5. Use Cases
5.1 Enterprise Automation

    HR onboarding/offboarding workflows.

    Automated customer support ticket resolution.

    Real-time financial reporting and forecasting.

5.2 Software Development & IT Ops

    AI-assisted debugging and code optimization.

    Automated incident response for DevOps teams.

    Terminal-based scripting and server management.

6. Conclusion

Remora is a next-generation AI automation platform that bridges the gap between business process management and technical execution. By combining intelligent workflow automation with advanced programming support, it enables organizations to streamline operations, enhance productivity, and drive data-driven decision-making.

For integration guides, API documentation, and deployment specifics, refer to the Remora Developer Hub (available upon request)."""))
