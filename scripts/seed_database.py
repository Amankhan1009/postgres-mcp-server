"""
Seeds Neon with realistic fictional data for Orbitals Inc.

Run manually — not part of the MCP server. Safe to rerun only against
an empty database; running twice will hit the unique constraints
(employees.email, departments.name) and fail loudly, which is
intentional — it stops you from silently duplicating data.
"""
import asyncio
from datetime import date, datetime, timedelta

from postgres_mcp.db.engine import get_session
from postgres_mcp.logging_config import configure_logging
from postgres_mcp.models import (
    Client,
    Department,
    Employee,
    Invoice,
    Meeting,
    MeetingAttendee,
    Order,
    Product,
    Project,
    ProjectAssignment,
    SupportTicket,
)


async def seed() -> None:
    configure_logging()
    async with get_session() as session:
        # --- Departments ---
        dept_names = ["Engineering", "Sales", "Support", "Product", "Finance", "HR"]
        departments = {name: Department(name=name) for name in dept_names}
        session.add_all(departments.values())
        await session.flush()

        # --- Employees (pass 1: no manager yet) ---
        employees_data = [
            ("Aarav", "Sharma", "aarav.sharma@orbitals.com", "Engineering Manager", "Engineering", 145000),
            ("Diya", "Patel", "diya.patel@orbitals.com", "Senior Backend Engineer", "Engineering", 118000),
            ("Kabir", "Mehta", "kabir.mehta@orbitals.com", "Backend Engineer", "Engineering", 92000),
            ("Ishita", "Rao", "ishita.rao@orbitals.com", "Frontend Engineer", "Engineering", 89000),
            ("Aditya", "Chawla", "aditya.chawla@orbitals.com", "Backend Engineer", "Engineering", 94000),
            ("Kiara", "Menon", "kiara.menon@orbitals.com", "Frontend Engineer", "Engineering", 87000),
            ("Rohan", "Bose", "rohan.bose@orbitals.com", "DevOps Engineer", "Engineering", 105000),
            ("Sanya", "Khanna", "sanya.khanna@orbitals.com", "QA Engineer", "Engineering", 79000),
            ("Vihaan", "Nair", "vihaan.nair@orbitals.com", "Sales Director", "Sales", 138000),
            ("Ananya", "Iyer", "ananya.iyer@orbitals.com", "Account Executive", "Sales", 78000),
            ("Yash", "Trivedi", "yash.trivedi@orbitals.com", "Account Executive", "Sales", 76000),
            ("Pooja", "Reddy", "pooja.reddy@orbitals.com", "Sales Development Rep", "Sales", 58000),
            ("Reyansh", "Gupta", "reyansh.gupta@orbitals.com", "Support Lead", "Support", 84000),
            ("Saanvi", "Joshi", "saanvi.joshi@orbitals.com", "Support Engineer", "Support", 62000),
            ("Devansh", "Pillai", "devansh.pillai@orbitals.com", "Support Engineer", "Support", 60000),
            ("Riya", "Chatterjee", "riya.chatterjee@orbitals.com", "Support Engineer", "Support", 61000),
            ("Arjun", "Verma", "arjun.verma@orbitals.com", "Product Manager", "Product", 112000),
            ("Naina", "Bhalla", "naina.bhalla@orbitals.com", "Product Designer", "Product", 91000),
            ("Krishna", "Rathore", "krishna.rathore@orbitals.com", "Product Analyst", "Product", 82000),
            ("Myra", "Kapoor", "myra.kapoor@orbitals.com", "Finance Manager", "Finance", 120000),
            ("Ayaan", "Sinha", "ayaan.sinha@orbitals.com", "Finance Analyst", "Finance", 76000),
            ("Zara", "D'Souza", "zara.dsouza@orbitals.com", "Accountant", "Finance", 68000),
            ("Advait", "Kulkarni", "advait.kulkarni@orbitals.com", "HR Manager", "HR", 98000),
            ("Tara", "Ahluwalia", "tara.ahluwalia@orbitals.com", "HR Generalist", "HR", 65000),
            ("Veer", "Malhotra", "veer.malhotra@orbitals.com", "Recruiter", "HR", 63000),
        ]
        employees = {}
        for first, last, email, title, dept, salary in employees_data:
            emp = Employee(
                first_name=first,
                last_name=last,
                email=email,
                job_title=title,
                hire_date=date(2021, 1, 1) + timedelta(days=len(employees) * 33),
                salary=salary,
                department_id=departments[dept].id,
            )
            employees[email] = emp
            session.add(emp)
        await session.flush()

        # --- Employees (pass 2: assign managers) ---
        manager_map = {
            "diya.patel@orbitals.com": "aarav.sharma@orbitals.com",
            "kabir.mehta@orbitals.com": "aarav.sharma@orbitals.com",
            "ishita.rao@orbitals.com": "aarav.sharma@orbitals.com",
            "aditya.chawla@orbitals.com": "aarav.sharma@orbitals.com",
            "kiara.menon@orbitals.com": "aarav.sharma@orbitals.com",
            "rohan.bose@orbitals.com": "aarav.sharma@orbitals.com",
            "sanya.khanna@orbitals.com": "aarav.sharma@orbitals.com",
            "ananya.iyer@orbitals.com": "vihaan.nair@orbitals.com",
            "yash.trivedi@orbitals.com": "vihaan.nair@orbitals.com",
            "pooja.reddy@orbitals.com": "vihaan.nair@orbitals.com",
            "saanvi.joshi@orbitals.com": "reyansh.gupta@orbitals.com",
            "devansh.pillai@orbitals.com": "reyansh.gupta@orbitals.com",
            "riya.chatterjee@orbitals.com": "reyansh.gupta@orbitals.com",
            "naina.bhalla@orbitals.com": "arjun.verma@orbitals.com",
            "krishna.rathore@orbitals.com": "arjun.verma@orbitals.com",
            "ayaan.sinha@orbitals.com": "myra.kapoor@orbitals.com",
            "zara.dsouza@orbitals.com": "myra.kapoor@orbitals.com",
            "tara.ahluwalia@orbitals.com": "advait.kulkarni@orbitals.com",
            "veer.malhotra@orbitals.com": "advait.kulkarni@orbitals.com",
        }
        for report_email, manager_email in manager_map.items():
            employees[report_email].manager_id = employees[manager_email].id
        await session.flush()

        # --- Clients ---
        clients_data = [
            ("Northwind Retail", "Priya Desai", "priya@northwindretail.com", "Retail"),
            ("Bluepeak Logistics", "Karan Malhotra", "karan@bluepeak.com", "Logistics"),
            ("Fenwick Health", "Neha Bhatt", "neha@fenwickhealth.com", "Healthcare"),
            ("Solstice Media", "Rohan Kulkarni", "rohan@solsticemedia.com", "Media"),
            ("Crestline Manufacturing", "Aman Bajaj", "aman@crestline.com", "Manufacturing"),
            ("Harborview Insurance", "Simran Kaur", "simran@harborview.com", "Insurance"),
            ("Palisade Realty", "Nikhil Anand", "nikhil@palisade.com", "Real Estate"),
            ("Meridian EdTech", "Kavya Suresh", "kavya@meridianedu.com", "Education"),
            ("Vantage Freight", "Farhan Ali", "farhan@vantagefreight.com", "Logistics"),
            ("Coral Bay Hospitality", "Leela Menon", "leela@coralbay.com", "Hospitality"),
            ("Ironclad Security", "Dev Oberoi", "dev@ironclad.com", "Security"),
            ("Brightline Energy", "Meera Iyengar", "meera@brightline.com", "Energy"),
        ]
        clients = {}
        for name, contact, email, industry in clients_data:
            c = Client(company_name=name, contact_name=contact, contact_email=email, industry=industry)
            clients[name] = c
            session.add(c)
        await session.flush()

        # --- Projects ---
        projects_data = [
            ("Northwind Retail", "Inventory Platform Revamp", "active", 180000, date(2025, 3, 1), None),
            ("Bluepeak Logistics", "Fleet Tracking Dashboard", "completed", 95000, date(2024, 11, 1), date(2025, 4, 1)),
            ("Fenwick Health", "Patient Portal V2", "active", 220000, date(2025, 4, 1), None),
            ("Solstice Media", "Ad Analytics Pipeline", "planned", 60000, date(2025, 9, 1), None),
            ("Crestline Manufacturing", "Supply Chain Optimizer", "on_hold", 150000, date(2025, 1, 15), None),
            ("Harborview Insurance", "Claims Automation Engine", "completed", 175000, date(2024, 8, 1), date(2025, 2, 1)),
            ("Palisade Realty", "Listing Search Revamp", "active", 88000, date(2025, 5, 1), None),
            ("Meridian EdTech", "Course Recommendation Engine", "active", 132000, date(2025, 2, 1), None),
            ("Vantage Freight", "Route Optimization Service", "cancelled", 70000, date(2024, 10, 1), None),
            ("Coral Bay Hospitality", "Booking Engine Redesign", "planned", 98000, date(2025, 10, 1), None),
        ]
        projects = {}
        for client_name, title, status, budget, start, end in projects_data:
            p = Project(
                name=title, status=status, start_date=start, end_date=end,
                budget=budget, client_id=clients[client_name].id,
            )
            projects[title] = p
            session.add(p)
        await session.flush()

        # --- Project Assignments ---
        assignments = [
            ("Inventory Platform Revamp", "diya.patel@orbitals.com", "Tech Lead"),
            ("Inventory Platform Revamp", "kabir.mehta@orbitals.com", "Backend Developer"),
            ("Inventory Platform Revamp", "sanya.khanna@orbitals.com", "QA Engineer"),
            ("Fleet Tracking Dashboard", "ishita.rao@orbitals.com", "Frontend Developer"),
            ("Fleet Tracking Dashboard", "rohan.bose@orbitals.com", "DevOps Engineer"),
            ("Patient Portal V2", "kabir.mehta@orbitals.com", "Backend Developer"),
            ("Patient Portal V2", "arjun.verma@orbitals.com", "Product Manager"),
            ("Patient Portal V2", "naina.bhalla@orbitals.com", "Product Designer"),
            ("Supply Chain Optimizer", "aditya.chawla@orbitals.com", "Backend Developer"),
            ("Claims Automation Engine", "diya.patel@orbitals.com", "Tech Lead"),
            ("Claims Automation Engine", "kiara.menon@orbitals.com", "Frontend Developer"),
            ("Listing Search Revamp", "aditya.chawla@orbitals.com", "Backend Developer"),
            ("Listing Search Revamp", "kiara.menon@orbitals.com", "Frontend Developer"),
            ("Course Recommendation Engine", "krishna.rathore@orbitals.com", "Product Analyst"),
            ("Course Recommendation Engine", "kabir.mehta@orbitals.com", "Backend Developer"),
            ("Booking Engine Redesign", "naina.bhalla@orbitals.com", "Product Designer"),
        ]
        for project_title, email, role in assignments:
            session.add(ProjectAssignment(
                project_id=projects[project_title].id, employee_id=employees[email].id, role=role,
            ))

        # --- Products ---
        products_data = [
            ("Orbitals CRM Lite", "Lightweight CRM for small teams", 4900),
            ("Orbitals Analytics Suite", "Business intelligence dashboarding", 12000),
            ("Orbitals Support Desk", "Ticketing and helpdesk platform", 7500),
            ("Orbitals Billing Engine", "Automated invoicing and billing", 9800),
            ("Orbitals Data Connector", "Prebuilt integrations and ETL pipelines", 6200),
            ("Orbitals Insights AI", "AI-powered reporting add-on", 15000),
        ]
        products = {}
        for name, desc, price in products_data:
            prod = Product(name=name, description=desc, price=price)
            products[name] = prod
            session.add(prod)
        await session.flush()

        # --- Orders ---
        orders_data = [
            ("Northwind Retail", "Orbitals CRM Lite", 3, 14700, "completed"),
            ("Bluepeak Logistics", "Orbitals Analytics Suite", 1, 12000, "completed"),
            ("Solstice Media", "Orbitals Support Desk", 2, 15000, "pending"),
            ("Crestline Manufacturing", "Orbitals Data Connector", 2, 12400, "completed"),
            ("Harborview Insurance", "Orbitals Billing Engine", 1, 9800, "completed"),
            ("Palisade Realty", "Orbitals CRM Lite", 4, 19600, "completed"),
            ("Meridian EdTech", "Orbitals Insights AI", 1, 15000, "pending"),
            ("Vantage Freight", "Orbitals Analytics Suite", 1, 12000, "cancelled"),
            ("Coral Bay Hospitality", "Orbitals Support Desk", 3, 22500, "pending"),
            ("Ironclad Security", "Orbitals Data Connector", 2, 12400, "completed"),
            ("Brightline Energy", "Orbitals Billing Engine", 2, 19600, "completed"),
            ("Fenwick Health", "Orbitals Insights AI", 1, 15000, "completed"),
        ]
        orders = {}
        for client_name, product_name, qty, total, status in orders_data:
            o = Order(
                quantity=qty, total_amount=total, status=status,
                client_id=clients[client_name].id, product_id=products[product_name].id,
            )
            orders[client_name] = o
            session.add(o)
        await session.flush()

        # --- Invoices ---
        invoices_data = [
            ("Northwind Retail", 14700, "paid", date(2025, 5, 1), date(2025, 5, 31), "order"),
            ("Bluepeak Logistics", 12000, "paid", date(2025, 4, 10), date(2025, 5, 10), "order"),
            ("Fenwick Health", 90000, "unpaid", date(2025, 7, 1), date(2025, 7, 31), "project"),
            ("Crestline Manufacturing", 12400, "paid", date(2025, 3, 5), date(2025, 4, 5), "order"),
            ("Harborview Insurance", 175000, "paid", date(2025, 1, 20), date(2025, 2, 20), "project"),
            ("Palisade Realty", 19600, "overdue", date(2025, 5, 15), date(2025, 6, 15), "order"),
            ("Meridian EdTech", 66000, "unpaid", date(2025, 7, 10), date(2025, 8, 10), "project"),
            ("Coral Bay Hospitality", 22500, "unpaid", date(2025, 7, 20), date(2025, 8, 20), "order"),
            ("Ironclad Security", 12400, "paid", date(2025, 6, 1), date(2025, 7, 1), "order"),
            ("Brightline Energy", 19600, "overdue", date(2025, 5, 25), date(2025, 6, 25), "order"),
            ("Northwind Retail", 90000, "paid", date(2025, 3, 1), date(2025, 3, 31), "project"),
            ("Fenwick Health", 15000, "paid", date(2025, 6, 15), date(2025, 7, 15), "order"),
        ]
        for client_name, amount, status, issued, due, source in invoices_data:
            kwargs = dict(
                amount=amount, status=status, issued_date=issued, due_date=due,
                client_id=clients[client_name].id,
            )
            if source == "order" and client_name in orders:
                kwargs["order_id"] = orders[client_name].id
            elif source == "project":
                matching = [p for p in projects.values() if p.client_id == clients[client_name].id]
                if matching:
                    kwargs["project_id"] = matching[0].id
                else:
                    kwargs["order_id"] = orders[client_name].id
            session.add(Invoice(**kwargs))

        # --- Support Tickets ---
        tickets_data = [
            ("Northwind Retail", "Login fails intermittently", "Users report random 401s.", "open", "high", "saanvi.joshi@orbitals.com"),
            ("Bluepeak Logistics", "Dashboard export button missing", "Export CSV button not visible on Safari.", "resolved", "low", "reyansh.gupta@orbitals.com"),
            ("Fenwick Health", "Data sync delay", "Patient records syncing 20+ minutes late.", "in_progress", "urgent", "saanvi.joshi@orbitals.com"),
            ("Crestline Manufacturing", "Report generation timeout", "Monthly report fails to generate for large datasets.", "open", "medium", "devansh.pillai@orbitals.com"),
            ("Harborview Insurance", "Incorrect claim status displayed", "UI shows 'pending' after approval.", "closed", "medium", "riya.chatterjee@orbitals.com"),
            ("Palisade Realty", "Search filters not saving", "User preferences reset on page reload.", "open", "low", "devansh.pillai@orbitals.com"),
            ("Meridian EdTech", "API rate limit errors", "Integration hitting 429s during peak hours.", "in_progress", "high", "saanvi.joshi@orbitals.com"),
            ("Coral Bay Hospitality", "Booking confirmation emails delayed", "Emails arriving 1+ hour late.", "open", "urgent", "riya.chatterjee@orbitals.com"),
            ("Ironclad Security", "SSO login broken for subset of users", "Okta integration failing for 2 test accounts.", "resolved", "high", "reyansh.gupta@orbitals.com"),
            ("Brightline Energy", "Billing engine mismatched totals", "Invoice totals don't match line items.", "in_progress", "urgent", "devansh.pillai@orbitals.com"),
        ]
        for client_name, subject, desc, status, priority, assignee in tickets_data:
            resolved_at = datetime(2025, 6, 15, 10, 30) if status in ("resolved", "closed") else None
            session.add(SupportTicket(
                subject=subject, description=desc, status=status, priority=priority,
                client_id=clients[client_name].id, assigned_employee_id=employees[assignee].id,
                resolved_at=resolved_at,
            ))

        # --- Meetings ---
        meetings_data = [
            ("Inventory Platform Kickoff", datetime(2025, 3, 3, 10, 0), 60, "Northwind Retail",
             ["diya.patel@orbitals.com", "arjun.verma@orbitals.com"]),
            ("Internal Eng Sync", datetime(2025, 7, 20, 9, 0), 30, None,
             ["aarav.sharma@orbitals.com", "diya.patel@orbitals.com", "kabir.mehta@orbitals.com"]),
            ("Patient Portal Design Review", datetime(2025, 5, 12, 14, 0), 45, "Fenwick Health",
             ["naina.bhalla@orbitals.com", "arjun.verma@orbitals.com", "kabir.mehta@orbitals.com"]),
            ("Q3 Sales Pipeline Review", datetime(2025, 7, 5, 11, 0), 60, None,
             ["vihaan.nair@orbitals.com", "ananya.iyer@orbitals.com", "yash.trivedi@orbitals.com"]),
            ("Claims Engine Retro", datetime(2025, 2, 3, 15, 0), 45, "Harborview Insurance",
             ["diya.patel@orbitals.com", "kiara.menon@orbitals.com"]),
            ("HR Onboarding Sync", datetime(2025, 6, 1, 9, 30), 30, None,
             ["advait.kulkarni@orbitals.com", "tara.ahluwalia@orbitals.com", "veer.malhotra@orbitals.com"]),
        ]
        for title, scheduled_at, duration, client_name, attendee_emails in meetings_data:
            m = Meeting(
                title=title, scheduled_at=scheduled_at, duration_minutes=duration,
                client_id=clients[client_name].id if client_name else None,
            )
            session.add(m)
            await session.flush()
            for email in attendee_emails:
                session.add(MeetingAttendee(meeting_id=m.id, employee_id=employees[email].id))

    print("✅ Database seeded successfully with expanded data.")


if __name__ == "__main__":
    asyncio.run(seed())